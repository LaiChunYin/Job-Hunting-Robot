import undetected_chromedriver
from job_websites.indeed import Indeed
from job_websites.linkedin import Linkedin
from config.config import Config
import logging
import argparse


def main():
    parser = argparse.ArgumentParser(description='Example Python CLI Tool.')
    parser.add_argument("website", type=str, help='Select a Job website: Indeed or Linkedin. For Linkedin, only interactive mode is supported')

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-s", "--scan", nargs=1, type=int, help='Run the scan job mode')
    group.add_argument("-i", "--interactive", action= "store_true", help='Run the interactive mode')

    parser.add_argument("-a", "--apply", action= "store_true", help='Apply automatically')
    parser.add_argument("-v", "--verbose", action= "store_true", help='Print logs')

    args = parser.parse_args()
    print("args are ", args)
    if args.verbose:
        log_level = logging.DEBUG
    else:
        log_level = logging.ERROR

    Config.initialize(log_level)

    logger = logging.getLogger(__name__)
    logger.debug(f"args are {args}")

    if args.website.lower() == "indeed":
        job_website = Indeed(undetected_chromedriver.Chrome(), Config.INDEED_EMAIL, Config.INDEED_PASSWORD, Config.INDEED_SEARCH_CRITERIA, Config.INDEED_FILTER_CRITERIA)
    elif args.website.lower() == "linkedin":
        job_website = Linkedin(undetected_chromedriver.Chrome(), Config.LINKEDIN_EMAIL, Config.LINKEDIN_PASSWORD, Config.LINKEDIN_SEARCH_CRITERIA, Config.LINKEDIN_FILTER_CRITERIA)
    else:
        parser.exit(0, "website shoule be either Indeed or Linkedin")

    if args.scan:
        job_website.find_jobs(args.scan[0], args.apply)
    elif args.interactive:
        job_website.interactive_mode(apply = args.apply)



if __name__ == '__main__':
    main()