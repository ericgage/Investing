from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium_stealth import stealth
import time

class BrowserSession:
    def __init__(self):
        self.driver = None
        
    def get(self, url):
        """Get a webpage"""
        if not self.driver:
            # Set up Chrome options for headless mode
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            
            # Initialize headless Chrome
            self.driver = webdriver.Chrome(options=options)
            
            # Apply stealth settings
            stealth(self.driver,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True,
            )
            
        self.driver.get(url)
        time.sleep(1)  # Small delay to ensure page loads
        
    @property
    def page_source(self):
        """Get the current page source"""
        if not self.driver:
            return None
        return self.driver.page_source
        
    def close(self):
        """Close the browser session"""
        if self.driver:
            self.driver.quit()
            self.driver = None 