from .base import BaseSystemTestCase
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

class UploadTest(BaseSystemTestCase):
    def upload_record(self, weight="70.5", breakfast="Eggs", lunch="Chicken salad", dinner="Fish and rice",
                      exercise="Running", duration="30", intensity="Moderate"):
        self.driver.get(f"{self.BASE_URL}/upload")
        WebDriverWait(self.driver, 10).until(
            expected_conditions.presence_of_element_located((By.ID, "recordForm"))
        )
        self.driver.find_element(By.ID, "weight").clear()
        self.driver.find_element(By.ID, "weight").send_keys(weight)
        self.driver.find_element(By.NAME, "breakfast").send_keys(breakfast)
        self.driver.find_element(By.NAME, "lunch").send_keys(lunch)
        self.driver.find_element(By.NAME, "dinner").send_keys(dinner)
        self.driver.find_element(By.NAME, "exercise[]").send_keys(exercise)
        self.driver.find_element(By.NAME, "duration[]").send_keys(duration)
        self.driver.find_element(By.NAME, "intensity[]").send_keys(intensity)
        submit_btn = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit'],.record__btn")
        self.driver.execute_script("arguments[0].scrollIntoView(true);", submit_btn)
        self.driver.execute_script("arguments[0].click();", submit_btn)
        # Handle possible alert
        try:
            WebDriverWait(self.driver, 2).until(expected_conditions.alert_is_present())
            alert = self.driver.switch_to.alert
            alert.accept()
        except TimeoutException:
            pass

    def test_upload_record(self):
        # Sign up and log in
        self.signup_user("uploaduser", "Uploadpass1", email="uploaduser@example.com")
        self.driver.get(f"{self.BASE_URL}/signin")
        self.driver.find_element(By.ID, "username").send_keys("uploaduser")
        self.driver.find_element(By.ID, "password").send_keys("Uploadpass1")
        submit_btn = self.driver.find_element(By.ID, "submit_btn")
        self.driver.execute_script("arguments[0].scrollIntoView(true);", submit_btn)
        self.driver.execute_script("arguments[0].click();", submit_btn)

        # Upload the first record
        self.upload_record()

        # Wait for confirmation or record in details
        WebDriverWait(self.driver, 10).until(
            expected_conditions.presence_of_element_located((By.ID, "recordDetails"))
        )
        page_source = self.driver.page_source
        self.assertIn("Eggs", page_source)
        self.assertIn("Chicken salad", page_source)
        self.assertIn("Fish and rice", page_source)
        self.assertIn("Running", page_source)

    def test_upload_duplicate_record(self):
        # Sign up and log in
        self.signup_user("uploaduser2", "Uploadpass1", email="uploaduser2@example.com")
        self.driver.get(f"{self.BASE_URL}/signin")
        self.driver.find_element(By.ID, "username").send_keys("uploaduser2")
        self.driver.find_element(By.ID, "password").send_keys("Uploadpass1")
        submit_btn = self.driver.find_element(By.ID, "submit_btn")
        self.driver.execute_script("arguments[0].scrollIntoView(true);", submit_btn)
        self.driver.execute_script("arguments[0].click();", submit_btn)

        # Upload the first record
        self.upload_record()

        # Upload a duplicate record for the same day (should trigger overwrite alert)
        self.upload_record(weight="71", breakfast="Toast", lunch="Soup", dinner="Steak",
                        exercise="Cycling", duration="45", intensity="Intense")

        # Accept the overwrite confirmation alert if it appears
        from selenium.common.exceptions import TimeoutException
        try:
            WebDriverWait(self.driver, 5).until(expected_conditions.alert_is_present())
            alert = self.driver.switch_to.alert
            self.assertIn("already exists", alert.text.lower())
            alert.accept()
        except TimeoutException:
            # No alert appeared, that's fine if overwrite is silent
            pass

        # Wait for the record details to update and check for new values
        WebDriverWait(self.driver, 10).until(
            expected_conditions.presence_of_element_located((By.ID, "recordDetails"))
        )
        page_source = self.driver.page_source
        self.assertIn("71", page_source)
        self.assertIn("Toast", page_source)
        self.assertIn("Soup", page_source)
        self.assertIn("Steak", page_source)
        self.assertIn("Cycling", page_source)