from abc import ABC, abstractclassmethod
from selenium import webdriver
import os
import undetected_chromedriver
from chatgpt_automation.chatgpt_automation import ChatGPTAutomation
import chatgpt_automation.prompts.prompts as prompts
import json
import re
import logging
import pandas as pd
import numpy as np
import logging
from files_generator.cover_letter_generator import CoverLetterGenerator
from config.config import Config
from selenium.webdriver.support.wait import WebDriverWait

logger = logging.getLogger(__name__)
pd.set_option('display.max_rows', None)  # or a large number if 'None' is too much
pd.set_option('display.max_columns', None)  # Show all columns

class JobWebsite(ABC):
    def __init__(self, driver, url, email, password, searching_criteria_dict, filter_criteria_dict, existing_jobs_path = "resources/jobs.csv"):
        # self.jobs represents the jobs found and saved previously in the csv file
        # self.jobs should only be updated in the apply function (change application status)
        existing_jobs_path = os.path.join(Config.PROJ_ROOT, existing_jobs_path)
        column_names = ['company', 'position', 'address', 'desciptionHtml', 'link', 'address_from_Internet', 'directApply', 'apply_link']
        self.primary_keys = ['company', 'position']
        self.jobs = pd.DataFrame(columns=column_names)
        logger.debug(f"self.jobs  {self.jobs}")

        if existing_jobs_path and os.path.isfile(existing_jobs_path):
            try:
                self.existing_jobs_path = existing_jobs_path
                df = pd.read_csv(existing_jobs_path)
                logger.debug(f"read csv 1 {df.to_dict(orient= 'records')}")
                df = df.astype(object).replace(np.nan, None)
                logger.debug(f"read csv 2 {df.to_dict(orient= 'records')}")
                logger.debug(f"job csv : {df}")
                self.jobs = df
            except Exception as e:
                logger.error("cannot read %s: %e", existing_jobs_path, e)

        self.email = email
        self.password = password
        self.searching_criteria_dict = searching_criteria_dict
        self.filter_criteria_dict = filter_criteria_dict


        self.url = url
        chrome_options = webdriver.ChromeOptions()

        self.driver = driver if driver else undetected_chromedriver.Chrome(options = chrome_options)
        self.wait_short = WebDriverWait(self.driver, 3)
        self.wait_medium = WebDriverWait(self.driver, 5)
        self.wait_long = WebDriverWait(self.driver, 10)

        logger.debug("init indeed")
        if not webdriver:
            #open in new tab
            self.driver.switch_to.new_window('tab')

        self.driver.get(self.url)
        self.handle = self.driver.current_window_handle

    @abstractclassmethod
    def login(self):
        pass


    @abstractclassmethod
    def searchJobs(self, searching_criteria_dict = {}, filter_criteria_dict = {}):
        pass

    @abstractclassmethod
    def scan_jobs(self, num_of_jobs = 5):
        pass


    def generate_cover_letters(self, jobs):
        logger.debug("generating cover letters")

        if not isinstance(jobs, pd.DataFrame):
            if isinstance(jobs, dict):
                jobs = [jobs]
            jobs = pd.DataFrame(jobs)

        for index, job in jobs.iterrows():
            job = job.to_dict()
            if job.get("cover_letter", False):
                continue

            logger.debug(f"writing for job: {job['position']}, {job['company']}")
            write_cover_letter_prompt = prompts.WRITE_COVER_LETTER.format(position = job["position"], resume= prompts.RESUME, job_desc = job["desciptionHtml"])
            # chatgpt = ChatGPTAutomation(self.driver)
            chatgpt = ChatGPTAutomation()  # open a new window if the job website's Google Account is different from ChatGPT's Google Account
            cover_letter = chatgpt.ask(write_cover_letter_prompt)
            job["cover_letter"] = cover_letter

            get_company_addr_prompt = prompts.GET_COMPANY_ADDRESS.format(company = job["company"])
            address_from_Internet = chatgpt.ask(get_company_addr_prompt)
            logger.debug(f"address_from_internet answer: {address_from_Internet}")
            addr_search_result = re.search("(\{.*\})", address_from_Internet, flags = re.S)
            address_from_Internet = addr_search_result.group(0) if addr_search_result else None
            logger.debug(f"address_from_internet json: {address_from_Internet}")

            # go back to Indeed after using ChatGPT
            self.driver.switch_to.window(self.handle)
            try:
                logger.debug(f"address from internet: {json.loads(address_from_Internet)}")
                job["address_from_internet"] = json.loads(address_from_Internet) if address_from_Internet else None
            except Exception as e:
                logger.error(f"no a json: {e}")
                job["address_from_internet"] = None

            logger.debug(f"in indeed, generating cover letter for {job}")
            CoverLetterGenerator(company=job["company"],
                            position=job["position"],
                            address=job["address_from_internet"] if job["address_from_internet"] else job["address"],
                            content=cover_letter).populate_file()
            logger.debug("--------------cover letter generated--------------")


    def generate_resume(self, jobDesc):
        pass

    @abstractclassmethod
    def apply(self, jobs = None, manualCheck = True):
        pass

    def generate_report(self, jobs = None, path = "resources/jobs.csv"):
        path = os.path.join(Config.PROJ_ROOT, path)
        logger.debug("generating report to {path}")

        logger.debug(f"report data  {self.jobs}")

        if not jobs is None:
            mode = "a"
            jobs_to_be_saved = jobs
        else:
            mode = "w"
            jobs_to_be_saved = self.jobs
        logger.debug(f"mode is  {mode}")
        jobs_to_be_saved.to_csv(path, mode=mode, index = False, header = not os.path.isfile(path))


    def close_popup_with_js(self):
        try:
            # the callback is to signal Selenium that the script is complete
            script = """
                console.log("running");
                var callback = arguments[arguments.length - 1];
                setInterval(function(){
                    var closeButton = document.querySelector('.DesktopJobAlertPopup-heading + button, button[aria-label="Close"]');
                    console.log("close btn is ", closeButton)
                    if (closeButton) closeButton.click();
                    callback()
                }, 3000);
            """

            self.driver.execute_async_script(script)
            logger.debug(f"Popup closed with JS.")
        except Exception as e:
            logger.error(f"Error closing popup with JS: {e}")



    def find_jobs(self, num_of_jobs = 5, apply = False):
            """
            apply immediately after getting a job description and generate cover letter
            If apply is set to True, the program will also apply immediately after the cover letter is generated
            """
            logger.debug(f"login window  {self.driver.current_window_handle}, {self.driver.window_handles}")
            self.login()
            logger.debug("----------searching Jobs----------")
            self.searchJobs(self.searching_criteria_dict, self.filter_criteria_dict)
            logger.debug("----------Scanning Jobs----------")
            new_jobs = []
            for job in self.scan_jobs(num_of_jobs):
                if not job:
                    continue

                logger.debug("----------generating cover letter----------")
                logger.debug(job)
                self.generate_cover_letters(job)
                if apply:
                    logger.debug("----------Applying----------")
                    self.apply(job)
                new_jobs += [job]
            logger.debug("----------generating report----------")
            new_jobs = pd.DataFrame(new_jobs)
            logger.debug(f"new jobs found: {new_jobs}")
            self.generate_report(new_jobs)
            logger.info("----------DONE----------")
            logger.info("You may still use the browsers. Please close the application manually")
            while True:
                pass

    def find_all_jobs_then_apply(self, num_of_jobs = 5, apply = True):
        """
        collect all job decription and generate cover letter first.
        If apply is set to True, the program will also apply the jobs found
        """
        self.login()
        logger.debug("----------searching Jobs----------")
        self.searchJobs(self.searching_criteria_dict, self.filter_criteria_dict)
        logger.debug("----------Scanning Jobs----------")
        new_jobs = []
        for job in self.scan_jobs(num_of_jobs):
            new_jobs += [job] if job else []
        logger.debug(f"new job  {new_jobs}")
        logger.debug("----------generating cover letter----------")
        self.generate_cover_letters(new_jobs)

        if apply:
            logger.debug("----------Applying----------")
            logger.debug(new_jobs)
            self.apply(new_jobs)

        logger.debug("----------generating report----------")
        logger.debug(new_jobs)
        self.generate_report(new_jobs)
        logger.info("----------DONE----------")
        logger.info("You may still use the browsers. Please close the application manually")
        while True:
            pass

    def apply_from_file(self):
        """
        read the jobs saved in jobs.csv and apply them
        """
        logger.debug("----------Applying from file----------")
        self.apply()
        logger.debug("----------generating report----------")
        self.generate_report()
        logger.info("----------DONE----------")
        logger.info("You may still use the browsers. Please close the application manually")
        while True:
            pass


    def interactive_mode(self, url_format = ".*", apply = False):
        """Get Job info from the given link and generate a cover letter"""
        self.login()
        job_link = input("Enter a Job link, or type 'quit': ")
        while job_link != "quit":
            if not re.search(url_format, job_link):
                logger.info(f"The job link should have the format like {url_format}")
                logger.info(f"Job links can be found in job search result or saved jobs")
                job_link = input("Enter a Job link, or type 'quit': ")
                continue

            logger.debug("----------getting job info----------")
            job = self.get_job_description(job_link)
            logger.debug("----------generating cover letter----------")
            self.generate_cover_letters(job)

            if apply:
                self.apply()

            logger.info("----------Done----------")
            job_link = input("Enter a Job link, or type 'quit': ")



