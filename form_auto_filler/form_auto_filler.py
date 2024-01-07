import re
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
from config.config import Config

logger = logging.getLogger(__name__)

class FormAutoFiller:

    input_element_css_selector = "textarea,input[type=text],input[type=tel],input[type=number],input[type=email],input[type=file]"

    def __init__(self, driver, company):
        self.driver = driver
        self.already_answered = {}  # check if a question pattern is already matched
        self.input_already_filled = {}   # check if an input element is filled already

        # the keys are some keywords/patterns that might appear in a question. 
        # the value is the corresponding answer
        self.questionsAns = {
            "first name": Config.PERSONAL_INFO["first_name"],
            "last name": Config.PERSONAL_INFO["last_name"],
            "preferred name": Config.PERSONAL_INFO["preferred_name"],
            "email": Config.PERSONAL_INFO["email"],
            "(phone|mobile)": Config.PERSONAL_INFO["mobile"],
            "how many year.*experience": Config.PERSONAL_INFO["year_of_experience"],
            "city": Config.PERSONAL_INFO["city"],
            "(resume|cv)": Config.PERSONAL_INFO["resume_path"].format(company = company),
            "(cover letter)": Config.PERSONAL_INFO["cover_letter_path"].format(company = company),
        }

        for question_pattern in self.questionsAns:
            self.already_answered[question_pattern] = False

    def find_questions(self):
        # Tracing back to find a preceding label or text
        # This is a heuristic and might need adjustments
        logger.debug("finding questions")
        input_elements = WebDriverWait(self.driver, 10).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, FormAutoFiller.input_element_css_selector)))
        logger.debug(f"input elements: {input_elements}")

        questions_and_inputs = {}
        for input_elem in input_elements:
            # find the last textual element above the input element that matches a question pattern
            # search from the back of input elements, find the first one that matches
            # search no more than 5 element because the question should not be to far away from the input area

            preceding_elements = input_elem.find_elements(By.XPATH, "preceding::*[self::div or self::span or self::p or self::label][text()]")
            logger.debug("preceding: {preceding_elements}")
            for elem in preceding_elements[:-3:-1]:
                logger.debug(f"elem is  {elem.tag_name}, {elem.get_attribute('innerText')}")
                if elem.tag_name in ['label', 'p', 'span', 'div']:
                    text = elem.text.strip()
                    logger.debug(f"text quest is {text}, {text in questions_and_inputs}")

                    if text and not text in questions_and_inputs:
                        questions_and_inputs[text] = input_elem
                    
        logger.debug(f"quest and input {questions_and_inputs}")
        return questions_and_inputs

    def answer_text_question_and_upload(self, question, input_element = None, auto_fill = True):
        """
        Find input element and then populate them. Can handle text and file inputs.
        """
        for question_pattern in self.questionsAns:
            # if a question is already answer but the input element is not yet filled, it's probably because of a wrong question is matched with the input element
            # if a input element is filled but the questions is not yet answered, it's probably because of there are more than one questions got associated with an input element
            # both cases are due to the fact that the program is searching too far away from the input box (for the first case, it is also because of the program are missing a question in the question bank)
            logger.debug(f"web element id  {input_element.id}")
            if self.already_answered[question_pattern] or self.input_already_filled.get(input_element.id, False):
                logger.debug(f"question_pattern already answered  {question_pattern}")
                continue
            match_result = re.search(question_pattern, question, re.IGNORECASE)
            logger.debug(f"match result {match_result}")

            if match_result:
                answer = self.questionsAns[question_pattern]
                logger.debug(f"answer is {answer}")
                self.already_answered[question_pattern] = True
                self.input_already_filled[input_element.id] = True

                # auto fill if driver is provided
                if auto_fill and not self.driver:
                    raise Exception("please provide driver for auto fill")
                elif auto_fill and self.driver and not input_element:
                    raise Exception("plese provide the input element for auto fill")
                elif auto_fill and self.driver and input_element:
                    try:
                        if input_element.tag_name == "input" and input_element.get_attribute("type") != "file":
                            WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable(input_element))
                            logger.debug(f"auto filling  {question} with {answer} to {input_element.tag_name}")
                            logger.debug(f"not file  {input_element.get_attribute('type')}")
                            input_element.clear()   # clear default values

                            # .clear() does not work here
                            input_element.send_keys(Keys.COMMAND, "a")
                            input_element.send_keys(Keys.DELETE)
                        else:
                            logger.debug("is file")

                        input_element.send_keys(answer)
                    except Exception as e:
                        logger.error(f"error in auto fill {type(e)}, {e}")
                        raise e

                return answer
        return None

    def answer_multiple_choice(self, question):
        pass