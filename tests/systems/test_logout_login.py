from tests.system.test_base import BaseSystemTestCase
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class SigninTest(BaseSystemTestCase):
    def test_user_signin_flow(self):
        username = "testuser"
        password = "Testpass1"
        email = "testuser@example.com"

        # Registered users (including basicinfo and automatically jump to the home page)
        self.signup_user(username, password, email)
        print("Successfully registered and filled in basic information")

        # logout
        logout_link = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.LINK_TEXT, "Log Out"))
        )
        logout_link.click()

        # Sign In
        signin_link = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.LINK_TEXT, "Sign In"))
        )
        signin_link.click()

        # Fill in the login form
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "username"))
        )
        self.driver.find_element(By.ID, "username").send_keys(username)
        self.driver.find_element(By.ID, "password").send_keys(password)
        submit_btn = self.driver.find_element(By.ID, "submit_btn")
        self.driver.execute_script("arguments[0].click();", submit_btn)

        # After logging in, go back to the home page and check that the user name is displayed in the upper right corner.
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.LINK_TEXT, username))
        )
        print("Login successful, display user name:", username)
