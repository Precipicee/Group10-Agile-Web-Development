from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from tests.systems.test_base import BaseSystemTestCase


class FriendTest(BaseSystemTestCase):
    def test_add_and_accept_friend(self):
        # Register the first account
        self.signup_user("user1", "Password123", "user1@example.com")
        print("user1 registration successful")

        # user1
        logout_btn = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Log Out"))
        )
        self.driver.execute_script("arguments[0].click();", logout_btn)
        print("User1 successfully logged out")

        # second accout
        self.signup_user("user2", "Password123", "user2@example.com")
        print("user2 registration successful")

        # Friends 
        friends_link = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Friends"))
        )
        self.driver.execute_script("arguments[0].click();", friends_link)

        print("URL:", self.driver.current_url)
        # Send a friend request
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "friend-username")))
        self.driver.find_element(By.ID, "friend-username").send_keys("user1")
        self.driver.find_element(By.ID, "btn-send-request").click()

        try:
            WebDriverWait(self.driver, 5).until(EC.alert_is_present())
            alert = self.driver.switch_to.alert
            print(f"Friend request prompt：{alert.text}")
            alert.accept()
        except TimeoutException:
            print("No prompt window detected")
        print("URL:", self.driver.current_url)

        # user2 logout
        logout_btn = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Log Out"))
        )
        self.driver.execute_script("arguments[0].click();", logout_btn)
        print("User2 successfully logged out")

        #  user1 login
        self.driver.get(f"{self.BASE_URL}/signin")
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "username")))
        self.driver.find_element(By.ID, "username").send_keys("user1")
        self.driver.find_element(By.ID, "password").send_keys("Password123")
        self.driver.find_element(By.ID, "submit_btn").click()

        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.LINK_TEXT, "Friends"))
        )


        # Friends
        friends_link = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Friends"))
        )
        self.driver.execute_script("arguments[0].click();", friends_link)

        # Accept the friend request
        try:
            accept_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "btn-accept"))
            )
            self.driver.execute_script("arguments[0].click();", accept_btn)
            WebDriverWait(self.driver, 5).until(EC.alert_is_present())
            alert = self.driver.switch_to.alert
            print(f"Accept the friend request：{alert.text}")
            alert.accept()
        except TimeoutException:
            print("No acceptance button or prompt detected")

        # Verify that the friend has been added successfully
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.ID, "friends-list-container"))
        )
        page = self.driver.page_source
        self.assertIn("user2", page)
        print("User2 successfully appeared in user1's friend list")
