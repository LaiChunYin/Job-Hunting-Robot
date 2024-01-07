import re
import os
import logging
from config.config import Config
from files_generator.file_generator import FileGenerator

logger = logging.getLogger(__name__)
class CoverLetterGenerator(FileGenerator):

    def __init__(self, template = "resources/templates/cover_letter_template.docx", company = "", position = "", address = "", content = "", contact_info = "", folder = "resources/cover_letters"):
        super().__init__(template, company, position, address, content, contact_info, folder)

    def populate_file(self):
        logger.debug("creating cover letter")

        for para in self.doc.paragraphs:
            logger.debug(f"para is  {para}")
            for run in para.runs:

                logger.debug(f"before run text {run.text}, {run.bold}, {run.italic}, {run.underline}, {run.font}, {run.contains_page_break}, {run.part}")
                run.text = re.sub(r"(\{[0-9a-zA-Z._\-:\s]*\})", lambda match, para = para: self.substitute_dynamic_contents(match, para), run.text)
                logger.debug(f"after  {run.text}")

        # Save the document
        file_path = os.path.join(Config.PROJ_ROOT, f"{self.folder}/{self.first_name}_{self.last_name}_Cover_Letter.docx")

        # Create a new folder if it doesn't exist
        os.makedirs(self.folder, exist_ok=True)

        self.doc.save(file_path)
        logger.debug("docx created")

        try:
            logger.info("Please make sure LibreOffice is Installed")
            self.convert_to_pdf()
        except Exception as e:
            logger.debug("cannot convert to pdf: ", e)

        return file_path
    
