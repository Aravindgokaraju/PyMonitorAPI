from .base_config import BaseConfig

class StableConfig(BaseConfig):
    def apply(self):
        # Apply base configurations first
        super().apply()
        
        # Minimal stealth settings
        self.chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        self.chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        
        return self.chrome_options