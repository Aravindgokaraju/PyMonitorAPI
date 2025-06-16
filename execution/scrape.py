import re
import traceback
from typing import Any, Dict, List, Tuple, Optional

from execution.models import SKU
from execution.mongo_service import MongoService
from .interaction_service import InteractionService
from .scraping_models import Criteria, Website
from .commandstack import CommandStack

class ScrapingService:
    def __init__(self):
        self.interaction_service = InteractionService()
        self.mongo_service = MongoService()
        self.command_stack = CommandStack()
        self.criteria_dict: Dict[str, Criteria] = {} #TODO: legacy variable, delete later
        self.parent_pair: Dict[str,str] = {}
        self.start_index = 0
        self.cachedWebsites
        
        # Initialize function map
        self.function_map = self._initialize_function_map()

    def _initialize_function_map(self):
        return {
            'open_site': self.interaction_service._open_website,
            'go_back': self.interaction_service._go_back,
            'basic_click': self.interaction_service._click,
            'strong_click': self.interaction_service._strong_click,
            'enter_string': self.interaction_service._enter_string,
            'test_command': self.interaction_service._test,
            'scroll_view': self.interaction_service._scroll_into_view,
            'fast_find': self.interaction_service._find_element,
            'fast_find_multiple': self.interaction_service._find_elements,
            'wait_find': self.interaction_service._wait_for_element_presence,
            'wait_click': self.interaction_service._wait_for_element_clickable,
            'local_finds': self.interaction_service._find_local_elements,
            'local_find': self.interaction_service._find_local_element,
            'self_find': self.interaction_service._find_self,
            'wait_find_self': self.interaction_service._wait_find_self,
            'print_text': self.interaction_service._print_text,
            'add_to_table': self.interaction_service._get_price,
            'sleep': self.interaction_service._sleep,
            'debug_print': self.interaction_service._debug,
        }

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

    def _get_sku_data(self) -> List[List[str]]:  # list of skus with each sku having a name, id, and number
        """Get SKU data from database"""
        skus = SKU.objects.all().values_list('sku_number', 'name', 'id')  # or whatever fields you need
        return [list(sku) for sku in skus]

    def _get_websites_data(self) -> List[Dict[str, Any]]:   #List of dicts each dict is a website, which has its own steps, actions, next, name etc
        """Get website data from Google Sheets and convert to Website objects"""
        website_data = self.mongo_service._get_websites_data()
        return website_data
        

    def _process_website(self, website_data:Dict[str, Any], skus: List[List[str]], table_data: List):
        """Process a single website with all SKUs"""
        self.command_stack.clear()
        # self.criteria_dict = self._criteria_to_dict(website.criteriaList) set this directly to the db object in sample_data
        self.start_index = 0
        
        self.interaction_service._open_website(website_data["id"])
        
        for full_sku in skus:
            if not full_sku:
                continue
                
            sku = full_sku[0]
            try:
                self._process_sku(website_data, sku, table_data)
            except:
                print("Skipping sku, error occured")


    def _process_sku(self, website_data: Dict[str, Any], sku: str, table_data: List):
        """Process a single SKU for a website"""
        sku_data = []
        #initial_criteria = self.criteria_dict[website.criteriaList[self.start_index].xpath].copyOf()
        initial_criteria = Criteria(website_data["steps"]) # Criteria will store its actions as well as its xpath removing need for global actions managment
        #Initial should be read from criteria dictionary
        self.command_stack.push(initial_criteria)
        
        try:
            while not self.command_stack.is_empty():
                criterion = self.command_stack.peek()
                webElement = self.interaction_service._find_element(self.criteria_dict,criterion.xpath) #You need criteria dict for parent finding features
                while criterion.actionCount < len(criterion.actions):
                    action = criterion.actions[criterion.actionCount]
                    self._execute_action(criterion, action, sku, sku_data) # If this returns an error and action count is zero, then retry find
                    
                self.command_stack.pop()
                
            if sku_data:
                table_data.extend(sku_data)
                
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
    def _execute_action(self, criterion: Criteria, action: str, sku: str, sku_data: List):
        """Execute a single action from criteria"""
        command = self._parse_action(action)
        if action == "enter_string":
             command(criterion, sku)
        else:
            command(criterion)
        if(criterion.childCount==0):
            criterion.setActionCount(criterion.actionCount + 1)



    def add_next_crit(self, current_criteria: Criteria):
        """Add the next single criteria to the command stack"""
        if(current_criteria.childCount == -1):
            print("scape.py: setting child count")
            current_criteria.childCount= self.interaction_service._smart_find_elements(current_criteria.child).count() 
            # If the current criteria has multiple children, make it so criteriaDict can decide which one to pick, or make the child property a list
        processed_count = current_criteria.childCount

        new_crit = self.criteria_dict[current_criteria.child].copyOf(
            xpath_id=processed_count
        ) # sets xpath_id to the processed count for the new criteria
        self.command_stack.push(new_crit)
        current_criteria.setChildCount(current_criteria.childCount-1)

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
        """
        Converts a list of step dictionaries into a dictionary of Criteria objects.
        
        Args:
            steps: List of step dictionaries containing xpath, actions, and next info
            
        Returns:
            Dictionary where keys are xpaths and values are corresponding Criteria objects
        """
        criteria_dict = {}
        parent_child_map = {}  # Temporary storage for parent-child relationships
        
        # First pass: Create all Criteria objects
        for step in steps:
            commands = [step['xpath']] + step.get('actions', [])
            criteria = Criteria(commands)
            
            # Store parent-child relationships if next exists
            if 'next' in step:
                parent_child_map[step['xpath']] = step['next']['xpath']
            
            criteria_dict[step['xpath']] = criteria
        
        # Second pass: Establish parent-child relationships
        for parent_xpath, child_xpath in parent_child_map.items():
            if parent_xpath in criteria_dict and child_xpath in criteria_dict:
                criteria_dict[parent_xpath].child = child_xpath
                criteria_dict[child_xpath].parent = parent_xpath
        
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