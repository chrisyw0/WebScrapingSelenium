import time
import requests
import os
from nis import cat
from xml.dom.minidom import Element
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import *
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
from multiprocessing.connection import wait

class WebScrapper():
    """
    This is the base class of doing web scraping
    """
    def __init__(self, url, image_path=None, out_path=None, out_file=None):
        """
        Constructor
        Parameters
        ----------
        url: str
            the url
        image_path: str
            the path that you want to save the image
        out_path: str
            the path that you want to save the raw data file
        out_file: str
            the file name for the raw data file
        """

        print(url, image_path, out_path, out_file)

        self.url = url
        self.driver = webdriver.Chrome(ChromeDriverManager().install())

        self.option = Options()
        self.option.headless = True

        if not image_path.endswith("/"):
            image_path += "/"

        self.image_path = image_path

        if not out_path.endswith("/"):
            out_path += "/"

        self.out_path = out_path
        self.out_file = out_file
        
        print("Result scraper class created")
        print("================================================")
        print(f"URL {self.url}")
        print(f"Image path {self.image_path}")
        print(f"Raw data file {self.out_path + self.out_file}")
        print("================================================")

    def process(self):
        """
        Please write your own function in the subclass
        """
        pass

    def load_url(self, wait_seconds=10, wait_until=None):
        """
        Ask Chrome to open the url and wait the accept cookies button appear

        Parameters
        ----------
        wait_seconds: int
            The number of seconds should be waited
        wait_until: any conditions from class EC
            The expected condition should be waiting for. For example: EC.element_to_be_clickable

        See Also
        ----------
        get_expected_condition_element_clickable: get expected class object for an element to be clickable
        
        """
        self.driver.get(self.url)

        if wait_until:
            wait = WebDriverWait(self.driver, wait_seconds, poll_frequency=1)
            wait.until(wait_until)

    def get_EC_element_clickable(self, xpath=None, class_name=None, element_id=None, css_selector=None):
        """
        A helper class to get an element to be clickable object, 
        either one of xpath, class, id or css selector should be inputed to get the element

        Parameters
        ------------
        xpath: str
            xpath of the element
        class_name: str
            class name of the element
        element_id: str
            element ID of the element
        css_selector: str
            CSS selector of the element

        Returns
        -------------
        element_to_be_clickable
            element to be clickable class searching by either xpath, class, id or css selector

        """

        until = None 

        if xpath:
            until = EC.element_to_be_clickable((By.XPATH, xpath))
        elif class_name:
            until = EC.element_to_be_clickable((By.CLASS_NAME, class_name))
        elif element_id:
            until = EC.element_to_be_clickable((By.ID, element_id))
        elif css_selector:
            until = EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector))

        return until

    def get_EC_element_presence(self, xpath=None, class_name=None, element_id=None, css_selector=None):
        """
        A helper class to get an element to be located object, 
        either one of xpath, class, id or css selector should be inputed to get the element

        Parameters
        ------------
        xpath: str
            xpath of the element
        class_name: str
            class name of the element
        element_id: str
            element ID of the element
        css_selector: str
            CSS selector of the element

        Returns
        -------------
        presence_of_element_located
            element to be located class searching by either xpath, class, id or css selector

        """
        until = None 

        if xpath:
            until = EC.presence_of_element_located((By.XPATH, xpath))
        elif class_name:
            until = EC.presence_of_element_located((By.CLASS_NAME, class_name))
        elif element_id:
            until = EC.presence_of_element_located((By.ID, element_id))
        elif css_selector:
            until = EC.presence_of_element_located((By.CSS_SELECTOR, css_selector))

        return until
    
    def get_EC_window_open(self):
        """
        A helper class to get an EC object for a window is opened, 
        
        Returns
        -------------
        new_window_is_opened
            new window is opened EC object

        """
        handles = self.driver.window_handles
        return EC.new_window_is_opened(handles)

    def wait_until(self, until, wait_secounds=10):
        """
        Ask Selenium to wait for something happen in some seconds 

        Parameters
        ------------
        until: any EC
            Any object from expected condition (EC) class
        wait_seconds: int
            number of seconds to be waited
        
        """
        wait = WebDriverWait(self.driver, wait_secounds, poll_frequency=1).until(until)

    def move_to_element(self, xpath=None, element_class=None, element_id=None, css_selector=None):
        """
        Scroll to element

        Parameters
        ------------
        xpath: str
            xpath of the element
        class_name: str
            class name of the element
        element_id: str
            element ID of the element
        css_selector: str
            CSS selector of the element
        """

        action = ActionChains(self.driver)
        element = self.get_web_element(xpath=xpath, element_class=element_class, element_id=element_id, css_selector=css_selector)
        
        if element:
            action.move_to_element(element).perform()

    def get_number_of_windows(self):
        """
        Get number of windows opened

        Returns
        ------------
        int
            number of active windows
        """

        return len(self.driver.window_handles)

    def switch_to_new_window(self, window_pos=-1):
        """
        Switch to new window

        Parameters
        ------------
        window_pos: int
            window position, 0 means current window, 1 means next window, -1 means the last window
        
        """
        self.driver.switch_to.window(self.driver.window_handles[-1])

    def close_current_window(self):
        """
        Close current window
        """
        self.driver.close()
        
    def get_web_element(self, parent=None, xpath=None, element_id=None, element_class=None, css_selector=None):
        """
        Get an element by either xpath, element id, class or css selector 
        from a element (parent) or the root element

        If the element doesn't exist or attach to the web element, it simpliy return None

        Parameters
        ------------
        parent: WebElement
            Parent element, will search from root element if not specified
        xpath: str
            xpath of the element
        class_name: str
            class name of the element
        element_id: str
            element ID of the element
        css_selector: str
            CSS selector of the element

        Returns
        -------------
        WebElement
            element to be located under parent or the root web element

        See Also
        -------------
        get_web_elements: if you look for a list of web elements

        """

        element = None

        if parent is None:
            parent = self.driver
        
        try: 
            if xpath:
                element = parent.find_element(By.XPATH, xpath)
            elif element_id:
                element = parent.find_element(By.ID, element_id)
            elif element_class:
                element = parent.find_element(By.CLASS_NAME, element_class)
            elif css_selector:
                element = parent.find_element(By.CSS_SELECTOR, css_selector)
        except (NoSuchElementException, StaleElementReferenceException) as e:
            print(e)

        return element
    
    def get_web_elements(self, parent=None, xpath=None, element_id=None, element_class=None, css_selector=None):
        """
        Get elements by either xpath, element id, class or css selector 
        from a element (parent) or the root element.

        If the element doesn't exist or attach to the web element, it simpliy return None

        Parameters
        ------------
        parent: WebElement
            Parent element, will search from root element if not specified
        xpath: str
            xpath of the element
        class_name: str
            class name of the element
        element_id: str
            element ID of the element
        css_selector: str
            CSS selector of the element

        Returns
        -------------
        List of WebElement
            elements to be located under parent or the root web element

        See Also
        -------------
        get_web_element: if you look for a single web elements

        """

        elements = None

        if parent is None:
            parent = self.driver
        
        try:
            if xpath:
                elements = parent.find_elements(By.XPATH, xpath)
            elif element_id:
                elements = parent.find_elements(By.ID, element_id)
            elif element_class:
                elements = parent.find_elements(By.CLASS_NAME, element_class)
            elif css_selector:
                elements = parent.find_elements(By.CSS_SELECTOR, css_selector)

        except (NoSuchElementException, StaleElementReferenceException) as e:
            print(e)

        return elements

    def click_button(self, parent=None, xpath=None, element_id=None, element_class=None, css_selector=None, retry=0):
        """
        Click an URL or button by searching either xpath, element id, class or 
        css selector from a parent class or root element

        Parameters
        ------------
        parent: WebElement
            Parent element, will search from root element if not specified
        xpath: str
            xpath of the element
        class_name: str
            class name of the element
        element_id: str
            element ID of the element
        css_selector: str
            CSS selector of the element

        Returns 
        ------------
        bool:
            Whether the button or URL is clicked
        
        See Also
        -------------
        get_web_element: for how the element being searched

        """
        
        button = self.get_web_element(parent=parent, xpath=xpath, element_id=element_id, element_class=element_class, css_selector=css_selector)
        
        if button:
            try:
                button.click()
                return True
            except WebDriverException as e:
                print(e)

        return False
    
    def stop_scraping(self):
        """
        Simpliy close the web driver and release the resource
        """
        self.driver.quit()

    @staticmethod
    def download_image(url, img_path, file_name=None):
        """
        Download a image from an URL and save to the path
        
        Parameters
        ------------
        url: str
            URL of the image
        img_path: str
            path to store the image
        file_name: str
            file name for the downloaded image

        Returns 
        ------------
        str:
            Local file name if the image is downloaded successfully or None if unable to download

        """

        local_filename = file_name if file_name else url.split('/')[-1]
        try: 
            with requests.get(url, stream=True) as r:
                r.raise_for_status()

                os.makedirs(img_path, exist_ok=True)

                with open(img_path + local_filename, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192): 
                        f.write(chunk)

                return local_filename
        except Exception as e:
            print(e)
        
        return None
