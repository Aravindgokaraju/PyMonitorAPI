

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

    def __repr__(self) -> str:
        """Returns a detailed, unambiguous string representation of the Criteria object.
        Shows all key attributes and relationships in a developer-friendly format.
        """
        repr_parts = [
            f"<Criteria(xpath='{self.xpath}'",
            f"xpath_id={self.xpath_id}",
            f"actions={self.actions}",
            f"actionCount={self.actionCount}/{len(self.actions)}",
            f"child='{self.child}'" if self.child else "child=None",
            f"childCount={self.childCount}" if self.childCount != -1 else "childCount=unset",
            f"next_actions={self.next_actions}" if self.next_actions else "next_actions=[]",
            f"parent='{self.parent}'" if self.parent else "parent=None",
            f"webElement={'set' if self.webElement else 'None'}"
        ]
        return ", ".join(repr_parts) + ">"