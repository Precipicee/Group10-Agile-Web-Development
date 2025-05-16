from tests.systems.test_base import BaseSystemTestCase
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

class UploadTest(BaseSystemTestCase):
    def test_upload_flow(self):
        username = "uploaduser"
        password = "Uploadpass1"
        email = "uploaduser@example.com"

        # Register and fill in the basic information
        self.signup_user(username, password, email)
        print("Successful registration ")
        print("URL:", self.driver.current_url)
        print("aftet registration：\n", self.driver.page_source[:500])

        # Click "Upload" in the navigation bar
        upload_link = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Upload"))
        )
        self.driver.execute_script("arguments[0].click();", upload_link)
        print("URL:", self.driver.current_url)


        # Wait for the Upload form to appear
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "recordForm"))
        )

        # Fill in the uploaded content
        self.driver.find_element(By.ID, "weight").clear()
        self.driver.find_element(By.ID, "weight").send_keys("68.2")
        self.driver.find_element(By.NAME, "breakfast").send_keys("Toast")
        self.driver.find_element(By.NAME, "lunch").send_keys("Noodles")
        self.driver.find_element(By.NAME, "dinner").send_keys("Salmon")
        self.driver.find_element(By.NAME, "exercise[]").send_keys("Jogging")
        self.driver.find_element(By.NAME, "duration[]").send_keys("30")
        self.driver.find_element(By.NAME, "intensity[]").send_keys("Moderate")

        submit_btn = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit'],.record__btn")
        self.driver.execute_script("arguments[0].click();", submit_btn)

        try:
            WebDriverWait(self.driver, 2).until(EC.alert_is_present())
            self.driver.switch_to.alert.accept()
        except TimeoutException:
            pass

        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "recordDetails"))
        )
        page_source = self.driver.page_source
        self.assertIn("Toast", page_source)
        self.assertIn("Noodles", page_source)
        self.assertIn("Salmon", page_source)
        self.assertIn("Jogging", page_source)
        print("Uploaded successfully, and the data is displayed correctly")
