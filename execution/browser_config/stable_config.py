import time
from selenium.webdriver.chrome.options import Options
import random
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
import os

class StableConfig:
    def __init__(self):
        print("STABLE CONFIG CONFIGING")
        self.chrome_options = Options()
        
    def apply(self):
        """Apply all Chrome configuration options for stable browsing"""
        # Common settings
        self.chrome_options.add_argument("--ignore-certificate-errors")
        self.chrome_options.add_argument("--headless=new")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument('--disable-extensions')
        self.chrome_options.add_argument('--disable-infobars')
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument('--disable-gpu')
        self.chrome_options.add_argument('--remote-debugging-port=9222')

        # Use environment variable or fallback
        chrome_bin = os.environ.get('CHROME_BIN')
        self.chrome_options.binary_location = chrome_bin

        # Random window size
        self.chrome_options.add_argument(
            f"--window-size={random.randint(1000,1400)},{random.randint(800,1000)}"
        )
        
        # Stealth settings
        self.chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        self.chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.chrome_options.add_experimental_option('useAutomationExtension', False)
        
        return self.chrome_options
    
    def create_driver(self):
        """
        Creates and returns a standard Selenium Chrome WebDriver instance
        with the configured options.
        
        Let webdriver-manager handle ChromeDriver installation automatically.
        """
        # Apply all configurations
        self.apply()
        
        # Use webdriver-manager to automatically handle ChromeDriver installation
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=self.chrome_options)
        
        # Additional stealth measure
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver
    
    def test_driver(self, test_url="https://httpbin.org/user-agent", delay_seconds=2):
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
                'window_size': driver.get_window_size(),
                'success': True
            }
            
            return driver, results
            
        except Exception as e:
            results = {
                'success': False,
                'error': str(e),
                'test_url': test_url
            }
            return None, results
        finally:
            if driver:
                try:
                    driver.quit()
                except Exception as quit_error:
                    print(f"⚠️ Error while quitting driver: {str(quit_error)}")


# import time
# from selenium.webdriver.chrome.options import Options
# import random
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.chrome.service import Service
# from selenium import webdriver

# import tempfile
# import os

# class StableConfig:
#     def __init__(self):
#         self.chrome_options = Options()
        
#     def apply(self):
#         """Apply all Chrome configuration options for stable browsing"""
#         # Common settings from BaseConfig
#         self.chrome_options.add_argument("--ignore-certificate-errors")
#         self.chrome_options.add_argument("--headless=new")
#         self.chrome_options.add_argument("--disable-dev-shm-usage")
#         self.chrome_options.add_argument('--disable-extensions')
#         self.chrome_options.add_argument('--disable-infobars')
#         self.chrome_options.add_argument("--no-sandbox")

#         #For Docker container
#         # self.chrome_options.binary_location = '/usr/bin/google-chrome-stable'  # Explicit path

#         #For Local Testing WINDOWS
#         # self.chrome_options.binary_location = r'C:/Program Files/Google/Chrome/Application/chrome.exe'

#         #LINUX
#         self.chrome_options.binary_location = '/usr/bin/google-chrome'  

#         # Random window size
#         self.chrome_options.add_argument(
#             f"--window-size={random.randint(1000,1400)},{random.randint(800,1000)}"
#         )
#         self.chrome_options.add_argument("--ignore-certificate-errors")
#         self.chrome_options.add_argument("--disable-dev-shm-usage")
#         self.chrome_options.add_argument('--disable-extensions')
#         self.chrome_options.add_argument('--disable-infobars')
#         self.chrome_options.add_argument("--no-sandbox")
        
        
#         # Minimal stealth settings from StableConfig
#         self.chrome_options.add_argument("--disable-blink-features=AutomationControlled")
#         self.chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        
#         return self.chrome_options
    
#     def create_driver(self):
#         """
#         Creates and returns a standard Selenium Chrome WebDriver instance
#         with the configured options.
        
#         Automatically handles driver management using webdriver-manager.
#         """
#         # Apply all configurations
#         self.apply()
        
#         # Create driver with automatic ChromeDriver management
#         driver = webdriver.Chrome(
#             service=Service(ChromeDriverManager().install()),
#             options=self.chrome_options
#         )
        
#         return driver
    
#     def test_driver(self, test_url="https://fingerprint-scan.com/", delay_seconds=0):
#         """
#         Test the basic driver configuration with proper resource cleanup
#         Returns: (driver, results_dict)
#         """
#         driver = None
#         try:
#             driver = self.create_driver()
#             driver.get(test_url)
#             driver.implicitly_wait(5)
            
#             if delay_seconds > 0:
#                 time.sleep(delay_seconds)
                
#             results = {
#                 'user_agent': driver.execute_script("return navigator.userAgent"),
#                 'webdriver': driver.execute_script("return navigator.webdriver"),
#                 'test_url': test_url,
#                 'page_title': driver.title,
#                 'page_url': driver.current_url,
#                 'window_size': driver.get_window_size()
#             }
            
#             return driver, results
            
#         except Exception as e:
#             if driver:
#                 try:
#                     driver.quit()
#                 except Exception as quit_error:
#                     print(f"⚠️ Error while quitting driver: {str(quit_error)}")
#             raise RuntimeError(f"Driver test failed: {str(e)}")
#         finally:
#             if driver:
#                 try:
#                     driver.quit()
#                 except Exception as quit_error:
#                     print(f"⚠️ Error in final driver cleanup: {str(quit_error)}")