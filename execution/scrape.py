import json
import os
import re

import traceback
from typing import Any, Dict, List, Tuple, Optional

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
            {"sku_id": "12345", "name": "Test Product 1", "id": "1"},
            {"sku_id": "67890", "name": "Test Product 2", "id": "2"}
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
        test_file = os.path.join(current_dir, 'test_data.json')
        
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
        """Process a single SKU for a website"""
        print(f"Processing SKU: {sku} for website: {website_data['url']}")
        print(f"Website data: {website_data}")
        sku_data = []
        #initial_criteria = self.criteria_dict[website.criteriaList[self.start_index].xpath].copyOf()
        #initial_criteria = Criteria(website_data["steps"].hasProperty("init==true")) # Criteria will store its actions as well as its xpath removing need for global actions managment
        #Initial should be read from criteria dictionary
        initial_step = next(
        step for step in website_data["steps"] 
        if step.get("start_trigger", False)
        )
        initial_criteria = self.criteria_dict[initial_step["xpath"]]
        print(f"Initial criteria selected: {initial_criteria}")

        self.command_stack.push(initial_criteria)
        print(f"Command stack after push: {[c.xpath for c in self.command_stack.stack]}")

        
        try:
            while not self.command_stack.is_empty():
                # Get the current criterion without removing it from the stack
                criterion = self.command_stack.peek()
                
                # Find the web element for this criterion
                webElement = self.interaction_service.smart_find(self.criteria_dict, criterion.xpath)
                criterion.webElement = webElement
                
                # Process all actions for this criterion
                while criterion.actionCount < len(criterion.actions):
                    action = criterion.actions[criterion.actionCount]
                    
                    # Execute the current action
                    self._execute_action(criterion, action, sku, sku_data)
                    
                    # Check if stack has changed (new item pushed or current item removed)
                    current_top = self.command_stack.peek() if not self.command_stack.is_empty() else None
                    if current_top != criterion:
                        # Stack changed - break out of action loop to reprocess new top
                        break
                        
                    # Only increment action counter if we're still processing the same criterion
                    if current_top == criterion:
                        criterion.actionCount += 1
                    else:
                        # Only reached if all actions completed without stack change
                        # Remove the completed criterion from the stack
                        self.command_stack.pop()
                        
                        # Perform the final act operation
                        continue  # Skip the break below
                    
                    # If we get here, the stack changed mid-processing
                    break  # Exit action loop to reprocess new stack top
                
                
        except Exception as e:
            print(f"ERROR processing SKU {sku}: {e}")
            # Mark as unavailable
            table_data.append((website_data["url"], sku, "Unavailable"))

    # def _execute_action(self, criterion: Criteria, action: str, sku: str, sku_data: List):
    #     """Execute a single action from criteria"""
    #     command = self._parse_action(action)
        
    #     if action == "enter_string":
    #         command(criterion, sku)
    #     elif action == "add_to_table":
    #         price = command(criterion)
    #         sku_data.append((criterion.webElement.parent.current_url, sku, price))
    #     elif "addCritDeep" in action:
    #         self._handle_add_crit_deep(criterion, action)
    #     elif "addCritShallow" in action:
    #         self._handle_add_crit_shallow(criterion, action)
    #     elif "addNextCrit" in action:
    #         self._handle_add_next_crit(criterion, action)
    #     elif action == "inc_start":
    #         self.start_index += 1
    #     else:
    #         command(criterion)
            
    #     criterion.setActionCount(criterion.actionCount + 1)
    def _execute_action(self, criterion, action, sku, sku_data):
        print(f"Executing action: {action} on criteria: {criterion.xpath}")
        print(f"Criteria details: {criterion}")
        print(f"Current action count: {criterion.actionCount}/{len(criterion.actions)}")
        
        try:
            command = self._parse_action(action)
            if action == "enter_string":
                command(criterion, sku)
            else:
                command(criterion)
        except Exception as e:
            print(f"Error executing action {action}: {str(e)}")
            raise


        # the loop over the criteria actions handles this I think
        # if(criterion.childCount==0):
        #     criterion.setActionCount(criterion.actionCount + 1)



    def add_next_crit(self, current_criteria: Criteria):
        """Add the next single criteria to the command stack"""
        #TODO: keep next actions in data format. If a certian part of the parent actions has to be repeated in order for each next action to work, 
        # add commands to manipulate action count in the next actions area so that when the stack gets back to the parent criteria, it reruns more than just the add next command
        if(current_criteria.childCount == -1):
            print("scape.py: setting child count")
            current_criteria.childCount= self.interaction_service.smart_find_elements(current_criteria.child).count() 
            # If the current criteria has multiple children, make it so criteriaDict can decide which one to pick, or make the child property a list
        processed_count = current_criteria.childCount
        if(processed_count>0):   # ensures that once everthings proccessed, we can move past add next crit.
            new_crit = self.criteria_dict[current_criteria.child].copyOf(
                xpath_id=processed_count
            ) # sets xpath_id to the processed count for the new criteria
            #TODO: execute next actions before pushing
            self.execute_next_actions(current_criteria)
            self.command_stack.push(new_crit)
            current_criteria.childCount = current_criteria.childCount-1

    def execute_next_actions(self,criterion):
        for action_label in criterion.next_actions:
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
        elif "addNextCrit" in action:
            return self.add_next_crit
        elif action == "remove_self":
            return self.remove_self
        else:
            return lambda *args, **kwargs: print("Unrecognized command; no action taken.")
        # ... (include all your helper methods like add_nth_child, add_crit_shallow, etc.)
        # Just convert them to class methods and adjust the self references

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