import requests
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import *
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.remote.webelement import WebElement
from typing import Optional, Any, Tuple, List

class WebScrapper():
    """
    This is the base class of doing web scraping
    """
    def __init__(self, url : str, image_path : str = None, out_path : str = None, out_file : str = None, force_capture : bool = False, is_testing : bool = False) -> None:
        """
        Constructor
        Parameters
        ----------
        url: str
            The url
        image_path: str
            The path that you want to save the image
        out_path: str
            The path that you want to save the raw data file
        out_file: str
            The file name for the raw data file
        force_capture: bool
            Capture the races that have already existed in the database 
        is_testing: bool
            Whether the process is run in testing mode
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

        self.force_capture = force_capture
        self.is_testing = is_testing
        
        print("Result scraper class created")
        print("================================================")
        print(f"URL {self.url}")
        print(f"Image path {self.image_path}")
        print(f"Raw data file {self.out_path + self.out_file}")
        print("================================================")

    def process(self) -> None:
        """
        Please write your own function in the subclass
        """
        pass

    def load_url(self, wait_seconds : int = 10, wait_until : Any = None) -> None:
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

    def get_EC_element_clickable(self, xpath : str = None, element_class : str = None, element_id : str = None) -> Optional[EC.element_to_be_clickable]:
        """
        A helper class to get an element to be clickable object, 
        either one of xpath, class or id should be inputed to get the element

        Parameters
        ------------
        xpath: str
            xpath of the element
        element_class: str
            class name of the element
        element_id: str
            element ID of the element

        Returns
        -------------
        element_to_be_clickable
            element to be clickable class searching by either xpath, class or id

        """

        until = None 

        if xpath:
            until = EC.element_to_be_clickable((By.XPATH, xpath))
        elif element_class:
            until = EC.element_to_be_clickable((By.CLASS_NAME, element_class))
        elif element_id:
            until = EC.element_to_be_clickable((By.ID, element_id))

        return until

    def get_EC_element_presence(self, xpath : str = None, element_class : str = None, element_id : str = None) -> Optional[EC.element_to_be_clickable]:
        """
        A helper class to get an element to be located object, 
        either one of xpath, class or id should be inputed to get the element

        Parameters
        ------------
        xpath: str
            xpath of the element
        element_class: str
            class name of the element
        element_id: str
            element ID of the element

        Returns
        -------------
        presence_of_element_located
            element to be located class searching by either xpath, class or id

        """
        until = None 

        if xpath:
            until = EC.presence_of_element_located((By.XPATH, xpath))
        elif element_class:
            until = EC.presence_of_element_located((By.CLASS_NAME, element_class))
        elif element_id:
            until = EC.presence_of_element_located((By.ID, element_id))

        return until
    
    def get_EC_window_open(self) -> EC.new_window_is_opened:
        """
        A helper class to get an EC object for a window is opened, 
        
        Returns
        -------------
        new_window_is_opened
            new window is opened EC object

        """
        handles = self.driver.window_handles
        return EC.new_window_is_opened(handles)

    def wait_until(self, until : Any, wait_secounds : int = 10) -> None:
        """
        Ask Selenium to wait for something happen in some seconds 

        Parameters
        ------------
        until: any EC
            Any object from expected condition (EC) class
        wait_seconds: int
            number of seconds to be waited
        
        """
        WebDriverWait(self.driver, wait_secounds, poll_frequency=1).until(until)

    def move_to_element(self, xpath : str = None, element_class : str = None, element_id : str = None)  -> None:
        """
        Scroll to element

        Parameters
        ------------
        xpath: str
            xpath of the element
        element_class: str
            class name of the element
        element_id: str
            element ID of the element
        """

        action = ActionChains(self.driver)
        element = self.get_web_element(xpath=xpath, element_class=element_class, element_id=element_id)
        
        if element:
            action.move_to_element(element).perform()

    def get_number_of_windows(self) -> int:
        """
        Get number of windows opened

        Returns
        ------------
        int
            number of active windows
        """

        return len(self.driver.window_handles)

    def switch_to_new_window(self, window_pos : int = -1) -> None:
        """
        Switch to new window

        Parameters
        ------------
        window_pos: int
            window position, 0 means current window, 1 means next window, -1 means the last window
        
        """
        self.driver.switch_to.window(self.driver.window_handles[window_pos])

    def close_current_window(self) -> None:
        """
        Close current window
        """
        self.driver.close()
        
    def get_web_element(self, parent : WebElement = None, xpath : str = None, element_id : str = None, element_class : str = None) -> Optional[WebElement]:
        """
        Get an element by either xpath, element id or class 
        from a element (parent) or the root element

        If the element doesn't exist or attach to the web element, it simpliy return None

        Parameters
        ------------
        parent: WebElement
            Parent element, will search from root element if not specified
        xpath: str
            xpath of the element
        element_id: str
            element ID of the element
        element_class: str
            class name of the element

        Returns
        -------------
        Optional[WebElement]
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

        except (NoSuchElementException, StaleElementReferenceException) as e:
            print(e)

        return element
    
    def get_web_elements(self, parent : WebElement = None, xpath : str = None, element_id : str = None, element_class : str = None) -> Optional[List[WebElement]]:
        """
        Get elements by either xpath, element id or class
        from a element (parent) or the root element.

        If the element doesn't exist or attach to the web element, it simpliy return None

        Parameters
        ------------
        parent: WebElement
            Parent element, will search from root element if not specified
        xpath: str
            xpath of the element
        element_id: str
            element ID of the element
        element_class: str
            class name of the element

        Returns
        -------------
        Optional[list(WebElement)]
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

        except (NoSuchElementException, StaleElementReferenceException) as e:
            print(e)

        return elements

    def click_button(self, parent : WebElement = None, xpath : str = None, element_id : str = None, element_class : str = None) -> Tuple[bool, Optional[WebElement]]:
        """
        Click an URL or button by searching either xpath, element id or class
         from a parent class or root element

        Parameters
        ------------
        parent: WebElement
            Parent element, will search from root element if not specified
        xpath: str
            xpath of the element
        element_id: str
            element ID of the element
        element_class: str
            class name of the element

        Returns 
        ------------
        Tuple[bool, Optional[WebElement])]:
            First bool value indicate whether the button or URL is clicked, Second value is the button
            If failed to click the button, the second value will be None
        
        See Also
        -------------
        get_web_element: for how the element being searched

        """
        
        button = self.get_web_element(parent=parent, xpath=xpath, element_id=element_id, element_class=element_class)
        
        if button:
            try:
                button.click()
                return True, button
            except (WebDriverException, ElementClickInterceptedException) as e:
                print(e)

        return False, None
    
    def stop_scraping(self) -> None:
        """
        Simpliy close the web driver and release the resource
        """
        self.driver.quit()

    @staticmethod
    def download_image(url : str, img_path : str, file_name : str = None) -> str:
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

        try: 
            local_filename = file_name if file_name else url.split('/')[-1]
            
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
