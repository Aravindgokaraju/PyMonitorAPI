import re
import time
from typing import List
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import TimeoutException


#NO GLOBAL CRITERIA, CRITERIA SHOULD BE PASSED IN FROM MAIN NOT STORED AS A GLOBAL HERE TO BE USED BY THE FUNCTIONS

class InteractionService:

    def __init__(self):
        # Set up Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--ignore-certificate-errors")
        chrome_options.add_argument("--disable-dev-shm-usage")
        #chrome_options.add_argument("--headless")
        chrome_options.add_argument('--disable-extensions')  # Disable extensions
        chrome_options.add_argument('--disable-infobars')  # Disable popups like "Chrome is being controlled by automated software"
        chrome_options.add_argument("--allow-insecure-localhost")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--no-sandbox")

        # Initialize ChromeDriver using ChromeDriverManager
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

        # Initialize ActionChains for performing complex actions
        self.action = ActionChains(self.driver)




    def _initialize_function_map(self):
            return {
                'open_site': self._open_website,
                'go_back': self._go_back,
                'basic_click': self._click,
                'strong_click': self._strong_click,
                'enter_string': self._enter_string,
                'test_command': self._test,
                'scroll_view': self._scroll_into_view,
                'fast_find': self._find_element,
                'fast_find_multiple': self._find_elements,
                'wait_find': self._wait_for_element_presence,
                'wait_click': self._wait_for_element_clickable,
                'wait_find_self': self._wait_find_self,
                'smart_find':self.smart_find,
                'print_text': self._print_text,
                'add_to_table': self._get_price,
                'sleep': self._sleep,
                'debug_print': self._debug,
            }





# FUNDAMENTAL FUNCTIONS

    #DEBUG FUNCTIONS
    def _sleep(self,criterion):
        time.sleep(10)
    def _debug(self,criterion):
        print("DEBUG COMMAND")

    # OPEN WEBSITE
    def _open_website(self, websiteURL):
        """Opens a given website using the driver."""
        print(f"Opening website: {websiteURL}")
        self.driver.get(websiteURL)
        print(f"Current URL: {self.driver.current_url}")
    

    # FAST FIND ELEMENT
    # not used in practice
    
    def _wait_find_self(self, criterion):
        path = criterion.xpath
        print(f"Using XPath: {path}")
    
        try:
            criterion.webElement = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, path))
            )
            print("Element found successfully")
            return True
        except TimeoutException:
            print(f"\nERROR: Timed out after 10 seconds while waiting for element with XPath: {path}")
            print("Possible reasons:")
            print("- The element doesn't exist")
            print("- The XPath is incorrect")
            print("- The page took too long to load")
            print("- The element is in an iframe")
            return False
        except Exception as e:
            print(f"\nERROR: An unexpected error occurred while waiting for element: {str(e)}")
            return False
    def _find_element(self,nextPath,itemNo=0):
        """Finds element"""
        indexed_path = f"({nextPath})[{itemNo + 1}]"
        return self.driver.find_element(By.XPATH, indexed_path)
    
    
    def _find_elements(self,nextPath):
        return self.driver.find_elements(By.XPATH, nextPath)
    


    #TODO: See if I need to pass in criteria or if I can just pass in xpath
    #WAIT FIND ELEMENT
    #redundant
    def _wait_for_element_presence(self, nextPath):
        """waits until the desired element gets detected"""
        return WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, nextPath))
        )     
    #WAIT TIL ELEMENT CLICKABLE
    #TODO: same as wait find but passing in path?
    def _wait_for_element_clickable(self, nextPath):
        """waits until the desired element gets marked as clickable"""
        return WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, nextPath))
        )


    
        
    def smart_find(self, criteria_dict, locator, parent_element=None, timeout=10):
        """
        Consolidated find function that tries:
        1. Wait-based global find first
        2. Wait-based local find (if parent provided)
        3. Returns None if neither succeeds
        
        Args:
            locator: XPath string (should work for both global and local)
            parent_element: Optional parent WebElement for local search
            timeout: Maximum wait time in seconds
        
        Returns:
            WebElement if found, None otherwise
        """
        def _wait_find(search_context, xpath):
            try:
                print("search context, ",search_context)
                print("xpath, ",xpath)
                return WebDriverWait(search_context, timeout).until(
                    EC.presence_of_element_located((By.XPATH, xpath)))
            except TimeoutException:
                print("TimeOut Exception on FInd")
                return None
        print("global find")
        # First try global find
        element = _wait_find(self.driver, locator)
        if element:
            print("ELEMENT FOUND locator:",locator)
            return element
        print("local find find")
        
        # If global fails and parent provided, try local find
        if parent_element is not None:
            # Convert to local XPath if not already
            local_locator = locator if locator.startswith('.') else f'.{locator}'
            print("ELEMENT FOUND local_locator:",local_locator)

            return _wait_find(parent_element, local_locator)
        
        return None
        
    # GO BACK
    def _go_back(self):
        self.driver.back()


    def smart_find_elements(self, locator, parent_element=None, timeout=10):
        """
        Consolidated find elements function that tries:
        1. Wait-based global find first
        2. Wait-based local find (if parent provided)
        3. Returns empty list if neither succeeds
        
        Args:
            locator: XPath string (should work for both global and local)
            parent_element: Optional parent WebElement for local search
            timeout: Maximum wait time in seconds
            
        Returns:
            List of WebElements if found, empty list otherwise
        """
        def _wait_find_elements(search_context, xpath):
            try:
                # Wait for at least one element to be present
                WebDriverWait(search_context, timeout).until(
                    EC.presence_of_element_located((By.XPATH, xpath)))
                # Then return all matching elements
                return search_context.find_elements(By.XPATH, xpath)
            except TimeoutException:
                return []
                
        # First try global find
        elements = _wait_find_elements(self.driver, locator)
        if elements:
            return elements
            
        # If global fails and parent provided, try local find
        if parent_element is not None:
            # Convert to local XPath if not already
            local_locator = locator if locator.startswith('.') else f'.{locator}'
            return _wait_find_elements(parent_element, local_locator)
        
        return []

