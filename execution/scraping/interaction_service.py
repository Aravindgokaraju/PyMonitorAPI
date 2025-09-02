# import random
# import re
# import time
# import undetected_chromedriver as uc  # Add this import
# from typing import List, Union
# from bs4 import BeautifulSoup
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.remote.webelement import WebElement
# from selenium.common.exceptions import TimeoutException
# from execution.browser_config.stable_config import StableConfig
# from execution.browser_config.stealth_config import StealthConfig



# #NO GLOBAL CRITERIA, CRITERIA SHOULD BE PASSED IN FROM MAIN NOT STORED AS A GLOBAL HERE TO BE USED BY THE FUNCTIONS

# class InteractionService:

#     #TODO:  Use Firefox with resistFingerprinting=true
#     # Install CanvasBlocker extension
#     # Disable WebGL (about:config → webgl.disabled)

#     def __init__(self, stealth_level='stable'):
#         # Choose configuration based on stealth level
#         if stealth_level == 'stealth':
#             self.config = StealthConfig()
#         else:
#             self.config = StableConfig()
            
#         # Apply configurations
#         if isinstance(self.config, StableConfig):
#             self.driver = self.config.create_driver()
#         else:
#             self.driver = uc.Chrome(
#             options=self.chrome_options,
#             headless=False,
#             use_subprocess=True,
#             version_main=114  # Optional: specify Chrome version
#             )
#             self.config._apply_stealth_measures(self.driver)
        
#         # Apply additional stealth measures if using stealth config
#         if isinstance(self.config, StealthConfig):
#             self.config._apply_stealth_measures()
            
#         self.action = ActionChains(self.driver)
    




#     def _initialize_function_map(self):
#             return {
#                 'open_site': self._open_website,
#                 'go_back': self._go_back,
#                 'basic_click': self._click,
#                 'strong_click': self._strong_click,
#                 'enter_string': self._enter_string,
#                 'test_command': self._test,
#                 'scroll_view': self._scroll_into_view,
#                 # 'fast_find': self._find_element,
#                 # 'fast_find_multiple': self._find_elements,
#                 'wait_find': self._wait_for_element_presence,
#                 'wait_click': self._wait_for_element_clickable,
#                 # 'wait_find_self': self._wait_find_self,
#                 'smart_find':self.smart_find,
#                 'print_text': self._print_text,
#                 'add_to_table': self._get_price,
#                 'sleep': self._sleep,
#                 'debug_print': self._debug,
#             }





# # FUNDAMENTAL FUNCTIONS

#     #DEBUG FUNCTIONS
#     def _sleep(self,criterion):
#         time.sleep(10000)

#     def _debug(self,criterion):
#         print("DEBUG COMMAND")

#     # OPEN WEBSITE
#     def _open_website(self, websiteURL):
#         """Opens a given website using the driver."""
#         print(f"Opening website: {websiteURL}")
#         self.driver.get(websiteURL)
#         print(f"Current URL: {self.driver.current_url}")
    



#     #TODO: See if I need to pass in criteria or if I can just pass in xpath
#     #WAIT FIND ELEMENT
#     #redundant
#     def _wait_for_element_presence(self, nextPath):
#         """waits until the desired element gets detected"""
#         return WebDriverWait(self.driver, 10).until(
#             EC.presence_of_element_located((By.XPATH, nextPath))
#         )
       
#     #WAIT TIL ELEMENT CLICKABLE
#     #TODO: same as wait find but passing in path?
#     def _wait_for_element_clickable(self, nextPath):
#         """waits until the desired element gets marked as clickable"""
#         return WebDriverWait(self.driver, 10).until(
#             EC.element_to_be_clickable((By.XPATH, nextPath))
#         )


    
        
#     def smart_find(self, criteria_dict, locator, parent_element=None, timeout=10):
#         """
#         Consolidated find function that tries:
#         1. Wait-based global find first
#         2. Wait-based local find (if parent provided)
#         3. Returns None if neither succeeds
        
#         Args:
#             locator: XPath string (should work for both global and local)
#             parent_element: Optional parent WebElement for local search
#             timeout: Maximum wait time in seconds
        
#         Returns:
#             WebElement if found, None otherwise
#         """
#         def _wait_find(search_context, xpath):
#             try:
#                 print("search context, ",search_context)
#                 print("xpath, ",xpath)
#                 print("smartfind timeout",timeout)
#                 return WebDriverWait(search_context, timeout).until(
#                     EC.presence_of_element_located((By.XPATH, xpath)))
#             except TimeoutException:
#                 print("TimeOut Exception on FInd")
#                 return None
#         print("global find")
#         # First try global find
#         element = _wait_find(self.driver, locator)
#         if element:
#             print("ELEMENT FOUND locator:",locator)
#             return element
#         print("local find find")
        
#         # If global fails and parent provided, try local find
#         if parent_element is not None:
#             # Convert to local XPath if not already
#             local_locator = locator if locator.startswith('.') else f'.{locator}'
#             print("ELEMENT FOUND local_locator:",local_locator)

#             return _wait_find(parent_element, local_locator)
        
