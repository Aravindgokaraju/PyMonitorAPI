# execution/scraping/standalone_scraper.py
import re
import sys
import time
import random
import traceback
from typing import Any, Dict, List, Tuple, Optional
from decimal import Decimal

# Import your existing classes (they should be database-agnostic)
from .interaction_service import InteractionService
from .interruption_handler import InterruptionHandler
from .scraping_models import Criteria
from .commandstack import CommandStack

class StandaloneScrapingService:
    """
    Database-agnostic scraping service for worker environment
    Returns pure data without any database operations
    """
    
    def __init__(self, stealth_level='stable'):
        self.interaction_service = InteractionService(stealth_level=stealth_level)
        self.interruption_handler = InterruptionHandler(self.interaction_service)
        self.function_map = self.interaction_service._initialize_function_map()
        self.command_stack = CommandStack()
        self.criteria_dict: Dict[str, Criteria] = {}
        self.parent_pair: Dict[str, str] = {}
        self.start_index = 0
        self.website = ""
        
    def scrape_websites(self, request_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Main method to execute the scraping process - returns pure data"""
        try:
            skus = self._get_sku_data(request_data)
            flows = self._get_flow_data(request_data)
            
            results = []
            
            for flow in flows:
                self.criteria_dict = self.steps_to_criteria_dict(flow["steps"])
                flow_results = self._process_website(flow, skus)
                results.extend(flow_results)
            return results
            
        except Exception as e:
            _, _, exc_traceback = sys.exc_info()
            line_number = exc_traceback.tb_lineno
            error_msg = f"Scraping failed at line {line_number}: {str(e)}"
            traceback.print_exc()
            raise ValueError(error_msg) from e
        finally:
            self.interaction_service.quit()

    def _get_sku_data(self, request_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract SKU data from request"""
        skus = request_data.get('skus', [])
        if not isinstance(skus, list):
            raise ValueError("'skus' must be an array")
        return skus

    def _get_flow_data(self, request_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract flow data from request"""
        flows = request_data.get('flows', [])
        if not isinstance(flows, list):
            raise ValueError("'flows' must be an array")
        return flows

    def _process_website(self, website_data: Dict[str, Any], skus: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process a single website with all SKUs - returns list of results"""
        self.command_stack.clear()
        self.criteria_dict = self.steps_to_criteria_dict(website_data["steps"])
        self.start_index = 0
        self.interruption_handler.load_interruptions(website_data["interruptions"])
        self.interaction_service._open_website(website_data["url"])
        self.website = website_data["url"]
        
        results = []
        
        for full_sku in skus:
            if not full_sku:
                continue
                
            sku = full_sku["sku_number"]
            try:
                sku_results = self._process_sku(website_data, sku)
                results.extend(sku_results)
            except Exception as e:
                print(f"Skipping SKU {sku}, error occurred: {str(e)}")
                # Optionally log the error but continue with other SKUs
        
        return results

    def _process_sku(self, website_data: Dict[str, Any], sku: str) -> List[Dict[str, Any]]:
        """Process a single SKU - returns list of price results"""
        print(f"Processing SKU: {sku} for website: {website_data['url']}")
        
        # Initialize with the starting step
        initial_step = next(
            step for step in website_data["steps"]
            if step.get("start_trigger", False)
        )
        
        initial_criteria = self.criteria_dict[initial_step["xpath"]].copyOf()
        self.command_stack.push(initial_criteria)
        
        results = []
        
        try:
            while not self.command_stack.is_empty():
                criterion = self.command_stack.peek()
                
                # Find the web element
                web_element = self.interaction_service.smart_find(self.criteria_dict, criterion.xpath, criterion.parent)
                if not web_element:
                    print(f"Element not found: {criterion.xpath}")
                    self.command_stack.pop()
                    continue
                    
                criterion.webElement = web_element
                
                # Process all actions for this criterion
                while criterion.actionCount < len(criterion.actions):
                    action = criterion.actions[criterion.actionCount]
                    
                    # Special handling for add_next
                    if action == "add_next":
                        self._handle_add_next_action(criterion)
                        if self.command_stack.peek() != criterion:
                            break
                        continue
                    
                    # Execute action and collect results
                    action_result = self._execute_action(criterion, action, sku)
                    if action_result and action == "add_to_table":
                        results.append(action_result)
                    
                    criterion.actionCount += 1
                    
                    if not self.command_stack.is_empty() and self.command_stack.peek() != criterion:
                        break
                
                # Check if we completed all actions
                if (not self.command_stack.is_empty() and 
                    self.command_stack.peek() == criterion and 
                    criterion.actionCount >= len(criterion.actions)):
                    self.command_stack.pop()

        except Exception as e:
            print(f"ERROR processing SKU {sku}: {str(e)}")
            traceback.print_exc()
            self.command_stack.clear()
        
        return results

    def _execute_action(self, criterion, action, sku) -> Optional[Dict[str, Any]]:
        """Execute an action and return any results"""
        max_retries = 1
        attempt = 0
        
        while attempt <= max_retries:
            try:
                self.interruption_handler.handle("before_step", criterion)
                
                command = self._parse_action(action)
                result = None
                
                if action == "enter_string":
                    command(criterion, sku)
                elif action == "add_to_table":
                    price = command(criterion)
                    result = {
                        'website': self.website,
                        'sku': sku,
                        'price': price,
                        'timestamp': time.time()
                    }
                elif action == "clear_stack":
                    break
                else:
                    command(criterion)
                
                self.interruption_handler.handle("after_step", criterion)
                return result
                
            except Exception as e:
                attempt += 1
                if attempt > max_retries:
                    print(f"Failed after {max_retries + 1} attempts")
                    raise
                print(f"Retrying after error: {str(e)}")
                self._recovery_sequence(criterion, e, action)
        
        return None

    def _recovery_sequence(self, criterion, error, failed_action):
        """Centralized recovery for all failure modes"""
        # 1. Handle error-specific interruptions
        self.interruption_handler.handle("on_error", criterion, error)
        
        # 2. Refresh context
        criterion.webElement = None
        self._refresh_element(criterion)
        
        # # 3. Action-specific reset
        # if failed_action == "enter_string":
        #     self._clear_input_field(criterion.xpath)
    
    def _refresh_element(self, criterion):
        """
        Completely refreshes the element reference and validates its state
        Returns: The refreshed WebElement
        Raises: Exception if element cannot be recovered
        """
        # 1. Clear existing reference
        criterion.webElement = None
        
        # 2. Find fresh element reference
        try:
            element = self.interaction_service.smart_find(
                self.criteria_dict,
                criterion.xpath,
                criterion.parent,
                #TODO: get this done must make find find the right child: xpath_id=getattr(criterion, 'xpath_id', 0)  # Handle indexed elements
            )
        except Exception as e:
            raise Exception(f"Element refresh failed for {criterion.xpath}: {str(e)}")

        # 3. Validate element state
        # if not element.is_displayed():
        #     print("recovery scroll")
        #     self.interaction_service._scroll_into_view(criterion)
        if not element.is_enabled():
            raise Exception(f"Element {criterion.xpath} exists but is disabled")

        # 4. Update criterion reference
        criterion.webElement = element
        return element
    

    def _parse_action(self, action: str):
        """Parse an action string and return the appropriate function"""
        print("ParseAction:", action)
        
        if action in self.function_map:
            return self.function_map[action]
        # elif "add_next" in action:
        #     return self.add_next_crit
        elif action == "remove_self":
            return self.remove_self
        elif action == "clear_stack":
            print("Trynna clear shii")
            return self.command_stack.clear()  # Add this line
        else:
            return lambda *args, **kwargs: print("Unrecognized command; no action taken.")
        # ... (include all your helper methods like add_nth_child, add_crit_shallow, etc.)
        # Just convert them to class methods and adjust the self references


    def execute_next_actions(self, criterion):
        """Execute all transition actions between parent and child criteria"""
        for action_label in criterion.next_actions:
            print(f"Executing transition action: {action_label}")
            if action_label == "smart_find":
                # Special handling for smart_find since it needs the locator
                self.interaction_service.smart_find(self.criteria_dict, criterion.child,criterion.xpath)
            else:
                next_command = self._parse_action(action_label)
                next_command(criterion)

    def _handle_add_next_action(self, criterion: Criteria):
        """Handle the add_next action with proper drill-and-return behavior"""
        # Initialize child count if first time
        if not criterion.child:
            raise ValueError(f"No child XPath defined for {criterion.xpath}")
        if criterion.childCount == -1:
            elements = self.interaction_service.smart_find_elements(criterion.child)
            criterion.childCount = len(elements) if elements else 0
            print(f"Found {criterion.childCount} child elements")
        
        if criterion.childCount > 0:
            # Execute any transition actions if they exist
            if hasattr(criterion, 'next_actions') and criterion.next_actions:
                print("Executing transition actions:")
                self.execute_next_actions(criterion)
            
            # Create and push child criteria
            new_child = self.criteria_dict[criterion.child].copyWith(
                parent=criterion.xpath,
                xpath_id=criterion.childCount - 1  # Using 0-based index
            )
            self.command_stack.push(new_child)
            print("Pushing command: add next")
            print("Size of stack: ",self.command_stack.size())


            criterion.childCount -= 1
            print(f"Pushed child {new_child.xpath}, remaining: {criterion.childCount}")
        else:
            print("No more children to process")
        
        # Always increment action count unless we're waiting for children
        criterion.actionCount += 1

    # Keep all your existing helper methods but remove database operations:
    # _handle_add_next_action, _recovery_sequence, _refresh_element, 
    # _parse_action, execute_next_actions, etc.
    
    # Remove _save_to_database method entirely
    
    @staticmethod
    def steps_to_criteria_dict(steps: List[dict]) -> Dict[str, 'Criteria']:
        """Same as your existing method - database agnostic"""
        criteria_dict = {}
        relationship_map = {}
        
        for step in steps:
            criteria = Criteria(step)
            criteria_dict[step['xpath']] = criteria
            
            if 'next' in step:
                child_xpath = step['next']['xpath']
                relationship_map[child_xpath] = step['xpath']
        
        for child_xpath, parent_xpath in relationship_map.items():
            if child_xpath in criteria_dict:
                criteria_dict[child_xpath].parent = parent_xpath
        
        return criteria_dict