# SELENIUM FUNCTIONS

    # SELENIUM CLICK
    def _click(self,criterion):
        webElement = criterion.webElement
        webElement.click()

    # ENTER VALUE INTO TEXTBOX AND SUBMIT
    def _enter_string(self,criterion, skuString):
        webElement = criterion.webElement
        webElement.send_keys(skuString)
        self.action.send_keys(Keys.RETURN).perform()
    
    def _print_text(self,criterion):
        webElement = criterion.webElement
        print(webElement.text)

    def _get_price(self,criterion):
        print("Appending Data")
        webElement = criterion.webElement
        ans = self.extract_price(webElement.text)
        if(ans):
            return ans
        else: return -1

    def extract_price(self,text):
        # Regular expression to match price patterns (e.g., $123.45, €123, 123.45)
        match = re.search(r'\b[$€£]?\d+(?:\.\d{1,2})?\b', text)
        if match:
            # Remove currency symbols and convert to float
            return float(match.group().lstrip('$€£'))
        return None


# ALERT CLOSING FUNCTIONS
    
    #CLOSE JAVASCRIPT ALERT
    def _close_alert(self):
        try:
            alert = self.driver.switch_to.alert
            alert_text = alert.text
            print(f"Alert text: {alert_text}")
            alert.dismiss()  # or alert.accept() to confirm
        except :
            print("No alert present on the page.")

    #BASIC IFRAME REMOVAL TODO GO IN DEPTH LATER IF NEEDED
    def _close_iframe(self,criterion):
        path = criterion.xpath
        self.driver.switch_to.default_content()
        # Use JavaScript to remove the iframe
        iframe_id = path  # Replace with the actual ID or selector of the iframe
        self.driver.execute_script(f"document.getElementById('{iframe_id}').remove();")

    
    

# JAVASCRIPT HARD FUNCTIONS

    # JAVASCRIPT CLICK
    def _strong_click(self,criterion):
        webElement = criterion.webElement
        self.driver.execute_script("arguments[0].click();", webElement)
        #time.sleep(5)

    def _scroll_into_view(self,criterion):
        webElement = criterion.webElement
        self.driver.execute_script("arguments[0].scrollIntoView(true);", webElement)

    
    # FOR ALERTS
    def _force_remove(self,criterion):
        self.driver.execute_script("document.querySelector('" + criterion.xpath + "').style.display = 'none';")


        
        
    
    def _read_xpath_string(self,criterion):
        webElement = criterion.webElement
        print(webElement.text)
            
    
       
            

    # def _print_string(self,criterion):
    #     path = criterion.xpath
    #     div_element = WebDriverWait(self.driver, 10).until(
    #     EC.presence_of_element_located((By.XPATH, path ))
    #     )
    #         # Find the list inside the div
    #     list_element = div_element.find_element(By.TAG_NAME, "ul")
            
    #         # Find all list items
    #     list_items = list_element.find_elements(By.TAG_NAME, "li")
            
    #         # Get the last list item
    #     last_item = list_items[-1]
            
    #         # Get the text of the last list item

    #     self.driver.execute_script("arguments[0].scrollIntoView(true);", div_element)
    #     last_item_text = last_item.text
            
    #     print(f"The text of the last item is: {last_item_text}")



    def parse_string(input_str):
        # Updated regular expression to allow for optional number
        match = re.match(r"(\w+)(?:\((\d+)\))?", input_str)
        if match:
            action = match.group(1)  # Captures the word
            number = int(match.group(2)) if match.group(2) else 0  # If no number, default to 0
            return (action, number)  # Return the tuple (action, number)
        else:
            return None  # Return None if no match is found
            
            
        



    def _test(self,something):
        print("Test command")
    
    def quit(self):
        self.driver.quit()

    





