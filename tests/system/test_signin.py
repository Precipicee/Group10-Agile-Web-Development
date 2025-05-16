from .base import BaseSystemTestCase
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

class SignInTest(BaseSystemTestCase):
    def test_signin_process(self):
        self.signup_user("testuser", "Testpass1")
        self.driver.get("http://localhost:5000/signin")
        WebDriverWait(self.driver, 10).until(
            expected_conditions.element_to_be_clickable((By.ID, "username"))
        )
        self.driver.find_element(By.ID, "username").send_keys("testuser")
        self.driver.find_element(By.ID, "password").send_keys("Testpass1")
        submit_btn = self.driver.find_element(By.ID, "submit_btn")
        self.driver.execute_script("arguments[0].scrollIntoView(true);", submit_btn)
        self.driver.execute_script("arguments[0].click();", submit_btn)
        WebDriverWait(self.driver, 5).until(
            expected_conditions.presence_of_element_located((By.LINK_TEXT, "Log Out"))
        )
        self.assertIn("Log Out", self.driver.page_source)

    def test_signin_wrong_username(self):
        self.signup_user("testuser", "Testpass1")
        self.driver.get("http://localhost:5000/signin")
        WebDriverWait(self.driver, 10).until(
            expected_conditions.element_to_be_clickable((By.ID, "username"))
        )
        self.driver.find_element(By.ID, "username").send_keys("wronguser")
        self.driver.find_element(By.ID, "password").send_keys("Testpass1")
        submit_btn = self.driver.find_element(By.ID, "submit_btn")
        self.driver.execute_script("arguments[0].scrollIntoView(true);", submit_btn)
        self.driver.execute_script("arguments[0].click();", submit_btn)
        WebDriverWait(self.driver, 5).until(
            expected_conditions.presence_of_element_located((By.CLASS_NAME, "flash-message"))
        )
        self.assertIn("Invalid username or password", self.driver.page_source)

    def test_signin_wrong_password(self):
        self.signup_user("testuser", "Testpass1")
        self.driver.get("http://localhost:5000/signin")
        WebDriverWait(self.driver, 10).until(
            expected_conditions.element_to_be_clickable((By.ID, "username"))
        )
        self.driver.find_element(By.ID, "username").send_keys("testuser")
        self.driver.find_element(By.ID, "password").send_keys("Wrongpass1")
        submit_btn = self.driver.find_element(By.ID, "submit_btn")
        self.driver.execute_script("arguments[0].scrollIntoView(true);", submit_btn)
        self.driver.execute_script("arguments[0].click();", submit_btn)
        WebDriverWait(self.driver, 5).until(
            expected_conditions.presence_of_element_located((By.CLASS_NAME, "flash-message"))
        )
        self.assertIn("Invalid username or password", self.driver.page_source)

    # Not checking for empty fields as the WTForms library handles this, and they are set to "required" and hence cannot be tested server-side.