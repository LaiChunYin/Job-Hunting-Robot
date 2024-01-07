import logging
from files_generator.file_generator import FileGenerator

logger = logging.getLogger(__name__)

class ResumeGenerator(FileGenerator):

    def __init__(self, template = "resources/templates/resume_template.docx", company = "", position = "", address = "", content = "", contact_info = "", folder = "resources/resumes"):
        pass

    def populate_file(self):
        pass