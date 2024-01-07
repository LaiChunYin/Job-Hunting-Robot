from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from utils.utils import Utils
import logging
import pandas as pd
from form_auto_filler.form_auto_filler import FormAutoFiller
import logging
from job_websites.job_website import JobWebsite
import re

logger = logging.getLogger(__name__)

class Indeed(JobWebsite):
    def __init__(self, driver, email, password, searching_criteria_dict, filter_criteria_dict, url = "https://ca.indeed.com", existing_jobs_path = "resources/jobs.csv"):
        super().__init__(driver, url, email, password, searching_criteria_dict, filter_criteria_dict, existing_jobs_path)

    def login(self):
        logger.debug("loggin in ")
        logger.debug(f"login window 2  {self.driver.current_window_handle}, {self.driver.window_handles}")
        signInBtn = self.wait_short.until(EC.visibility_of_element_located((By.XPATH, f"//a[contains(text(), 'Sign in')]")))
        logger.debug(f"sign btn is {signInBtn.tag_name}")
        signInBtn.click()

        # logging in Indeed
        email_input = self.wait_short.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "input[type=email]")))
        email_input.send_keys(self.email)
        email_input.send_keys(Keys.RETURN)

        google_login_btn = self.wait_short.until(EC.visibility_of_element_located((By.ID, "login-google-button")))
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
        self.wait_long.until(EC.number_of_windows_to_be(1), "Indeed login timeout")
        self.driver.switch_to.window(original_window)
        logger.debug(f"window 5  {self.driver.current_window_handle}, {self.driver.window_handles}")



    def searchJobs(self, searching_criteria_dict = {}, filter_criteria_dict = {}):
        """
        Set the searching criteria and click the search button
        """
        logger.debug("searching for jobs......")
        # make sure that it is on the job searching page
        home_page_btn = self.wait_short.until(EC.visibility_of_element_located((By.ID, "FindJobs")))
        home_page_btn.click()

        # make the filters appear first
        find_jobs_btn = self.wait_short.until(EC.visibility_of_element_located((By.XPATH, f"//button[contains(text(), 'Find jobs')]")))
        find_jobs_btn.click()

        keywords_input = self.wait_short.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "input[placeholder*='Job title, keywords, or company']")))

        logger.debug(f"keyword input  {keywords_input.tag_name}")
        logger.debug(f"keyword  {searching_criteria_dict['keywords'] if 'keywords' in searching_criteria_dict else None}")

        location_input = self.wait_short.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "input[placeholder*='City, province']")))

        time.sleep(1)  # cannot input keywords and location without this
        keywords_input.send_keys(searching_criteria_dict["keywords"] if "keywords" in searching_criteria_dict else "")
        time.sleep(0.5)
        location_input.click()
        time.sleep(0.5)
        # need to delete the original location first. Using clear() does not work
        self.wait_short.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "button[aria-label*='Clear location input']"))).click()
        time.sleep(0.5)
        location_input.send_keys(searching_criteria_dict["location"] if "location" in searching_criteria_dict else None)

        
        self.close_popup_with_js()
        for filter in filter_criteria_dict:
            if filter_criteria_dict[filter]:
                condition = filter_criteria_dict[filter].lower()
                filter_menu = self.wait_short.until(EC.visibility_of_element_located((By.ID, f"filter-{filter}")))
                filter_menu.click()

                logger.debug(f"xpath is //a[contains({Utils.translate_to_lower_case}, '{condition}')]")
                try:
                    # a pop up may appear at this step
                    self.wait_short.until(EC.visibility_of_element_located((By.XPATH, f"//a[contains({Utils.translate_to_lower_case}, '{condition}')]"))).click()
                    self.close_popup_with_js()
                    self.wait_short.until(EC.presence_of_element_located((By.XPATH, f"//*[contains(@class, 'FilterPill-pillLabel') and contains({Utils.translate_to_lower_case}, '{condition}')]")), "filter timeout")
                except Exception as e:
                    logger.debug(f"cannot find element {e}")
                    continue

        logger.debug("all filters set")
        find_jobs_btn = self.wait_short.until(EC.visibility_of_element_located((By.XPATH, f"//button[contains(text(), 'Find jobs')]")))
        find_jobs_btn.click()


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

        job_desc_html = self.wait_medium.until(EC.presence_of_element_located((By.ID, "jobDescriptionText")), "find job desc text timeout").get_attribute("innerHTML")

        directApply = False

        try:
            apply_btn_locator = (By.ID, "indeedApplyButton")
            self.wait_short.until(EC.visibility_of_element_located(apply_btn_locator))
            logger.debug("apply btn %s", apply_btn_locator)
            directApply = True
            apply_link = self.driver.current_url
            logger.debug("direct apply and link %s, %s", directApply, apply_link)
        except Exception as e:
            logger.debug("cannot apply directly")
            apply_link = self.wait_short.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "button[aria-label*='Apply now']"))).get_attribute("href")
            logger.debug("apply link is %s", apply_link)

        company = self.wait_short.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div[data-testid=inlineHeader-companyName]"))).get_attribute("innerText")
        position = self.wait_short.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".jobsearch-JobInfoHeader-title-container span"))).get_attribute("innerText").split("\n")[0]
        address_and_work_mode = self.wait_short.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div[data-testid=inlineHeader-companyLocation]"))).get_attribute("innerText")
        address = re.search("(\w|,|\s)*", address_and_work_mode)
        if address:
            address = address.group(0)
        logger.debug(f"address_and_work_mode is {address_and_work_mode}, address is {address}")

        # Check if the primary key of the new row exists in the DataFrame
        logger.debug(f"self.jobs.empty {self.jobs.empty}")
        if job_link is None and not self.jobs.empty and (self.jobs[self.primary_keys] == [company, position]).all(axis = 1).any():
            logger.debug(f"Job {position} at {company} already exist in job csv")
            return None
        
        return {
            "company": company,
            # position obtained from the html has the format {position}\n-job post
            "position": position,
            "address": address,
            "desciptionHtml": job_desc_html,
            "link": self.driver.current_url,
            "address_from_Internet": None,
            "directApply": directApply, # apply on Indeed directly
            "apply_link": apply_link, # if the job can be applied directly, the apply link will be the same as link
            "applied": False
        }


    def scan_jobs(self, num_of_jobs = 10):
        jobs_found = 0

        is_last_page = False
        page = 1
        self.close_popup_with_js()
        while not is_last_page:
            logger.debug(f"In page {page}")
            job_results = self.wait_short.until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, ".mosaic-provider-jobcards li a")))
            logger.debug(f"job results: {job_results}")

            for job in job_results:
                self.wait_short.until(EC.element_to_be_clickable(job))
                job.click()

                data = self.get_job_description()
                if data == 0:
                    continue
                
                if not data is None:
                    jobs_found += 1
                    logger.debug(f"jobs found: {jobs_found}")
                yield data
                if jobs_found >= num_of_jobs:
                    break

            if jobs_found >= num_of_jobs:
                break

            try:
                next_page_btn_locator = self.wait_short.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "a[data-testid=pagination-page-next]")))
                self.wait_medium.until(EC.presence_of_element_located(next_page_btn_locator), "next page timeout")
                logger.debug("going to next")
                page += 1
            except:
                is_last_page = False
                logger.debug("no more pages")


    def apply(self, jobs = None, manualCheck = True):
        logger.debug("applying")

        logger.debug("applying")

        if not jobs:
            jobs = self.jobs

        if not isinstance(jobs, pd.DataFrame):
            if isinstance(jobs, dict):
                jobs = []
            jobs = pd.DataFrame(jobs)

        for index, job in jobs.iterrows():
            job = job.to_dict()
            logger.debug(f"applying job {job}")
            
            auto_fill = FormAutoFiller(self.driver, job["company"])

            # there are 2 cases, a job can either be applied directly via indeed or via the company's website
            # For direct indeed apply, the program can automate the whole process
            # For the indirect apply, the program will try to detect input fields and populate them
            if not job["applied"] and job["directApply"]:
                self.driver.get(job["apply_link"])

                apply_btn = self.wait_medium.until(EC.visibility_of_element_located((By.ID, "indeedApplyButton")), "apply btn timeout")
                logger.debug(f"apply btn {apply_btn}, {apply_btn.tag_name}")
                original_window = self.driver.current_window_handle
                logger.debug(f"oringinal window {original_window}, {self.driver.window_handles}")
                num_of_windows = len(self.driver.window_handles)
                logger.debug(f"num of winds  {num_of_windows}")
                time.sleep(1) # nothing will happen without this line
                apply_btn.click()
                # button that runs javascript cannot be triggered by selenium.click()
                logger.debug(f"window handles  {self.driver.window_handles}")
                res = self.wait_medium.until(EC.number_of_windows_to_be(num_of_windows + 1), "not going to new page timeout")
                logger.debug(f"res  {res}")
                new_window = self.driver.window_handles[-1]

                self.driver.switch_to.window(new_window)
                time.sleep(5)

                logger.debug(f"window handles after {self.driver.current_window_handle}, {self.driver.window_handles}")

                in_submission_page = False
                url_changes = True
                while not in_submission_page:
                    try:
                        if url_changes:
                            # close the pop up for resume privacy setting
                            self.close_popup_with_js()
                            url_changes = False

                            # sometimes the resume input box is hidden
                            show_resume_btn = Utils.is_element_exist(self.driver, By.ID, "resume-display-buttonHeader")
                            logger.debug(f"exist ?  {show_resume_btn}")
                            if show_resume_btn:
                                logger.debug(f"show resume")
                                show_resume_btn.click()


                            questions_and_inputs = auto_fill.find_questions()
                            logger.debug(f"questions are  {questions_and_inputs}")

                            for question in questions_and_inputs:
                                answer = auto_fill.answer_text_question_and_upload(question, input_element=questions_and_inputs[question])
                                logger.debug(f"answer in indeed {answer}")


                            current_url = self.driver.current_url
                            continue_btn = self.wait_short.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "button[data-testid='continue-button']")))
                            continue_btn.click()
                            self.wait_short.until(EC.url_changes(current_url), "still on the same input page timeout")
                            url_changes = True

                        else:
                            logger.warning("Cannot proceed automatically")
                            Utils.wait_for_human_verification()
                        logger.debug("getting submit btn")
                        submit_btn = self.wait_short.until(EC.presence_of_element_located((By.XPATH, f"//button[contains(text(), 'Submit')]")), "find submission btn timeout")
                        in_submission_page = True

                    except Exception as e:
                        logger.debug(f"apply error  {e}")
                        logger.debug("not in submission page: ", e)


                if manualCheck:
                    Utils.wait_for_human_verification()
                else:
                    submit_btn.click()
            elif not job["applied"]:
                # for jobs that are applied via the company's own website,
                # the program would just try to populate the data at best effort
                # manual checking is mandatory

                while True:
                    user_response = input("Continue Auto Fill? y or n: ")

                    if user_response == "n":
                        break
                    elif user_response != "y":
                        logger.debug("Please enter either y or n")
                        continue

                    logger.debug(f"indirect apply {job}")
                    questions_and_inputs = auto_fill.find_questions()
                    logger.debug(f"questions and inputs  {question}")

                    for question in questions_and_inputs:
                        answer = auto_fill.answer_text_question_and_upload(question, input_element=questions_and_inputs[question])
                        logger.debug(f"answer in indeed {answer}")

                Utils.wait_for_human_verification()

            jobs.loc[index, "applied"] = True
    

    def interactive_mode(self, url_format = "https:\/\/.*indeed.com\/(viewjob|jobs)\?", apply = False):
        super().interactive_mode(url_format, apply)


