from abc import ABC, abstractclassmethod
from docx import Document
import re
from datetime import datetime
from config.config import Config
import logging
import subprocess
import os

logger = logging.getLogger(__name__)
class FileGenerator(ABC):

    def __init__(self, template, company, position, address, content, contact_info, folder):
        self.first_name = Config.PERSONAL_INFO["first_name"]
        self.last_name = Config.PERSONAL_INFO["last_name"]
        self.dynamic_contents = {}
        date = datetime.now().strftime("%B %d, %Y")

        self.template = os.path.join(Config.PROJ_ROOT, template)
        self.doc = Document(self.template)
        self.dynamic_contents["date"] = date
        self.dynamic_contents["company"] = company
        self.dynamic_contents["position"] = position
        self.dynamic_contents["address"] = self.parse_address(address)
        self.dynamic_contents["content"] = content
        self.dynamic_contents["contact_info"] = contact_info
        self.folder = os.path.join(Config.PROJ_ROOT, f"{folder}/{self.dynamic_contents['company']}")
        

    def get_format_attributes(self, object):
        if object == "paragraph":
            return ['alignment', 'left_indent', 'right_indent', 'first_line_indent', 
                    'space_before', 'space_after', 'line_spacing',
                    'keep_together', 'keep_with_next', 'page_break_before', 'widow_control']
        elif object == "run":
            return ['name', 'bold', 'italic', 'underline', 'strike', 'size', 'color.rgb', 'highlight_color']
        else:
            raise Exception("object should be either 'paragraph' or 'run'")
        
    # paragraph format is a read-only, need to copy its attributes one by one
    def copy_format(self, to_obj, from_obj, format_attributes):

        for attr in format_attributes:
            target = to_obj
            copy_from = from_obj
            logger.debug(f"setting attr {attr}")
            subAttributes = attr.split(".")
            logger.debug(f"sub attributes {subAttributes}")
            while len(subAttributes) > 1:
                attr = subAttributes.pop(0)
                target = getattr(target, attr)
                copy_from = getattr(copy_from, attr)
            attr = subAttributes.pop(0)    
            logger.debug(f"final to attr {target}, {attr}, {getattr(copy_from, attr)}")
            setattr(target, attr, getattr(copy_from, attr))

            
    def substitute_dynamic_contents(self, match, para):
        placeholder = match.group(0)[1:-1]
        logger.debug(f"placholder is {placeholder}, {para}")

        if placeholder == "content":
            
            style = para.style
            paragraph_format = para.paragraph_format
            run_font_format = para.runs[0].font
            logger.debug(f"style is {style}, {paragraph_format}, {run_font_format}")
            paragraphs = re.split("\n+", self.dynamic_contents["content"])
            logger.debug(f"paragraphs are {paragraphs}")
            logger.debug(f"for para format attr {paragraph_format.__dir__()}")
            logger.debug(f"for run format attr  {run_font_format.__dir__()}")
            num_of_paragraphs = len(paragraphs)
            logger.debug(f"num of para  {num_of_paragraphs}")
            # add paragraphs starting from the last one because the same para is used for each iteration
            # after each iteration, the next paragraph of para would be the newly creating paragraph
            # if the paragraphs are added in the normal order, for each iteration, the newly created paragraph would be inserted between para and the paragraph created previously
            # Also, for the top paragraph, it will be used to replace the placeholder {content}. No new paragraph will be added
            for index, text in enumerate(paragraphs[:0:-1]):
                # Create a new paragraph XML element
                new_paragraph = self.doc.add_paragraph("\n" + text)
                para._p.addnext(new_paragraph._p)

                paragraph_format_attributes = self.get_format_attributes("paragraph")
                run_font_format_attributes = self.get_format_attributes("run")
                self.copy_format(new_paragraph.paragraph_format, paragraph_format, paragraph_format_attributes)
                for run in new_paragraph.runs:
                    logger.debug(f"new para run  {run.text}")
                    self.copy_format(run.font, run_font_format, run_font_format_attributes)

            return paragraphs[0]
        else:
            subfields = placeholder.split(" ")
            logger.debug(f"subfields are {subfields}")

            logger.debug(f"{placeholder} not found")
            value = self.dynamic_contents.get(subfields.pop(0), None)
            for field in subfields:
                logger.debug(f"{field} not found")
                value = value.get(field, None)

            return value



    @abstractclassmethod
    def populate_file(self):
        pass
    

    def convert_to_pdf(self):
        # requires MS word to be installed
        # convert(f"{self.folder}/{self.first_name}_{self.last_name}_Cover_Letter.docx", f"{self.folder}/{self.first_name}_{self.last_name}_Cover_Letter.pdf", keep_active = True)

        """
        Convert a document to PDF using LibreOffice.
        :param libreoffice_path: Path to the LibreOffice executable
        :param input_file: Path to the input file (e.g., DOCX)
        :param output_dir: Directory where the output PDF will be saved
        """
        # requires LibreOffice to be installed
        input_file = f"{self.folder}/{self.first_name}_{self.last_name}_Cover_Letter.docx"
        output_dir = self.folder
        args = [
            Config.LIBREOFFICE_PATH, 
            '--headless', 
            '--convert-to', 
            'pdf', 
            '--outdir', 
            output_dir, 
            input_file
        ]
        result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result

    def parse_address(self, address):
        logger.debug(f"parsing address {address}")
        if isinstance(address, str):
            parsed_addr = {}
            for area in address.split(", "):
                area = area.strip()
                if not "street" in parsed_addr:
                    parsed_addr["street"] = area
                elif not "city" in parsed_addr:
                    parsed_addr["city"] = area
                elif not "province" in parsed_addr:
                    parsed_addr["province"] = area
                elif not "country" in parsed_addr:
                    parsed_addr["country"] = area
                elif not "postalCode" in parsed_addr:
                    parsed_addr["postalCode"] = area

            if "city" in parsed_addr and "province" in parsed_addr:
                parsed_addr["city"] += ","
            return parsed_addr
        else:
            return address
