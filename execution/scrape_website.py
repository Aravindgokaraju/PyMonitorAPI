from datetime import datetime
import json
import os
import re

import traceback
from typing import Any, Dict, List, Tuple, Optional

from execution.interruption_handler import InterruptionHandler

# from execution.mongo_service import MongoService
from .interaction_service import InteractionService
from .scraping_models import Criteria, Website
from .commandstack import CommandStack

# from execution.scrape import ScrapingService
# scraper = ScrapingService()
# scraper.scrape_websites()
class ScrapingService:
    def __init__(self):
        self.interaction_service = InteractionService()
        self.interruption_handler = InterruptionHandler()
        self.function_map = self.interaction_service._initialize_function_map()

        # self.mongo_service = MongoService()
        self.command_stack = CommandStack()
        self.criteria_dict: Dict[str, Criteria] = {} #TODO: legacy variable, delete later
        self.parent_pair: Dict[str,str] = {}
        self.start_index = 0
        self.cachedWebsites=""
        
        # Initialize function map


    def scrape_websites(self) -> List[Tuple[str, str, str]]:
        """Main method to execute the scraping process"""
        try:
            # Get data from Google Sheets
            skus = self._get_sku_data()
            websites = self._get_websites_data()
            
            table_data = []
            
            for website in websites:
                self._process_website(website, skus, table_data)
            
            return table_data
            

        except Exception as e:
            traceback.print_exc()
            raise Exception(f"Scraping failed: {e}")
        finally:
            self.interaction_service.quit()

    def _get_sku_data(self) -> List[Dict[str, Any]]:
        """Get SKU data - temporarily using test data"""
        return [
            {"sku_id": "HM9604-400", "name": "Test Product 1", "id": "1"},
            {"sku_id": "HJ7654-400", "name": "Test Product 2", "id": "2"}
        ]
        
        # Original implementation:
        # skus = SKU.objects.all().values_list('sku_number', 'name', 'id')
        # return [list(sku) for sku in skus]

    def _get_websites_data(self) -> List[Dict[str, Any]]:
        """Get website data - temporarily using test data"""
        # TODO: Replace this with actual MongoDB call when ready
        return self._get_test_website_data()
        
        # Original implementation:
        # website_data = self.mongo_service._get_websites_data()
        # return website_data
    
    def _get_test_website_data(self) -> List[Dict[str, Any]]:
        """Read test website data from JSON file in the same directory"""
        # Get the directory of the current script
        current_dir = os.path.dirname(os.path.abspath(__file__))
        test_file = os.path.join(current_dir, 'test_data')
        
        try:
            with open(test_file, 'r', encoding='utf-8') as f:
                test_data = json.load(f)
                
            # Convert the steps into criteria dictionary format
            self.criteria_dict = self.steps_to_criteria_dict(test_data["steps"])
            
            # Return the test data in the expected format
            return [{
                "id": test_data["_id"],
                "name": test_data["name"],
                "steps": test_data["steps"],
                "url": test_data["url"],
                "criteriaList": list(self.criteria_dict.values())  # For legacy compatibility
            }]
        except FileNotFoundError:
            raise Exception(f"Test data file not found at: {test_file}")
        except json.JSONDecodeError:
            raise Exception(f"Invalid JSON format in test data file: {test_file}")
        except KeyError as e:
            raise Exception(f"Missing required field in test data: {e}")


    def _process_website(self, website_data:Dict[str, Any], skus: List[List[str]], table_data: List):
        """Process a single website with all SKUs"""
        self.command_stack.clear()
        # self.criteria_dict = self._criteria_to_dict(website.criteriaList) set this directly to the db object in sample_data
        self.start_index = 0
        self.interruption_handler.load_interruptions(website_data.get("interruptions", []))
        self.interaction_service._open_website(website_data["id"])
        
        for full_sku in skus:
            if not full_sku:
                continue
                
            sku = full_sku["sku_id"]
            try:
                self._process_sku(website_data, sku, table_data)
            except:
                print("Skipping sku, error occured")

    def _process_sku(self, website_data: Dict[str, Any], sku: str, table_data: List):
        """Process a single SKU for a website with improved drill-and-return handling"""
        print(f"Processing SKU: {sku} for website: {website_data['url']}")
        
        # Initialize with the starting step
        initial_step = next(
            step for step in website_data["steps"] 
            if step.get("start_trigger", False)
        )
        initial_criteria = self.criteria_dict[initial_step["xpath"]].copyWith()
        print("Pushing command: processing")
        self.command_stack.push(initial_criteria)
        print("Size of stack: ",self.command_stack.size())
        
        print(f"Initial criteria: {initial_criteria.xpath}")
        print(f"Stack state: {[c.xpath for c in self.command_stack.stack]}")

        try:
            while not self.command_stack.is_empty():
                criterion = self.command_stack.peek()
                print(f"\nProcessing criterion: {criterion.xpath}")
                print(f"Action progress: {criterion.actionCount}/{len(criterion.actions)}")
                
                # Find the web element
                web_element = self.interaction_service.smart_find(self.criteria_dict, criterion.xpath)
                if not web_element:
                    print(f"Element not found: {criterion.xpath}")
                    self.command_stack.pop()
                    print("POPPING STACK")
                    print("Size of stack: ",self.command_stack.size())
                    continue
                    
                criterion.webElement = web_element
                
                # Process all actions for this criterion
                while criterion.actionCount < len(criterion.actions):
                    action = criterion.actions[criterion.actionCount]
                    print(f"Executing action: {action}")
                    
                    # Special handling for add_next to maintain drill-and-return
                    if action == "add_next":
                        self._handle_add_next_action(criterion)
                        if self.command_stack.peek() != criterion:
                            break  # New item was pushed, process it first
                        continue
                    
                    # Execute regular action
                    self._execute_action(criterion, action, sku, table_data)
                    criterion.actionCount += 1
                    
                    # Check if stack changed during execution
                    if not self.command_stack.is_empty() and self.command_stack.peek() != criterion:
                        break
                
                # Check if we completed all actions for this criterion
                if (not self.command_stack.is_empty() and 
                    self.command_stack.peek() == criterion and 
                    criterion.actionCount >= len(criterion.actions)):
                    print(f"Completed all actions for: {criterion.xpath}")
                    self.command_stack.pop()
                    print("POPPING STACK")
                    print("Size of stack: ",self.command_stack.size())

            print("STACK EMPTY")
        except Exception as e:
            print(f"ERROR processing SKU {sku}: {str(e)}")
            traceback.print_exc()
            self.command_stack.clear()

    # def _execute_action(self, criterion, action, sku, table_data):
    #     print(f"Executing action: {action} on criteria: {criterion.xpath}")
    #     print(f"Criteria details: {criterion}")
    #     print(f"Current action count: {criterion.actionCount}/{len(criterion.actions)}")
        
    #     try:
    #         command = self._parse_action(action)
    #         if action == "enter_string":
    #             command(criterion, sku)
    #         elif action == "add_to_table":
    #             # Example of data collection
    #             price = command(criterion)  # Assuming command returns the price
    #             print(price)
    #             table_data.append({
    #                 'url': self.interaction_service.driver.current_url,
    #                 'sku': sku,
    #                 'price': price,
    #                 'element_text': criterion.webElement.text,
    #                 'timestamp': datetime.now().isoformat()
    #             })
    #         else:
    #             command(criterion)
    #     except Exception as e:
    #         print(f"Error executing action {action}: {str(e)}")
    #         raise

    def _execute_action(self, criterion, action, sku, table_data):
        print(f"Executing action: {action} on criteria: {criterion.xpath}")
        max_retries = 1  # Will try once more after initial failure
        attempt = 0
        
        while attempt <= max_retries:
            try:
                self.interruption_handler.handle("before_step", criterion)

                print(f"Attempt {attempt + 1} of {max_retries + 1}")
                command = self._parse_action(action)
                
                if action == "enter_string":
                    command(criterion, sku),


                elif action == "add_to_table":
                    price =command(criterion),
                    table_data.append({
                        'url': self.interaction_service.driver.current_url,
                        'sku': sku,
                        'price': price,
                        'timestamp': datetime.now().isoformat()
                    })
                    print("TABLE DATA",table_data)

                else:
                    command(criterion),
                
                self.interruption_handler.handle("after_step", criterion)

 
                    #command(criterion)
                break  # Success - exit retry loop
            
                
            except Exception as e:
                attempt += 1
                if attempt > max_retries:
                    print(f"Failed after {max_retries + 1} attempts")
                    raise
                print(f"Retrying after error: {str(e)}")
                # Reset the element reference before retrying
                self._recovery_sequence(criterion, e, action)



    def _retry_element_interaction(self, action_func, xpath):
        """Helper method to retry element interactions"""
        try:
            return action_func()
        except Exception as e:
            print(f"Element interaction failed, refreshing reference to {xpath}")
            # Re-find the element before retrying
            element = self.interaction_service.smart_find(self.criteria_dict, xpath)
            if not element:
                raise Exception(f"Element not found after retry: {xpath}")
            return action_func()

        # the loop over the criteria actions handles this I think
        # if(criterion.childCount==0):
        #     criterion.setActionCount(criterion.actionCount + 1)

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
                xpath_id=getattr(criterion, 'xpath_id', 0)  # Handle indexed elements
            )
        except Exception as e:
            raise Exception(f"Element refresh failed for {criterion.xpath}: {str(e)}")

        # 3. Validate element state
        if not element.is_displayed():
            self.interaction_service.scroll_to(element)
        if not element.is_enabled():
            raise Exception(f"Element {criterion.xpath} exists but is disabled")

        # 4. Update criterion reference
        criterion.webElement = element
        return element
    
    def _handle_add_next_action(self, criterion: Criteria):
        """Handle the add_next action with proper drill-and-return behavior"""
        # Initialize child count if first time
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


    def add_next_crit(self, current_criteria: Criteria):
        """Add the next single criteria to the command stack"""
        #TODO: keep next actions in data format. If a certian part of the parent actions has to be repeated in order for each next action to work, 
        # add commands to manipulate action count in the next actions area so that when the stack gets back to the parent criteria, it reruns more than just the add next command
        if(current_criteria.childCount == -1):
            print("scape.py: setting child count")
            current_criteria.childCount= len(self.interaction_service.smart_find_elements(current_criteria.child))
            # If the current criteria has multiple children, make it so criteriaDict can decide which one to pick, or make the child property a list
        processed_count = current_criteria.childCount
        if(processed_count>0):   # ensures that once everthings proccessed, we can move past add next crit.
            new_crit = self.criteria_dict[current_criteria.child].copyWith(
                parent=current_criteria.xpath,
                xpath_id = processed_count
            ) # sets xpath_id to the processed count for the new criteria
            #TODO: execute next actions before pushing
            self.execute_next_actions(current_criteria)
            self.command_stack.push(new_crit)
            print("Pushing",new_crit.xpath)
            current_criteria.childCount = current_criteria.childCount-1

    def execute_next_actions(self, criterion):
        """Execute all transition actions between parent and child criteria"""
        for action_label in criterion.next_actions:
            print(f"Executing transition action: {action_label}")
            if action_label == "smart_find":
                # Special handling for smart_find since it needs the locator
                self.interaction_service.smart_find(self.criteria_dict, criterion.child)
            else:
                next_command = self._parse_action(action_label)
                next_command(criterion)


    def remove_self(self, curr_crit: Criteria):
        """Remove the current criteria from the dictionary"""
        self.criteria_dict.pop(curr_crit.xpath, None)

    def _parse_action(self, action: str):
        """Parse an action string and return the appropriate function"""
        print("ParseAction:", action)
        
        if action in self.function_map:
            return self.function_map[action]
        # elif "add_next" in action:
        #     return self.add_next_crit
        elif action == "remove_self":
            return self.remove_self
        else:
            return lambda *args, **kwargs: print("Unrecognized command; no action taken.")
        # ... (include all your helper methods like add_nth_child, add_crit_shallow, etc.)
        # Just convert them to class methods and adjust the self references

    # def handle_interruptions(self, trigger_condition, current_step=None):
    #     for interruption in self.config.get("interruptions", []):
    #         trigger = interruption.get("trigger", {})
            
    #         # Check if trigger condition matches
    #         if self._should_handle(trigger, trigger_condition, current_step):
    #             self._execute_interruption(interruption)

    # def _should_handle(self, trigger, condition, current_step):
    #     if trigger.get("on") != condition:
    #         return False
            
    #     # For step-specific triggers
    #     if condition in ["before_step", "after_step"]:
    #         return current_step and current_step.xpath == trigger.get("target_step")
            
    #     return True

    # def _execute_interruption(self, interruption):
    #     attempts = interruption["retry"]["attempts"]
    #     strategy = interruption["retry"]["strategy"]
        
    #     for attempt in range(attempts):
    #         try:
    #             element = self.find_element(interruption["xpath"])
    #             self.execute_actions(element, interruption["actions"])
    #             break
    #         except Exception as e:
    #             if attempt == attempts - 1:
    #                 raise
    #             self._apply_retry_delay(attempt, strategy)
    @staticmethod
    def _db_to_criteria_dict(criteria_list: List[Criteria]) -> Dict[str, Criteria]:
        return {criteria.xpath: criteria for criteria in criteria_list}

    @staticmethod
    def steps_to_criteria_dict(steps: List[dict]) -> Dict[str, 'Criteria']:
        criteria_dict = {}
        
        # First pass: Create all Criteria objects
        for step in steps:
            criteria = Criteria(step)  # Now accepts the full step dict
            criteria_dict[step['xpath']] = criteria
        
        # Second pass: Link parents/children
        for step in steps:
            if 'next' in step:
                parent = criteria_dict[step['xpath']]
                child_xpath = step['next']['xpath']
                
                if child_xpath in criteria_dict:
                    parent.child = child_xpath
                    criteria_dict[child_xpath].parent = parent.xpath
        
        return criteria_dict

    @staticmethod
    def _get_function_arguments(action: str) -> List[str]:
        match = re.match(r'\w+\((.*)\)', action)
        if match:
            return [arg.strip() for arg in re.split(r',\s*(?![^()]*\))', match.group(1))]
        raise ValueError("Invalid function call format.")

    @staticmethod
    def _decr_string_count(s: str) -> str:
        match = re.match(r'(\w+)\((.*),(.*),(\d+)\)$', s)
        if match:
            return f"{match.group(1)}({match.group(2)},{match.group(3)},{int(match.group(4))-1})"
        raise ValueError("Invalid string format.")