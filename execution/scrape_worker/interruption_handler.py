
class InterruptionHandler:
    def __init__(self, interaction_service):
        self.interaction = interaction_service
        self.interruptions = []
        self.function_map = self.interaction._initialize_function_map()


    def load_interruptions(self, interruptions_config):
        """Load interruptions configuration"""
        print("Loading interruptions")
        self.interruptions = interruptions_config

    def handle(self, trigger_type, current_step=None, error=None):
        """Main handling entry point"""
        for interruption in self.interruptions:
            if self._should_handle(interruption, trigger_type, current_step, error):
                print("Executing interruption in handle")
                self._execute_interruption(interruption)
                break
    
    #TODO: remove current_step and the whole passing it down chain
    def _should_handle(self, interruption, trigger_type, current_step, error):
        trigger = interruption.get("trigger", {})
        print("Should Handling Trigger:", trigger, trigger.get("on"))

        if trigger.get("on") != trigger_type:
            return False

        # Add proper error object checking
        if trigger_type == "on_error":
            if error is None:
                return False
            if not hasattr(error, '__class__'):
                return False
            if "error_types" in trigger:
                error_name = error.__class__.__name__
                if error_name not in trigger["error_types"]:
                    return False



            # Step targeting
            # if trigger_type in ["before_step", "after_step"]:
            #     return current_step and current_step.xpath == trigger.get("target_step")

        return True
    
    def _execute_interruption(self, interruption):
        """Executes interruption actions if the element is found.
        Returns:
            bool: True if actions were executed, False if element not found.
        """
        print("executing interruption")
        element = self.interaction.smart_find(None, interruption["xpath"],None,1)
        if not element:
            print(f"Interruption element not found: {interruption['xpath']}")
            return False

        for action in interruption["actions"]:
            print(f"Executing interruption action: {action}")
            command = self.function_map.get(action)
            if not command:
                print(f"Action '{action}' not found in function_map")
                continue
            command(element)  # Execute action on the element
            print(f"Successfully executed: {action}")

        return True  # All actions executed successfully
    
    def _execute_interruption_with_retry(self, interruption):
        attempts = interruption["retry"].get("attempts", 1)
        delay = interruption["retry"].get("delay_ms", 1000) / 1000

        for attempt in range(attempts):
            try:
                element = self.interaction.smart_find(None, interruption["xpath"],None,2)
                if not element:  # If element not found, skip actions
                    print(f"Interruption element not found (attempt {attempt + 1}/{attempts})")
                    continue  # Try again (if retries left)
                for action in interruption["actions"]:
                    print("EXECUTE INTERRUPTION ACTION ",action)
                    command = self.function_map.get(action)
                    command(element) #TODO: make a webElement overload
                    print("EXECUTED ",action)
                return True
            except Exception as e:
                if attempt == attempts - 1:
                    raise
                # time.sleep(delay)
        return False