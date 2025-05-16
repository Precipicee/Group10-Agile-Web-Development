from tests.system.test_base import BaseSystemTestCase
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class SignupTest(BaseSystemTestCase):
    def test_user_signup_flow(self):
        username = "testsignupuser"
        password = "StrongPass1!"
        email = "testsignupuser@example.com"

        # Step 1: Visit homepage
        self.driver.get(self.BASE_URL)

        # Step 2: Click Sign In
        signin_link = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Sign In"))
        )
        signin_link.click()

        # Step 3: On Sign In page, click Sign Up link
        signup_link = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Sign Up"))
        )
        signup_link.click()

        # Step 4: Fill out the Sign Up form
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "username"))
        )
        self.driver.find_element(By.ID, "username").send_keys(username)
        self.driver.find_element(By.ID, "email").send_keys(email)
        self.driver.find_element(By.ID, "password").send_keys(password)
        self.driver.find_element(By.ID, "confirm").send_keys(password)
        submit_btn = self.driver.find_element(By.ID, "submit_btn")
        self.driver.execute_script("arguments[0].click();", submit_btn)

        # Step 5: Fill out Basic Info
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "height"))
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
        self.driver.execute_script("arguments[0].click();", self.driver.find_element(By.ID, "submit_btn"))

        # Step 6: Verify we are redirected to homepage and user is logged in
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.LINK_TEXT, username))
        )
        self.assertIn(username, self.driver.page_source)
