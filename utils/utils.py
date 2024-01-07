import logging
import time
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logger = logging.getLogger(__name__)

class Utils: 
    translate_to_lower_case = "translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')"

    @staticmethod
    def wait_for_human_verification(msg = "Please check the current page before proceeding to the next step."):
        logger.info(msg)

        while True:
            user_input = input(
                "Enter 'y' if you have verified the page, or 'n' to check again: ").lower()

            if user_input == 'y':
                logger.info("Continuing with the automation process...")
                break
            elif user_input == 'n':
                logger.warning("Waiting for you to complete the human verification...")
                time.sleep(5)  # You can adjust the waiting time as needed
            else:
                logger.error("Invalid input. Please enter 'y' or 'n'.")

    @staticmethod
    def is_element_exist(driver, by, value, timeout = 3):
        try:
            logger.debug("in is element exist")
            return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, value)))
        except Exception as e:
            logger.debug(f"in find_element {e}")
            return False
