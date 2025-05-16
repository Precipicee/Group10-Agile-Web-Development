from .base import BaseSystemTestCase
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

class EditProfileTest(BaseSystemTestCase):
    def test_edit_profile(self):
        self.signup_user("edituser", "Editpass1", email="edituser@example.com")
        self.driver.get(f"{self.BASE_URL}/signin")
        self.driver.find_element(By.ID, "username").send_keys("edituser")
        self.driver.find_element(By.ID, "password").send_keys("Editpass1")
        submit_btn = self.driver.find_element(By.ID, "submit_btn")
        self.driver.execute_script("arguments[0].scrollIntoView(true);", submit_btn)
        self.driver.execute_script("arguments[0].click();", submit_btn)
        self.driver.get(f"{self.BASE_URL}/profile")

        WebDriverWait(self.driver, 10).until(
            expected_conditions.presence_of_element_located((By.ID, "profile-username"))
        )

        # Wait for the Edit button and click it
        WebDriverWait(self.driver, 10).until(
            expected_conditions.element_to_be_clickable((By.ID, "edit-profile-btn"))
        )
        edit_btn = self.driver.find_element(By.ID, "edit-profile-btn")
        edit_btn.click()

        # Wait for the height input to appear
        WebDriverWait(self.driver, 10).until(
            expected_conditions.presence_of_element_located((By.CSS_SELECTOR, "#profile-height input"))
        )

        # Fill out the fields
        height_input = self.driver.find_element(By.CSS_SELECTOR, "#profile-height input")
        height_input.clear()
        height_input.send_keys("180")

        weight_input = self.driver.find_element(By.CSS_SELECTOR, "#profile-weight-reg input")
        weight_input.clear()
        weight_input.send_keys("75")

        target_weight_input = self.driver.find_element(By.CSS_SELECTOR, "#profile-weight-target input")
        target_weight_input.clear()
        target_weight_input.send_keys("70")

        # Click the Save button (same button, now 💾)
        edit_btn.click()

        # Wait for the display mode to return and check updated values
        WebDriverWait(self.driver, 10).until(
            expected_conditions.text_to_be_present_in_element((By.ID, "profile-height"), "180")
        )
        self.assertIn("180", self.driver.find_element(By.ID, "profile-height").text)
        self.assertIn("75", self.driver.find_element(By.ID, "profile-weight-reg").text)
        self.assertIn("70", self.driver.find_element(By.ID, "profile-weight-target").text)
    
    def test_edit_profile_invalid_height(self):
        self.signup_user("edituser3", "Editpass1", email="edituser3@example.com")
        self.driver.get(f"{self.BASE_URL}/signin")
        self.driver.find_element(By.ID, "username").send_keys("edituser3")
        self.driver.find_element(By.ID, "password").send_keys("Editpass1")
        submit_btn = self.driver.find_element(By.ID, "submit_btn")
        self.driver.execute_script("arguments[0].scrollIntoView(true);", submit_btn)
        self.driver.execute_script("arguments[0].click();", submit_btn)
        self.driver.get(f"{self.BASE_URL}/profile")

        WebDriverWait(self.driver, 10).until(
            expected_conditions.element_to_be_clickable((By.ID, "edit-profile-btn"))
        )
        edit_btn = self.driver.find_element(By.ID, "edit-profile-btn")
        edit_btn.click()

        WebDriverWait(self.driver, 10).until(
            expected_conditions.presence_of_element_located((By.CSS_SELECTOR, "#profile-height input"))
        )
        height_input = self.driver.find_element(By.CSS_SELECTOR, "#profile-height input")
        height_input.clear()
        height_input.send_keys("abc")  # Invalid input

        edit_btn.click()

        # Check for error message (adjust selector/message as needed)
        WebDriverWait(self.driver, 5).until(expected_conditions.alert_is_present())
        alert = self.driver.switch_to.alert
        self.assertIn("Save failed", alert.text)  # Or check for a more specific message
        alert.accept()


    # Can be reworked to check for height too.
    def test_edit_profile_negative_weight(self):
        self.signup_user("edituser4", "Editpass1", email="edituser4@example.com")
        self.driver.get(f"{self.BASE_URL}/signin")
        self.driver.find_element(By.ID, "username").send_keys("edituser4")
        self.driver.find_element(By.ID, "password").send_keys("Editpass1")
        submit_btn = self.driver.find_element(By.ID, "submit_btn")
        self.driver.execute_script("arguments[0].scrollIntoView(true);", submit_btn)
        self.driver.execute_script("arguments[0].click();", submit_btn)
        self.driver.get(f"{self.BASE_URL}/profile")

        WebDriverWait(self.driver, 10).until(
            expected_conditions.element_to_be_clickable((By.ID, "edit-profile-btn"))
        )
        edit_btn = self.driver.find_element(By.ID, "edit-profile-btn")
        edit_btn.click()

        WebDriverWait(self.driver, 10).until(
            expected_conditions.presence_of_element_located((By.CSS_SELECTOR, "#profile-weight-reg input"))
        )
        weight_input = self.driver.find_element(By.CSS_SELECTOR, "#profile-weight-reg input")
        weight_input.clear()
        weight_input.send_keys("-10")  # Negative value

        edit_btn.click()

        # Wait for the input to disappear and display mode to return
        WebDriverWait(self.driver, 10).until_not(
            expected_conditions.presence_of_element_located((By.CSS_SELECTOR, "#profile-weight-reg input"))
        )

        # Now check the displayed value
        displayed_weight = self.driver.find_element(By.ID, "profile-weight-reg").text
        if "-10" in displayed_weight:
            self.fail("Negative weight was accepted, but should have been rejected.")