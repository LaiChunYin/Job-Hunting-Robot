from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import re
import logging
import pandas as pd
import logging
from job_websites.job_website import JobWebsite

logger = logging.getLogger(__name__)


class Linkedin(JobWebsite):
    def __init__(self, driver, email, password, searching_criteria_dict, filter_criteria_dict, url = "https://www.linkedin.com/", existing_jobs_path = "resources/jobs.csv"):
        super().__init__(driver, url, email, password, searching_criteria_dict, filter_criteria_dict, existing_jobs_path)

    
    def login(self):
        logger.debug("loggin in ")
        logger.debug(f"login window 2  {self.driver.current_window_handle}, {self.driver.window_handles}")
        signInBtn = self.wait_short.until(EC.visibility_of_element_located((By.XPATH, f"//a[contains(text(), 'Sign in')]")))
        # signInBtn = self.wait_short.until(EC.visibility_of_element_located((By.LINK_TEXT, f"Sign In")
        logger.debug(f"sign btn is {signInBtn.tag_name}")
        signInBtn.click()

        # logging in Indeed
        google_login_btn = self.wait_short.until(EC.visibility_of_element_located((By.XPATH, f"//*[contains(text(), 'Continue with Google')]")))
        google_login_btn.click()

        # logging in Google
        # go to the google pop up window
        # Store the window handle of the original window
        original_window = self.driver.current_window_handle

        # Switch to the new window
        logger.debug(f"windows {len([window for window in self.driver.window_handles if window != original_window])}")
        logger.debug(f"window 1 {self.driver.current_window_handle}, {self.driver.window_handles}")
        new_window = self.driver.window_handles[-1]
        self.driver.switch_to.window(new_window)
        logger.debug(f"window 2 {self.driver.window_handles}")

        email_input = self.wait_short.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "input[type=email]")))
        email_input.send_keys(self.email)
        email_input.send_keys(Keys.RETURN)
        logger.debug(f"window 2 {self.driver.current_window_handle}, {self.driver.window_handles}")

        password_input = self.wait_short.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "input[aria-label='Enter your password']")))
        logger.debug(f"password input  {password_input.tag_name}")
        password_input.send_keys(self.password)
        password_input.send_keys(Keys.RETURN)
        logger.debug(f"window 3  {self.driver.current_window_handle}, {self.driver.window_handles}")

        # the Google login page will be closed automatically
        self.wait_long.until(EC.number_of_windows_to_be(1), "login timeout")
        self.driver.switch_to.window(original_window)
        logger.debug(f"window 5  {self.driver.current_window_handle}, {self.driver.window_handles}")





    def searchJobs(self, searching_criteria_dict = {}, filter_criteria_dict = {}):
        pass

    def get_job_description(self, job_link = None):
        """
        Scrap the job information from the current page
        """
        logger.debug(f"getting job desc {job_link}")
        if job_link:
            logger.debug(f"has job link {self.driver.current_window_handle}, {self.driver.window_handles}")
            self.driver.switch_to.window(self.handle)
            self.driver.get(job_link)
            logger.debug(f"after get link {self.driver.current_window_handle}, {self.driver.window_handles}")

        job_desc_html = self.wait_short.until(EC.visibility_of_element_located((By.CLASS_NAME, "jobs-description__container"))).get_attribute("innerHTML")
        directApply = False

        job_id_match = re.search("jobid=\d*", self.driver.current_url, flags = re.IGNORECASE)
        logger.debug(f"job id match is {job_id_match}")
        if job_id_match:
            logger.debug("from job search")
            job_id = job_id_match.group().split("=")[-1]
            logger.debug(f"linkedin job id: {job_id}")

            company = self.wait_short.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".job-details-jobs-unified-top-card__primary-description-container .app-aware-link"))).get_attribute("innerText")
            position = self.wait_short.until(EC.visibility_of_element_located((By.CLASS_NAME, "job-details-jobs-unified-top-card__job-title-link"))).get_attribute("innerText").split("\n")[0]
            # sometimes job may not exist in the collection page
            job = self.wait_short.until(EC.presence_of_element_located((By.CSS_SELECTOR, f"div[data-job-id='{job_id}']")), "job id timeout")
            logger.debug(f"job is {job}")
            if job:
                address = job.find_element(By.CLASS_NAME, "job-card-container__metadata-item").get_attribute("innerText").split(" (")[0]
            else:
                address = self.wait_short.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".jobs-unified-top-card .job-details-jobs-unified-top-card__bullet"))).get_attribute("innerText").split(" (")[0]
            logger.debug(f"job address is {address}")
            
        else:
            logger.debug("from saved jobs")
            company = self.wait_short.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".job-details-jobs-unified-top-card__primary-description-without-tagline a"))).get_attribute("innerText")
            position = self.wait_short.until(EC.visibility_of_element_located((By.CLASS_NAME, "job-details-jobs-unified-top-card__job-title"))).get_attribute("innerText").split("\n")[0]
            address = self.wait_short.until(EC.visibility_of_element_located((By.CLASS_NAME, "jobs-unified-top-card__bullet"))).get_attribute("innerText").split(" (")[0]
        logger.debug(f"company: {company}, position: {position}, address: {address}")

        try:
            if job_id_match:
                apply_btn_locator = (By.CSS_SELECTOR, "button[aria-label^='Easy Apply to']")
            else:
                apply_btn_locator = (By.CSS_SELECTOR, ".jobs-unified-top-card button[aria-label^='Easy Apply to']")
            self.wait_short.until(EC.visibility_of_element_located(apply_btn_locator))
            logger.debug("apply btn %s", apply_btn_locator)
            directApply = True
            apply_link = self.driver.current_url
            logger.debug("direct apply and link %s, %s", directApply, apply_link)
        except Exception as e:
            logger.debug("cannot apply directly")
            if job_id_match:
                apply_btn_locator = (By.CSS_SELECTOR, "button[aria-label^='Apply to']")
            else:
                apply_btn_locator = (By.CSS_SELECTOR, ".jobs-unified-top-card button[aria-label^='Apply to']")

            self.wait_short.until(EC.visibility_of_element_located(apply_btn_locator))
            apply_link = self.driver.current_url
            logger.debug("apply link is %s", apply_link)
            
        # Check if the primary key of the new row exists in the DataFrame
        if job_link is None and (self.jobs[self.primary_keys] == pd.DataFrame([{"company": company, "position": position}])).all(axis = 1).any():
            print("same key")
            return None
        
        return {
            "company": company,
            # position obtained from the html has the format {position}\n-job post
            "position": position,
            "address": address,
            "desciptionHtml": job_desc_html,
            "link": self.driver.current_url,
            "address_from_Internet": None,
            "directApply": directApply, # apply on Linkedin directly
            "apply_link": apply_link, # for Linkedin jobs, link should be the same as apply_link
            "applied": False
        }

    def scan_jobs(self, num_of_jobs = 10):
       pass



    def apply(self, jobs = None, manualCheck = True):
        pass
    

    def interactive_mode(self, url_format = "https:\/\/.*linkedin.com\/jobs\/(search|view|collections)", apply = False):
        super().interactive_mode(url_format, apply)



