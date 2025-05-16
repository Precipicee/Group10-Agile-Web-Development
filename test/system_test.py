import unittest
import time
import multiprocessing

from Fittrack import create_app, db
from Fittrack.models import User
from Fittrack.config import TestingConfig

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

import logging
import warnings

logging.getLogger('selenium').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('werkzeug').setLevel(logging.ERROR)
warnings.filterwarnings("ignore", category=ResourceWarning)

class SystemTestCase(unittest.TestCase):

    def setUp(self):
        testApp = create_app(TestingConfig)
        self.app_ctx = testApp.app_context()
        self.app_ctx.push()
        db.create_all()

        def run_app():
            testApp.run(use_reloader=False, port=5000, debug=False)

        self.server_thread = multiprocessing.Process(target=run_app)
        self.server_thread.start()

        options = webdriver.ChromeOptions()
        options.add_argument('--headless=new')
        options.add_experimental_option("prefs", {
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False
        })
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-features=PasswordManagerOnboarding,PasswordCheck")
        self.driver = webdriver.Chrome(options=options)
        #self.driver = webdriver.Chrome()


        super().setUp()
    
    def signup_user(self, username, password, email="test@example.com"):
        self.driver.get(f"{self.BASE_URL}/signup")

        WebDriverWait(self.driver, 10).until(
            expected_conditions.presence_of_element_located((By.ID, "username"))
        )
        self.driver.find_element(By.ID, "username").send_keys(username)
        self.driver.find_element(By.ID, "email").send_keys(email)
        self.driver.find_element(By.ID, "password").send_keys(password)
        self.driver.find_element(By.ID, "confirm").send_keys(password)
        submit_btn = self.driver.find_element(By.ID, "submit_btn")
        self.driver.execute_script("arguments[0].scrollIntoView(true);", submit_btn)
        self.driver.execute_script("arguments[0].click();", submit_btn)
        # Wait for redirect or confirmation
        WebDriverWait(self.driver, 5).until(
            expected_conditions.url_changes("http://localhost:5000/signup")
        )
        self.complete_profile()
        logout_link = WebDriverWait(self.driver, 5).until(
            expected_conditions.element_to_be_clickable((By.LINK_TEXT, "Log Out"))
        )
        self.driver.execute_script("arguments[0].click();", logout_link)

    def complete_profile(self):
        # Wait for the profile completion page to load (adjust selectors as needed)
        WebDriverWait(self.driver, 10).until(
            expected_conditions.presence_of_element_located((By.ID, "height"))
        )
        self.driver.find_element(By.ID, "height").send_keys("170")
        self.driver.find_element(By.ID, "current_weight").send_keys("70")
        self.driver.find_element(By.ID, "target_weight").send_keys("65")
        self.driver.find_element(By.ID, "target_weight_time_days").send_keys("30")
        self.driver.find_element(By.ID, "target_exercise_time_per_week").send_keys("150")
        self.driver.find_element(By.ID, "target_exercise_timeframe_days").send_keys("60")
        
        # Fill in date of birth (adjust ID if needed)
        self.driver.find_element(By.ID, "birthday").send_keys("01011990")  # Format may need to be YYYY-MM-DD or DD/MM/YYYY

        # Select gender (assuming radio buttons with IDs like gender-male, gender-female, etc.)
        gender_radio = self.driver.find_element(By.ID, "gender-0")
        self.driver.execute_script("arguments[0].click();", gender_radio)

        # Pick an avatar (assuming hidden input with id="avatar" and clickable images)
        avatar_input = self.driver.find_element(By.ID, "avatar")
        self.driver.execute_script("arguments[0].value = 'a.png';", avatar_input)
        # Optionally, click the avatar image if required:
        # avatar_img = self.driver.find_element(By.CSS_SELECTOR, "img[src*='a.png']")
        # self.driver.execute_script("arguments[0].click();", avatar_img)

        
        # Add other required fields as needed
        submit_btn = self.driver.find_element(By.ID, "submit_btn")
        self.driver.execute_script("arguments[0].scrollIntoView(true);", submit_btn)
        self.driver.execute_script("arguments[0].click();", submit_btn)
    
    def test_homepage_loads(self):
        self.driver.get("http://localhost:5000/")
        WebDriverWait(self.driver, 10).until(
            expected_conditions.presence_of_element_located((By.TAG_NAME, "body"))
        )
        self.assertIn("FitTrack", self.driver.title)

    # Example: test sign in page loads
    def test_signin_process(self):
        self.signup_user("testuser", "Testpass1")
        self.driver.get("http://localhost:5000/signin")
        WebDriverWait(self.driver, 10).until(
            expected_conditions.element_to_be_clickable((By.ID, "username"))
        )

        username_field = self.driver.find_element(By.ID, "username")
        username_field.send_keys("testuser")
        
        # Wait until password field is interactable
        WebDriverWait(self.driver, 5).until(
            expected_conditions.element_to_be_clickable((By.ID, "password"))
        )
        password_field = self.driver.find_element(By.ID, "password")
        password_field.send_keys("Testpass1")

        # Scroll submit button into view and click
        submit_btn = self.driver.find_element(By.ID, "submit_btn")
        self.driver.execute_script("arguments[0].scrollIntoView(true);", submit_btn)
        self.driver.execute_script("arguments[0].click();", submit_btn)

        # Wait for redirect after login (adjust URL as needed)
        WebDriverWait(self.driver, 5).until(
            expected_conditions.url_contains("/")
        )
        WebDriverWait(self.driver, 5).until(
            expected_conditions.presence_of_element_located((By.LINK_TEXT, "Log Out"))
        )
        self.assertIn("Log Out", self.driver.page_source)

    def tearDown(self):
        self.server_thread.terminate()
        self.driver.close()
        db.session.remove()
        db.drop_all()
        self.app_ctx.pop()
        return super().tearDown()

if __name__ == '__main__':
    unittest.main()