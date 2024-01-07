from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time

# from selenium_stealth import stealth
import undetected_chromedriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from utils.utils import Utils
from selenium.webdriver.common.action_chains import ActionChains

import numpy as np
import logging
from config.config import Config

logger = logging.getLogger(__name__)
class ChatGPTAutomation:
    _instance = None
    def __new__(cls, *arg):
        logger.debug("chat gpt __new__")
        if cls._instance is None:
            logger.debug("new chatgpt instance")
            cls._instance = super(ChatGPTAutomation, cls).__new__(cls)
        return cls._instance

    def __init__(self, driver = None, mode = "chatGPT", version = 4, plugins = [], use_same_converation = True):
        """
        Open chatGpt in a new window if the mode is set as "chatGPT"
        Will support using API Key in the future
        """

        self.user_data_dir = "/Users/macbook/Library/Application Support/Google/Chrome/Default/"

        # Dont go to chat.openai.com directly. It will be blocked by CloudFlare
        # url = r"https://chat.openai.com"
        url = r"https://openai.com/"

        #----------
        use_different_version_or_plugins = False
        if (not hasattr(self, "version") or not hasattr(self, "plugins")) or (self.version != version or set(self.plugins) != set(plugins)):
            self.version = version
            self.plugins = plugins
            use_different_version_or_plugins = True
            

        if hasattr(self, "handle"):
            logger.debug(f"reusing old chat gpt window {self.handle}")
            self.driver.switch_to.window(self.handle)

            # chatgpt.change_chatgpt_version("plugin", plugins=["WebPilot"])
            if not use_same_converation or (use_different_version_or_plugins):
                self.change_chatgpt_version(self.version, self.plugins)
        else:
            if isinstance(driver, undetected_chromedriver.Chrome):
                logger.debug("gpt using existing driver")
                self.driver = driver
                num_of_windows = len(self.driver.window_handles)
                logger.debug(f"original windows {self.driver.window_handles}")

                self.driver.switch_to.new_window("tab")
                logger.debug(f"gpt windows {self.driver.window_handles}")
                self.wait_short.until(EC.number_of_windows_to_be(num_of_windows + 1), "chat gpt window now opened")
                logger.debug("window opened")
                self.driver.switch_to.window(self.driver.window_handles[-1])
            else:
                self.driver = self.setup_undetected_webdriver()

            self.wait_short = WebDriverWait(self.driver, 3)
            self.wait_medium = WebDriverWait(self.driver, 10)
            self.wait_long = WebDriverWait(self.driver, 120)
            
            logger.debug(f"handles:  {self.driver.current_window_handle}, {self.driver.window_handles}")
            time.sleep(1)
            self.driver.get(url)
            time.sleep(5)
            self.wait_short.until(EC.visibility_of_element_located((By.LINK_TEXT, "Log in"))).click()

            # Clicking the Log in button directly will trigger the bot detection
            log_in = self.wait_short.until(EC.visibility_of_element_located((By.LINK_TEXT, "Log in")))
            x = log_in.location['x']
            y = log_in.location['y']
            # Optionally, you can consider the size of the element
            width = log_in.size['width']
            height = log_in.size['height']
            logger.debug(f"width: {width}, height: {height}")
            # Coordinates to click (for example, the center of the element)
            click_x = x + width / 2
            click_y = y + height / 2

            ActionChains(self.driver).move_by_offset(click_x, click_y).click(0).perform()

            time.sleep(3)  # need this to bypass bot detection, dont know why

            self.driver.switch_to.window(self.driver.window_handles[-1])

            self.handle = self.driver.current_window_handle
            logger.debug(f"creating new chat gpt window {self.handle}, {self.driver.window_handles}")


            # logging in OpenAI
            try:
                email = Config.CHATGPT_EMAIL
                password = Config.CHATGPT_PASSWORD
                self.google_login(email, password)
                # select between ChatGPT and API modes
                go_to_chatgpt_btn = self.wait_medium.until(EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'ChatGPT')]")))
                self.wait_medium.until(EC.element_to_be_clickable(go_to_chatgpt_btn))
                go_to_chatgpt_btn.click()

                # login ChatGPT
                login_btn = self.wait_medium.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "button[data-testid=login-button]")))
                login_btn.click()

                # OpenAI requires login for the second time
                self.google_login(email, password)
            except:
                Utils.wait_for_human_verification("Cannot login in automatically. Please open a new tab, and then login to ChatGPT manually. Make sure that ChatGPT is opened in the latest window")
                self.handle = self.driver.window_handles[-1]
                self.driver.switch_to.window(self.handle)

            # self.change_chatgpt_version("plugin", plugins=["WebPilot"])
            self.change_chatgpt_version(self.version, self.plugins)


    def change_chatgpt_version(self, version = 4, plugins = []):
        """
        create a new conversation window that uses the specified GPT version and plugins
        """
        if version != 3.5 or version != 4 or version != "plugins":
            logger.debug("version must be either 3.5, 4 or plugin. Use 4 as default now")
            version = 4

        # version_menu_btn = self.wait_medium.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "[class=text-token-text-tertiary]")))
        version_menu_btn = self.wait_medium.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "main [aria-haspopup=menu]")))
        version_menu_btn.click()

        if "plugin" in str(version).lower():
            version_btn = self.wait_short.until(EC.visibility_of_element_located((By.XPATH, f"//*[contains(text(), 'Plugins')]")))

            if len(plugins) > 3:
                logger.debug("Maximum number of plugins is 3")
            else:
                plugins_menu = self.driver(By.ID, "headlessui-listbox-button-:rj:")
                plugins_menu.click()

                # unselect all exisiting plugins (the ticked plugins)
                existing_plugins = self.wait_medium.until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "#headlessui-listbox-options-:r20: rect[fill=currentColor]")))
                logger.debug(f"unselecting {len(existing_plugins)}")
                for plugin_btn in existing_plugins:
                    plugin_btn.click()

                # selected plugins
                logger.debug(f"selecting {plugins}")
                for plugin_name in plugins:
                    plugin_btn = self.wait_short.until(EC.visibility_of_element_located((By.XPATH, f"//*[@id, 'headlessui-listbox-options-:r20:']//span[contains({Utils.translate_to_lower_case}, '{plugin_name}')]")))
                    logger.debug("plugin btn found")
                    plugin_btn.click()
        else:
            version_btn = self.wait_short.until(EC.visibility_of_element_located((By.XPATH, f"//*[contains(text(), 'GPT-{str(version)}')]")))

        version_btn.click()

    def ask(self, question, wait_time=1):
        input_box = self.wait_short.until(EC.visibility_of_element_located((By.ID, "prompt-textarea")))
        sentences = question.split('\n')
        logger.debug(f"asking question {question}, {sentences}")
        # sending return or \n directly will send question to GPT)
        for sentence in sentences:
            input_box.send_keys(sentence)
            input_box.send_keys(Keys.LEFT_SHIFT + Keys.RETURN)
        input_box.send_keys(Keys.RETURN) # send the question
        time.sleep(wait_time)  # wait the text to be fully pasted
        
        # the send button becomes stop generate button when a response is being generated
        self.wait_long.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid=send-button]")), "Generation timeout")
        time.sleep(2) # sometimes the last sentence cannot be printed out without this line
        response = []
        response = self.wait_medium.until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "[data-testid*=conversation-turn-] [data-message-author-role*=assistant]")))
        return response[-1].get_attribute("innerText") if len(response) > 0 else None
    

    def setup_undetected_webdriver(self):
        # options = undetected_chromedriver.ChromeOptions() 
        driver = undetected_chromedriver.Chrome() 
        # driver.maximize_window() 
        return driver


    def quit(self):
        """ Closes the browser and terminates the WebDriver session."""
        logger.debug("Closing the browser...")
        self.driver.close()
        self.driver.quit()


    def google_login(self, email, password):
        google_login = self.wait_short.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "button[data-provider=google]")))
        google_login.click()

        # sometimes Google may ask you to choose from a existing account
        logger.debug("try existing")
        existing_account_locator = (By.XPATH, f"//*[contains(text(), '{Config.CHATGPT_EMAIL}')]")
        existing_account_btn = Utils.is_element_exist(self.driver, *existing_account_locator, timeout=10)

        if existing_account_btn:
            existing_account_btn.click()
            logger.debug("existing clicked")
        else:
            # sometimes Google ask for the email and password
            logger.debug("not existing found")
            email_box = self.wait_short.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "input[type=email]")))
            email_box.send_keys(email)
            email_box.send_keys(Keys.RETURN)

            time.sleep(2) # app crashes without this line
            pwd_box = self.wait_short.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "input[type=password]")))
            logger.debug(f"pwd box {pwd_box}")
            pwd_box.send_keys(password)
            pwd_box.send_keys(Keys.RETURN)

        # self.wait_for_human_verification()

