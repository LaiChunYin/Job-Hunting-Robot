from dotenv import load_dotenv
import os
import logging
import yaml

class Config:
    # Configure logging
    class CustomFormatter(logging.Formatter):
        white = "\x1b[38;20m"
        yellow = "\x1b[33;20m"
        red = "\x1b[31;20m"
        green = "\033[92m"
        bold_red = "\x1b[31;1m"
        reset = "\x1b[0m"
        format = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"

        FORMATS = {
            logging.DEBUG: white + format + reset,
            logging.INFO: green + format + reset,
            logging.WARNING: yellow + format + reset,
            logging.ERROR: red + format + reset,
            logging.CRITICAL: bold_red + format + reset
        }

        def format(self, record):
            log_fmt = self.FORMATS.get(record.levelno)
            formatter = logging.Formatter(log_fmt)
            return formatter.format(record)
        
    def initialize(log_level = logging.DEBUG):
        # Create a handler
        log_level = logging.DEBUG
        print("log level ", log_level)
        handler = logging.StreamHandler()
        handler.setFormatter(Config.CustomFormatter())

        # Set Selenium's logger to only log warnings or higher
        logging.basicConfig(level= log_level, handlers=[handler])
        logging.getLogger('selenium').setLevel(logging.ERROR)
        logging.getLogger('urllib3').setLevel(logging.ERROR)
        logging.getLogger('undetected_chromedriver').setLevel(logging.ERROR)

    load_dotenv()

    LIBREOFFICE_PATH = os.getenv("LIBREOFFICE_PATH")
    CHATGPT_EMAIL = os.getenv("CHATGPT_EMAIL")
    INDEED_EMAIL = os.getenv("INDEED_EMAIL")
    LINKEDIN_EMAIL = os.getenv("LINKEDIN_EMAIL")
    CHATGPT_PASSWORD = os.getenv("CHATGPT_PASSWORD")
    INDEED_PASSWORD = os.getenv("INDEED_PASSWORD")
    LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD")
    CHATGPT_API_KEY = os.getenv("CHATGPT_API_KEY")

    PROJ_ROOT = os.path.abspath(os.path.join(__file__, "../.."))
    print(f"project root is {PROJ_ROOT}")

    with open(os.path.join(PROJ_ROOT, 'config/personal_info.yaml'), 'r') as file:
        data = yaml.safe_load(file)
        PERSONAL_INFO = data
        PERSONAL_INFO["resume_path"] = os.path.abspath(os.path.join(PROJ_ROOT, PERSONAL_INFO["resume_path"])) if "resume_path" in PERSONAL_INFO else None
        PERSONAL_INFO["cover_letter_path"] = os.path.abspath(os.path.join(PROJ_ROOT, PERSONAL_INFO["cover_letter_path"])) if "cover_letter_path" in PERSONAL_INFO else None
        # print(f"personal info is {PERSONAL_INFO}")

    with open(os.path.join(PROJ_ROOT, 'config/search_and_filter.yaml'), 'r') as file:
        data = yaml.safe_load(file)
        INDEED_SEARCH_CRITERIA = data["indeed_search_criteria"] if "indeed_search_criteria" in data else {}
        INDEED_FILTER_CRITERIA = data["indeed_filter_criteria"] if "indeed_filter_criteria" in data else {}
        LINKEDIN_SEARCH_CRITERIA = data["linkedin_search_criteria"] if "linkedin_search_criteria" in data else {}
        LINKEDIN_FILTER_CRITERIA = data["linkedin_filter_criteria"] if "linkedin_filter_criteria" in data else {}
        # print(f"search and filter is {INDEED_SEARCH_CRITERIA}, {INDEED_FILTER_CRITERIA}")
