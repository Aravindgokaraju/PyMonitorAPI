from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

def get_chrome_driver(headless=False):
    """
    Returns a configured Chrome WebDriver instance with automatic driver management
    
    Args:
        headless (bool): Whether to run in headless mode (no browser UI)
    
    Returns:
        webdriver.Chrome: Configured Chrome driver instance
    """
    # Set up Chrome options
    chrome_options = Options()
    
    # Common options
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-infobars')
    chrome_options.add_argument("--allow-insecure-localhost")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--no-sandbox")
    
    # Headless mode if specified
    if headless:
        chrome_options.add_argument("--headless=new")
    
    # Automatic driver management
    service = Service(ChromeDriverManager().install())
    
    # Initialize ChromeDriver
    return webdriver.Chrome(service=service, options=chrome_options)