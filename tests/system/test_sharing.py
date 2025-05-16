from .base import BaseSystemTestCase
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import TimeoutException

class SharingTest(BaseSystemTestCase):
    def signup(self, username, password, email):
        self.signup_user(username, password, email)

    def login(self, username, password):
        self.driver.get(f"{self.BASE_URL}/signin")
        WebDriverWait(self.driver, 10).until(
            expected_conditions.presence_of_element_located((By.ID, "username"))
        )
        self.driver.find_element(By.ID, "username").send_keys(username)
        self.driver.find_element(By.ID, "password").send_keys(password)
        submit_btn = self.driver.find_element(By.ID, "submit_btn")
        self.driver.execute_script("arguments[0].scrollIntoView(true);", submit_btn)
        self.driver.execute_script("arguments[0].click();", submit_btn)

    def test_share_report(self):
        # Register two users
        self.signup("shareuser1", "Sharepass1", email="shareuser1@example.com")
        self.signup("shareuser2", "Sharepass2", email="shareuser2@example.com")

        # User1 logs in and sends a friend request to user2
        self.login("shareuser1", "Sharepass1")
        self.driver.get(f"{self.BASE_URL}/friends")
        WebDriverWait(self.driver, 10).until(
            expected_conditions.presence_of_element_located((By.ID, "friend-username"))
        )
        self.driver.find_element(By.ID, "friend-username").send_keys("shareuser2")
        send_btn = self.driver.find_element(By.ID, "btn-send-request")
        self.driver.execute_script("arguments[0].scrollIntoView(true);", send_btn)
        self.driver.execute_script("arguments[0].click();", send_btn)

        # Log out user1
        self.driver.get(f"{self.BASE_URL}/logout")

        # User2 logs in and accepts the friend request
        self.login("shareuser2", "Sharepass2")
        self.driver.get(f"{self.BASE_URL}/friends")
        WebDriverWait(self.driver, 10).until(
            expected_conditions.presence_of_element_located((By.CLASS_NAME, "btn-accept"))
        )
        self.driver.find_element(By.CLASS_NAME, "btn-accept").click()

        try:
            WebDriverWait(self.driver, 2).until(expected_conditions.alert_is_present())
            alert = self.driver.switch_to.alert
            alert.accept()
        except TimeoutException:
            pass

        # Log out user2
        self.driver.get(f"{self.BASE_URL}/logout")

        # User1 logs in, uploads a record, and shares the report with user2
        self.login("shareuser1", "Sharepass1")
        self.driver.get(f"{self.BASE_URL}/upload")
        WebDriverWait(self.driver, 10).until(
            expected_conditions.presence_of_element_located((By.ID, "recordForm"))
        )
        self.driver.find_element(By.ID, "weight").clear()
        self.driver.find_element(By.ID, "weight").send_keys("65")
        self.driver.find_element(By.NAME, "breakfast").send_keys("Oats")
        self.driver.find_element(By.NAME, "lunch").send_keys("Salad")
        self.driver.find_element(By.NAME, "dinner").send_keys("Chicken")
        self.driver.find_element(By.NAME, "exercise[]").send_keys("Jogging")
        self.driver.find_element(By.NAME, "duration[]").send_keys("20")
        self.driver.find_element(By.NAME, "intensity[]").send_keys("Moderate")
        submit_btn = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit'],.record__btn")
        self.driver.execute_script("arguments[0].scrollIntoView(true);", submit_btn)
        self.driver.execute_script("arguments[0].click();", submit_btn)
        
        try:
            WebDriverWait(self.driver, 2).until(expected_conditions.alert_is_present())
            alert = self.driver.switch_to.alert
            alert.accept()
        except TimeoutException:
            pass

        WebDriverWait(self.driver, 10).until(
            expected_conditions.presence_of_element_located((By.ID, "recordDetails"))
        )

        # Go to reports page and share the report
        self.driver.get(f"{self.BASE_URL}/visualise")
        self.driver.get(f"{self.BASE_URL}/visualise")
        WebDriverWait(self.driver, 10).until(
            expected_conditions.element_to_be_clickable((By.ID, "btn-weight"))
        )
        self.driver.find_element(By.ID, "btn-weight").click()

        # Now wait for the share button on the weight report page
        WebDriverWait(self.driver, 10).until(
            expected_conditions.presence_of_element_located((By.CLASS_NAME, "btn-share"))
        )
        share_btn = self.driver.find_element(By.CLASS_NAME, "btn-share")
        self.driver.execute_script("arguments[0].scrollIntoView(true);", share_btn)
        self.driver.execute_script("arguments[0].click();", share_btn)

        WebDriverWait(self.driver, 10).until(
            expected_conditions.presence_of_element_located((By.NAME, "receiver_id"))
        )
        select = self.driver.find_element(By.NAME, "receiver_id")
        for option in select.find_elements(By.TAG_NAME, "option"):
            if option.text == "shareuser2":
                option.click()
                break
        submit_btn = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        self.driver.execute_script("arguments[0].scrollIntoView(true);", submit_btn)
        self.driver.execute_script("arguments[0].click();", submit_btn)

        # Log out user1
        self.driver.get(f"{self.BASE_URL}/logout")

        # User2 logs in and checks for the shared report
        self.login("shareuser2", "Sharepass2")
        self.driver.get(f"{self.BASE_URL}/shared_reports")
        WebDriverWait(self.driver, 10).until(
            expected_conditions.presence_of_element_located((By.CLASS_NAME, "shared-report-card"))
        )
        page_source = self.driver.page_source
        self.assertIn("shareuser1", page_source)
        self.assertIn("report", page_source.lower())