#         return None
        
#     # GO BACK
#     def _go_back(self):
#         self.driver.back()


#     def smart_find_elements(self, locator, parent_element=None, timeout=10):
#         """
#         Consolidated find elements function that tries:
#         1. Wait-based global find first
#         2. Wait-based local find (if parent provided)
#         3. Returns empty list if neither succeeds
        
#         Args:
#             locator: XPath string (should work for both global and local)
#             parent_element: Optional parent WebElement for local search
#             timeout: Maximum wait time in seconds
            
#         Returns:
#             List of WebElements if found, empty list otherwise
#         """
#         def _wait_find_elements(search_context, xpath):
#             try:
#                 # Wait for at least one element to be present
#                 WebDriverWait(search_context, timeout).until(
#                     EC.presence_of_element_located((By.XPATH, xpath)))
#                 # Then return all matching elements
#                 return search_context.find_elements(By.XPATH, xpath)
#             except TimeoutException:
#                 return []
                
#         # First try global find
#         elements = _wait_find_elements(self.driver, locator)
#         if elements:
#             return elements
            
#         # If global fails and parent provided, try local find
#         if parent_element is not None:
#             # Convert to local XPath if not already
#             local_locator = locator if locator.startswith('.') else f'.{locator}'
#             return _wait_find_elements(parent_element, local_locator)
        
#         return []

# # SELENIUM FUNCTIONS

#     # SELENIUM CLICK
#     def _click(self,criterion):
#         webElement = criterion.webElement
#         webElement.click()

#     # ENTER VALUE INTO TEXTBOX AND SUBMIT
#     def _enter_string(self,criterion, skuString):
#         webElement = criterion.webElement
#         webElement.send_keys(skuString)
#         self.action.send_keys(Keys.RETURN).perform()
    
#     def _print_text(self,criterion):
#         webElement = criterion.webElement
#         print("Printing text",webElement.text)

#     def _get_price(self,criterion):
        
#         webElement = criterion.webElement
#         ans = self.extract_price(webElement.text)
#         print("Appending Data ",ans)
#         if(ans):
#             return ans
#         else: return -1

#     def extract_price(self,text):
#         # Regular expression to match price patterns (e.g., $123.45, €123, 123.45)
#         match = re.search(r'\b[$€£]?\d+(?:\.\d{1,2})?\b', text)
#         if match:
#             # Remove currency symbols and convert to float
#             return float(match.group().lstrip('$€£'))
#         return None


# # ALERT CLOSING FUNCTIONS
    
#     # #CLOSE JAVASCRIPT ALERT
#     # def _close_alert(self):
#     #     try:
#     #         alert = self.driver.switch_to.alert
#     #         alert_text = alert.text
#     #         print(f"Alert text: {alert_text}")
#     #         alert.dismiss()  # or alert.accept() to confirm
#     #     except :
#     #         print("No alert present on the page.")

#     # #BASIC IFRAME REMOVAL TODO GO IN DEPTH LATER IF NEEDED
#     # def _close_iframe(self,criterion):
#     #     path = criterion.xpath
#     #     self.driver.switch_to.default_content()
#     #     # Use JavaScript to remove the iframe
#     #     iframe_id = path  # Replace with the actual ID or selector of the iframe
#     #     self.driver.execute_script(f"document.getElementById('{iframe_id}').remove();")

    
    

# # JAVASCRIPT HARD FUNCTIONS

#     # JAVASCRIPT CLICK
#     def _strong_click(self, target):
#         """
#         Enhanced click method that accepts either:
#         - Criteria object (containing webElement)
#         - Direct WebElement reference
        
#         Args:
#             target: Either a Criteria object or WebElement
#         """
#         # Extract WebElement based on input type
#         web_element = target.webElement if hasattr(target, 'webElement') else target
        
#         # Verify we have a valid WebElement
#         if not isinstance(web_element, WebElement):
#             raise TypeError("Target must be either Criteria object or WebElement")
        
#         try:
#             # First attempt regular click
#             web_element.click()
#         except Exception as e:
#             # Fallback to JavaScript click
#             try:
#                 self.driver.execute_script("arguments[0].click();", web_element)
#             except Exception as js_e:
#                 raise Exception(f"Both native and JS click failed: {str(e)} -> {str(js_e)}")

#     def _scroll_into_view(self,criterion):
#         webElement = criterion.webElement
#         self.driver.execute_script("arguments[0].scrollIntoView(true);", webElement)

    
#     # FOR ALERTS
#     def _force_remove(self,criterion):
#         self.driver.execute_script("document.querySelector('" + criterion.xpath + "').style.display = 'none';")


#     #HOOMAN Update
#     def human_type(element, text):
#         """Type like a human (with delays and mistakes)"""
#         for char in text:
#             element.send_keys(char)
#             time.sleep(random.uniform(0.05, 0.2))  # Random typing speed

