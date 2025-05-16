import unittest
import time
import multiprocessing
import warnings
import logging

from Fittrack import create_app, db
from Fittrack.config import TestingConfig

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

logging.getLogger('selenium').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('werkzeug').setLevel(logging.ERROR)
warnings.filterwarnings("ignore", category=ResourceWarning)

class BaseSystemTestCase(unittest.TestCase):
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
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-features=PasswordManagerOnboarding,PasswordCheck")
        options.add_experimental_option("prefs", {
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False
        })
        self.driver = webdriver.Chrome(options=options)

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
        WebDriverWait(self.driver, 5).until(
            expected_conditions.url_changes("http://localhost:5000/signup")
        )
        self.complete_profile()
        logout_link = WebDriverWait(self.driver, 5).until(
            expected_conditions.element_to_be_clickable((By.LINK_TEXT, "Log Out"))
        )
        self.driver.execute_script("arguments[0].click();", logout_link)

    def complete_profile(self):
        WebDriverWait(self.driver, 10).until(
            expected_conditions.presence_of_element_located((By.ID, "height"))
        )
        self.driver.find_element(By.ID, "height").send_keys("170")
        self.driver.find_element(By.ID, "current_weight").send_keys("70")
        self.driver.find_element(By.ID, "target_weight").send_keys("65")
        self.driver.find_element(By.ID, "target_weight_time_days").send_keys("30")
        self.driver.find_element(By.ID, "target_exercise_time_per_week").send_keys("150")
        self.driver.find_element(By.ID, "target_exercise_timeframe_days").send_keys("60")
        self.driver.find_element(By.ID, "birthday").send_keys("01011990")
        self.driver.execute_script("arguments[0].click();", self.driver.find_element(By.ID, "gender-0"))
        self.driver.execute_script("arguments[0].value = 'a.png';", self.driver.find_element(By.ID, "avatar"))
        submit_btn = self.driver.find_element(By.ID, "submit_btn")
        self.driver.execute_script("arguments[0].scrollIntoView(true);", submit_btn)
        self.driver.execute_script("arguments[0].click();", submit_btn)

    def tearDown(self):
        self.server_thread.terminate()
        self.driver.close()
        db.session.remove()
        db.drop_all()
        self.app_ctx.pop()
        return super().tearDown()