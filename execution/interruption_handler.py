from selenium.common.exceptions import NoSuchElementException
import time

class InterruptionHandler:
    def __init__(self, interaction_service):
        self.interaction = interaction_service
        self.interruptions = []

    def load_interruptions(self, interruptions_config):
        """Load interruptions configuration"""
        self.interruptions = interruptions_config

    def handle(self, trigger_type, current_step=None, error=None):
        """Main handling entry point"""
        for interruption in self.interruptions:
            if self._should_handle(interruption, trigger_type, current_step, error):
                self._execute_interruption(interruption)

    def _should_handle(self, interruption, trigger_type, current_step, error):
        trigger = interruption.get("trigger", {})
        if trigger.get("on") != trigger_type:
            return False

        # Error type filtering
        if trigger_type == "on_error" and "error_types" in trigger:
            if error.__class__.__name__ not in trigger["error_types"]:
                return False

        # Step targeting
        if trigger_type in ["before_step", "after_step"]:
            return current_step and current_step.xpath == trigger.get("target_step")

        return True

    def _execute_interruption(self, interruption):
        attempts = interruption["retry"].get("attempts", 1)
        delay = interruption["retry"].get("delay_ms", 1000) / 1000

        for attempt in range(attempts):
            try:
                element = self.interaction.smart_find(None, interruption["xpath"])
                for action in interruption["actions"]:
                    self.interaction.execute_action(element, action)
                return True
            except Exception as e:
                if attempt == attempts - 1:
                    raise
                time.sleep(delay)
        return False