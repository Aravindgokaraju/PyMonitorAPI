import json
import re
from typing import List, Optional
from selenium.webdriver.remote.webelement import WebElement

from execution.interaction_service import InteractionService


class Website:


    def __repr__(self):
        print(self.criteria)
        return (f"ExampleClass(url='{self.url}', criteria={self.criteria})")
    
    def __init__(self,siteName:str, rawCriteria:str):
        #RawCriteria is a string depicting an array of arrays with each subarray being the name of a DOM element followed by actions to take on it
        print("\nCriteria:  "+ rawCriteria+"\n")
        rawListCriteria = json.loads(rawCriteria)
        elementCommandList:list = []
        for criterion in rawListCriteria:
            array = re.findall(r"'([^']*)'", criterion)
            parsedCriterion:Criteria = Criteria(array)

            elementCommandList.append(parsedCriterion)   
        
        self.criteriaList = elementCommandList
        self.url = siteName



class Criteria:
    def __init__(self, step_data: dict):  # Changed from commands:list to step_data:dict
        """
        Enhanced Criteria class that handles both current actions and next_actions.
        
        Args:
            step_data: Dictionary containing:
                - xpath: str
                - actions: List[str] (actions for current step)
                - next: Optional[dict] with:
                    - xpath: str
                    - actions: List[str] (transition actions)
        """
        # Core element identification
        self.xpath = step_data['xpath']
        self.xpath_id = 0  # Used for finding specific elements
        
        # Action tracking
        self.actions = step_data.get('actions', [])
        self.actionCount = 0
        
        # Child element handling
        self.childCount = -1
        self.child = step_data.get('next', {}).get('xpath', "")
        
        # Next step transition actions
        self.next_actions = step_data.get('next', {}).get('actions', [])
        
        # Parent reference
        self.parent = ""

        self.webElement = None

    def copyOf(self):
        """Create a basic copy with same xpath and actions"""
        return Criteria({
            'xpath': self.xpath,
            'actions': self.actions.copy(),
            **({'next': {'xpath': self.child, 'actions': self.next_actions.copy()}} 
               if self.child else {})
        })

    def copyWith(self, **kwargs):
        """Enhanced copy with overrides that preserves all relationships"""
        new_data = {
            'xpath': kwargs.get('xpath', self.xpath),
            'actions': self.actions.copy(),  # Original actions preserved
            'next': {
                'xpath': kwargs.get('child', self.child),
                'actions': self.next_actions.copy()
            } if self.child else {}
        }
        
        new_criteria = Criteria(new_data)
        
        # Set additional attributes
        new_criteria.actionCount = kwargs.get('actionCount', self.actionCount)
        new_criteria.childCount = kwargs.get('childCount', self.childCount)
        new_criteria.xpath_id = kwargs.get('xpath_id', self.xpath_id)
        new_criteria.parent = kwargs.get('parent', self.parent)
        
        return new_criteria

    # def copyWith(self, **kwargs):
    #     """Enhanced copy with overrides that preserves all relationships but resets action state"""
    #     new_data = {
    #         'xpath': kwargs.get('xpath', self.xpath),
    #         'actions': self.actions.copy(),  # Original actions preserved
    #         'next': {
    #             'xpath': kwargs.get('child', self.child),
    #             'actions': self.next_actions.copy()
    #         } if self.child else {}
    #     }
        
    #     new_criteria = Criteria(new_data)
        
    #     # Reset action state for new processing
    #     new_criteria.actionCount = 0
    #     new_criteria.childCount = -1
        
    #     # Set additional attributes
    #     new_criteria.xpath_id = kwargs.get('xpath_id', self.xpath_id)
    #     new_criteria.parent = kwargs.get('parent', self.parent)
        
    #     return new_criteria
    
    # def setActionCount(self, newCount):
    #     self.actionCount = newCount
    
    # def setChildCount(self, newCount):
    #     self.childCount = newCount

    # def __repr__(self):
    #     return (f"Criteria(xpath='{self.xpath}', "
    #         f"actions={self.actions}, "
    #         f"current_action_index={self.actionCount}, "
    #         f"child_xpath='{self.child}', "
    #         f"child_count={self.childCount}, "
    #         f"next_actions={self.next_actions}, "
    #         f"web_element={bool(self.webElement)})")
# class Criteria:
    
#     def __init__(self, commands:list):
#         #Criterion Array holds the specifics for ONE criterion is in format of:
#         #[xpath,action1,action2,action3]
        
#         self.xpath = commands[0]
#         self.actionCount = 0  # TODO: Implement Action Count into Stack logic to keep track of which action is left of at
#         # IMPORTANT: If the child has multiple instances in which we have to sift through, this keeps track of the number of objects in child, actionCount cannot increment unless this is 0
#         #This will also be the number used to add the nth child with the same child to the stack
#         self.childCount=-1
#         self.xpath_id = 0 # used in find command to find specific element
#         self.actions:list =[]
#         self.next_actions:list = []
#         self.parent = ""
#         self.child=""
        


#         for i in range(1, len(commands)):
#             self.actions.append(commands[i])
    
#     def copyOf(self):
#         # Create a copy of the instance by using the same xpath and actions list
#         return Criteria([self.xpath] + self.actions)

#     def copyWith(self, **kwargs):
#         """Create a copy of the Criteria with the same actions, allowing optional overrides for other attributes.
        
#         Args:
#             **kwargs: Optional attributes to override in the new copy (xpath, actionCount, childCount, etc.)
#                     Actions cannot be overridden through this method.
                    
#         Returns:
#             A new Criteria instance with the same actions and any specified attribute overrides.
#         """
#         # Start with the original xpath and actions
#         new_commands = [kwargs.get('xpath', self.xpath)] + self.actions
        
#         # Create the new instance
#         new_criteria = Criteria(new_commands)
        
#         # Set other attributes (either from kwargs or original values)
#         new_criteria.actionCount = kwargs.get('actionCount', self.actionCount)
#         new_criteria.childCount = kwargs.get('childCount', self.childCount)
#         new_criteria.xpath_id = kwargs.get('xpath_id', self.xpath_id)
#         new_criteria.parent = kwargs.get('parent', self.parent)
#         new_criteria.child = kwargs.get('child', self.child)
    
#         return new_criteria
#     def setActionCount(self,newCount):
#         self.actionCount = newCount
    
#     def setChildCount(self,newCount):
#         self.childCount = newCount
    
    



#     def __repr__(self):
#         return (f"SampleClass(xpath='{self.xpath}', actions ='{self.actions[0]}')")
    
#     # def _initWebElement(self,element):
#     #     self.webElement = element
