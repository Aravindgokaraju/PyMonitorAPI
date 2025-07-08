import time
from selenium.webdriver.chrome.options import Options
import random
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium import webdriver

import tempfile
import os

class StableConfig:
    def __init__(self):
        self.chrome_options = Options()
        
    def apply(self):
        """Apply all Chrome configuration options for stable browsing"""
        # Common settings from BaseConfig
        self.chrome_options.add_argument("--ignore-certificate-errors")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument('--disable-extensions')
        self.chrome_options.add_argument('--disable-infobars')
        self.chrome_options.add_argument("--no-sandbox")
        
        # Random window size
        self.chrome_options.add_argument(
            f"--window-size={random.randint(1000,1400)},{random.randint(800,1000)}"
        )
        self.chrome_options.add_argument("--ignore-certificate-errors")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument('--disable-extensions')
        self.chrome_options.add_argument('--disable-infobars')
        self.chrome_options.add_argument("--no-sandbox")
        
        
        # Minimal stealth settings from StableConfig
        self.chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        self.chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        
        return self.chrome_options
    
    def create_driver(self):
        """
        Creates and returns a standard Selenium Chrome WebDriver instance
        with the configured options.
        
        Automatically handles driver management using webdriver-manager.
        """
        # Apply all configurations
        self.apply()
        
        # Create driver with automatic ChromeDriver management
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=self.chrome_options
        )
        
        return driver
    
    def test_driver(self, test_url="https://fingerprint-scan.com/", delay_seconds=0):
        """
        Test the basic driver configuration with proper resource cleanup
        Returns: (driver, results_dict)
        """
        driver = None
        try:
            driver = self.create_driver()
            driver.get(test_url)
            driver.implicitly_wait(5)
            
            if delay_seconds > 0:
                time.sleep(delay_seconds)
                
            results = {
                'user_agent': driver.execute_script("return navigator.userAgent"),
                'webdriver': driver.execute_script("return navigator.webdriver"),
                'test_url': test_url,
                'page_title': driver.title,
                'page_url': driver.current_url,
                'window_size': driver.get_window_size()
            }
            
            return driver, results
            
        except Exception as e:
            if driver:
                try:
                    driver.quit()
                except Exception as quit_error:
                    print(f"⚠️ Error while quitting driver: {str(quit_error)}")
            raise RuntimeError(f"Driver test failed: {str(e)}")
        finally:
            if driver:
                try:
                    driver.quit()
                except Exception as quit_error:
                    print(f"⚠️ Error in final driver cleanup: {str(quit_error)}")