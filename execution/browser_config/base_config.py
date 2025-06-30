from selenium.webdriver.chrome.options import Options
import random
import tempfile
import os

class BaseConfig:
    def __init__(self):
        self.chrome_options = Options()
        
    def apply(self):
        # Common settings that apply to all configurations
        self.chrome_options.add_argument("--ignore-certificate-errors")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument('--disable-extensions')
        self.chrome_options.add_argument('--disable-infobars')
        self.chrome_options.add_argument("--no-sandbox")
        
        # Random window size
        self.chrome_options.add_argument(
            f"--window-size={random.randint(1000,1400)},{random.randint(800,1000)}"
        )
        
        return self.chrome_options