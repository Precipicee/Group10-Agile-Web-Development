import unittest
import time
import warnings
import logging
import threading
import socket

from werkzeug.serving import make_server
from Fittrack import create_app, db
from Fittrack.config import TestingConfig

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logging.getLogger('selenium').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('werkzeug').setLevel(logging.ERROR)
warnings.filterwarnings("ignore", category=ResourceWarning)


class ServerThread:
    def __init__(self, app):
        self.app = app
        self.server = make_server('127.0.0.1', 5000, app)
        self.ctx = app.app_context()
        self.ctx.push()
        self.thread = threading.Thread(target=self.server.serve_forever)

    def start(self):
        self.thread.start()

    def shutdown(self):
        self.server.shutdown()
        self.thread.join()
        self.ctx.pop()


class BaseSystemTestCase(unittest.TestCase):
    BASE_URL = "http://127.0.0.1:5000"

    def setUp(self):
        self.testApp = create_app(TestingConfig)
        self.app_ctx = self.testApp.app_context()
        self.app_ctx.push()
        db.create_all()

        self.server = ServerThread(self.testApp)
        self.server.start()

        for _ in range(20):
            try:
                sock = socket.create_connection(("127.0.0.1", 5000), timeout=1)
                sock.close()
                break
            except socket.error:
                time.sleep(0.5)
        else:
            raise RuntimeError("Flask app did not start in time.")

        options = webdriver.ChromeOptions()
        options.add_argument('--headless=new')
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-features=PasswordManagerOnboarding,PasswordCheck")
        options.add_experimental_option("prefs", {
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False
        })
        self.driver = webdriver.Chrome(options=options)

        self.driver.get(f"{self.BASE_URL}/")
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        print("The page was loaded successfully for the first time.")

        super().setUp()

    def signup_user(self, username, password, email="test@example.com"):
        self.driver.get(f"{self.BASE_URL}/signin")
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.LINK_TEXT, "Sign Up"))).click()

        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "username")))
        self.driver.find_element(By.ID, "username").send_keys(username)
        self.driver.find_element(By.ID, "email").send_keys(email)
        self.driver.find_element(By.ID, "password").send_keys(password)
        self.driver.find_element(By.ID, "confirm").send_keys(password)
        submit_btn = self.driver.find_element(By.ID, "submit_btn")
        self.driver.execute_script("arguments[0].scrollIntoView(true);", submit_btn)
        self.driver.execute_script("arguments[0].click();", submit_btn)

        # Wait for the basicinfo page to be loaded
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "height")))

        # Use JavaScript to set all field values to ensure that the verification is passed.
        js_fill_form = """
        document.getElementById("avatar").value = "a.png";
        document.getElementById("birthday").value = "1990-01-01";
        document.getElementById("gender-0").checked = true;
        document.getElementById("height").value = "170";
        document.getElementById("current_weight").value = "70";
        document.getElementById("target_weight").value = "65";
        document.getElementById("target_weight_time_days").value = "30";
        document.getElementById("target_exercise_time_per_week").value = "150";
        document.getElementById("target_exercise_timeframe_days").value = "60";
        """
        self.driver.execute_script(js_fill_form)

        # Submit the form
        submit_btn = self.driver.find_element(By.ID, "submit_btn")
        self.driver.execute_script("arguments[0].click();", submit_btn)

        # Wait to jump back to the homepage (there is an "Upload" button on the homepage)
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.LINK_TEXT, "Upload"))
        )
        print("Successfully register and fill in the basic information")
        print("URL:", self.driver.current_url)


    def tearDown(self):
        self.server.shutdown()
        self.driver.quit()
        db.session.remove()
        db.drop_all()
        self.app_ctx.pop()
        return super().tearDown()
