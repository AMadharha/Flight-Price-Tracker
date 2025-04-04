from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from datetime import datetime
import time

class GoogleFlightBot:
    def __init__(self, chrome_driver_path, headless=False):
        """
        Initializes the Selenium WebDriver with specified options.

        Args:
            chrome_driver_path (str): Path to the Chrome WebDriver executable.

        Attributes:
            driver (webdriver.Chrome): The Selenium Chrome WebDriver instance.
            actions (ActionChains): An ActionChains instance for performing advanced user interactions.
        """
        # Options
        self.chrome_options = Options()
        if headless:
            self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--start-maximized")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument("--disable-gpu")

        # Initialize WebDriver
        self.service = Service(chrome_driver_path)

    def run(self, origin, destination, departure_dt, return_dt):
        """
        Searches for flights based on the given parameters and returns flight details.

        Args:
            origin (str): The departure airpot.
            destination (str): The arrival airport.
            departure_dt (str): The departure date in YYYY-MM-DD format.
            return_dt (str): The return date in YYYY-MM-DD format.

        Returns:
            tuple: A tuple containing:
                - departure_details (str): Flight details for the selected departure flight.
                - returning_details (str): Flight details for the selected return flight.
        """
        # Process date input
        departure_date = datetime.strptime(departure_dt, '%Y-%m-%d').strftime('%a, %b, %d')
        return_date = datetime.strptime(return_dt, '%Y-%m-%d').strftime('%a, %b, %d')

        self.driver = webdriver.Chrome(service=self.service, options=self.chrome_options)
        self.actions = ActionChains(self.driver)
        self.driver.get('https://www.google.com/travel/flights')

        # Input origin airport
        origin_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//input[@aria-label="Where from?"]'))
        )
        origin_input.clear()
        origin_input.send_keys(origin)

        time.sleep(1)
        origin_option = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, f'//li[contains(@aria-label, "{origin}")]'))
        )
        origin_option.click()

        # Input destination airport
        time.sleep(1)
        destination_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//input[@aria-label="Where to? "]'))
        )
        origin_input.clear()
        destination_input.send_keys(destination)

        time.sleep(1)
        destination_option = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, f'//li[contains(@aria-label, "{destination}")]'))
        )
        destination_option.click()

        # Input departure date
        time.sleep(1)
        departure_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//input[@aria-label="Departure"]'))
        )
        departure_input.clear()
        departure_input.send_keys(departure_date)

        # Click somewhere else
        time.sleep(1)
        flights_div = self.driver.find_element(By.XPATH, "//div[text()='Flights']")
        location = flights_div.location
        x = location['x']
        y = location['y']
        self.actions.move_by_offset(x, y).click().perform()
        self.actions.reset_actions()

        # Input return date
        time.sleep(1)
        return_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//input[@aria-label="Return"]'))
        )
        return_input.clear()
        return_input.send_keys(return_date)

        # Click somewhere else
        time.sleep(1)
        flights_div = self.driver.find_element(By.XPATH, "//div[text()='Flights']")
        location = flights_div.location
        x = location['x']
        y = location['y']
        self.actions.move_by_offset(x, y).click().perform()
        self.actions.reset_actions()

        # Search for flights
        time.sleep(1)
        search_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//button[@aria-label="Search"]'))
        )
        search_button.click()

        # Extract departure flight details
        time.sleep(1)
        departure_flight_divs = WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@aria-label, 'round trip total') and contains(@aria-label, 'Select flight')]"))
        )
        if departure_flight_divs:
            departure_details = departure_flight_divs[0].get_attribute("aria-label")

        # Click the departure flight
        time.sleep(1)
        self.driver.execute_script("window.scrollTo(0, 0);")
        window_size = self.driver.get_window_size()
        center_x = window_size["width"] // 2
        center_y = (window_size["height"] // 2) - 100
        self.actions.move_by_offset(center_x, center_y).click().perform()

        # Extract returning flight details
        time.sleep(1)
        returning_flight_divs = WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@aria-label, 'round trip total') and contains(@aria-label, 'Select flight')]"))
        )
        if returning_flight_divs:
            returning_details = returning_flight_divs[0].get_attribute("aria-label")

        self.driver.quit()

        return (departure_details, returning_details)