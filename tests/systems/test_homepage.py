from tests.system.test_base import BaseSystemTestCase
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

class HomepageTest(BaseSystemTestCase):
    def test_homepage_loads(self):
        self.driver.get("http://127.0.0.1:5000/")
        WebDriverWait(self.driver, 10).until(
            expected_conditions.presence_of_element_located((By.TAG_NAME, "body"))
        )
        self.assertIn("FitTrack", self.driver.title)