#     def human_click(self,element):
#         """Move mouse erratically before clicking"""
#         action = ActionChains(self.driver)
#         action.move_to_element_with_offset(element, random.randint(-5,5), random.randint(-5,5))
#          # Add micro-jitter (1-3 random small movements)
#         for _ in range(random.randint(1, 3)):
#             action.move_by_offset(
#                 random.randint(-2, 2),
#                 random.randint(-2, 2)
#             ).pause(random.uniform(0.05, 0.1))

#         action.move_to_element(element)  # Correct to exact position
#         action.pause(random.uniform(0.2, 1.0))
#         action.click()
#         action.perform()

#     def human_scroll(self, element=None):
#         """Simulates human scrolling with variable speed and pauses"""
#         if element:
#             # Scroll to element with jitter
#             self.driver.execute_script(
#                 f"window.scrollBy(0, {random.randint(-50, 50)});"  # Initial jitter
#             )
#             time.sleep(random.uniform(0.1, 0.3))
#             self.driver.execute_script(
#                 "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
#                 element
#             )
#         else:
#             # Random scroll with momentum effect
#             scroll_px = random.randint(200, 800)
#             for chunk in range(3, 0, -1):
#                 partial_scroll = scroll_px // chunk
#                 self.driver.execute_script(
#                     f"window.scrollBy(0, {partial_scroll});"
#                 )
#                 time.sleep(random.uniform(0.1, 0.5))  # Decreasing pauses
        
#         # Post-scroll micro-movements
#         for _ in range(random.randint(1, 2)):
#             self.driver.execute_script(
#                 f"window.scrollBy(0, {random.randint(-15, 15)});"
#             )
#             time.sleep(random.uniform(0.05, 0.15))
        
#         # Final reading pause
#         time.sleep(random.uniform(0.5, 2.0)) 
    
#     def human_read_with_scroll(self, element):
#         # Scroll element into view naturally
#         self.driver.execute_script(
#             "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
#             element
#         )
#         time.sleep(random.uniform(0.8, 1.5))
        
#         # Read with human-like delays
#         return self.human_read(element, min_delay=0.2, max_delay=0.7)

#     def human_read(
#         element_or_html: Union['WebElement', str],
#         tag: str = None,
#         class_: str = None,
#         min_delay: float = 0.1,
#         max_delay: float = 0.5,
#         line_delay: bool = True,
#         jitter: bool = True
#     ) -> Union[str, List[str]]:
#         """
#         Simulates human-like text reading behavior using BeautifulSoup.
        
#         Args:
#             element_or_html: Selenium WebElement or raw HTML string
#             tag: Specific HTML tag to focus on (e.g., 'div', 'span')
#             class_: CSS class to filter by
#             min_delay: Minimum delay between chunks (seconds)
#             max_delay: Maximum delay between chunks
#             line_delay: Whether to add extra delay for line breaks
#             jitter: Randomize delay times within range
            
#         Returns:
#             Extracted text as string or list of paragraphs
#         """
#         # Convert input to HTML string
#         if hasattr(element_or_html, 'get_attribute'):
#             html = element_or_html.get_attribute('outerHTML')
#         else:
#             html = str(element_or_html)
        
#         # Parse with BeautifulSoup
#         soup = BeautifulSoup(html, 'html.parser')
        
#         # Targeted extraction
#         if tag or class_:
#             css_selector = tag or ''
#             if class_:
#                 css_selector += f'.{class_.replace(" ", ".")}'
#             elements = soup.select(css_selector)
#             if not elements:
#                 return ""
#             soup = elements[0]
        
#         # Remove unwanted elements
#         for unwanted in soup(['script', 'style', 'noscript', 'svg']):
#             unwanted.decompose()
        
#         # Get clean text with natural line breaks
#         text = soup.get_text(separator='\n', strip=True)
        
#         # Simulate reading behavior
#         lines = [line for line in text.split('\n') if line.strip()]
#         result = []
        
#         for line in lines:
#             # Add word-by-word delay
#             words = line.split()
#             for i, word in enumerate(words):
#                 # Skip delays for very short words
#                 if len(word) > 3:
#                     delay = random.uniform(min_delay, max_delay) if jitter else (min_delay + max_delay)/2
#                     time.sleep(delay * (0.5 if i % 3 == 0 else 1))  # Varied rhythm
                
#                 result.append(word + (' ' if i < len(words)-1 else ''))
            
#             if line_delay:
#                 time.sleep(random.uniform(min_delay*1.5, max_delay*2))
        
#         # Return as single string or list of paragraphs
#         return ' '.join(result) if len(lines) < 3 else lines
    
#     def _read_xpath_string(self,criterion):
#         webElement = criterion.webElement
#         print(webElement.text)
            
    

#     def parse_string(input_str):
#         # Updated regular expression to allow for optional number
#         match = re.match(r"(\w+)(?:\((\d+)\))?", input_str)
#         if match:
#             action = match.group(1)  # Captures the word
#             number = int(match.group(2)) if match.group(2) else 0  # If no number, default to 0
#             return (action, number)  # Return the tuple (action, number)
#         else:
#             return None  # Return None if no match is found
            
            
    



#     def _test(self,something):
#         print("Test command")
    
#     def quit(self):
#         self.driver.quit()

    





