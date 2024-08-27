from text_processing.abstractor import Abstractor
from text_processing.text_processor import TextProcessor
import logging
from typing import Optional

class DescriptionObfuscator:
    def __init__(self, abstractor: Optional[Abstractor] = None, text_processor: Optional[TextProcessor] = None):
        """
        Initialize the DescriptionObfuscator with an Abstractor and a TextProcessor.

        Args:
            abstractor (Optional[Abstractor]): The abstractor used for obfuscation. Defaults to a new instance.
            text_processor (Optional[TextProcessor]): The text processor used for obfuscation. Defaults to a new instance.
        """
        self.abstractor = abstractor or Abstractor()
        self.text_processor = text_processor or TextProcessor()

    def obfuscate(self, description: str) -> str:
        """
        Obfuscate the provided description using the abstractor and text processor.

        Args:
            description (str): The description to be obfuscated.

        Returns:
            str: The obfuscated description, or a fallback message in case of an error.
        """
        try:
            logging.info(f"Starting obfuscation for description: {description}")
            obfuscated_description = self.text_processor.obfuscate_description(description, self.abstractor)
            logging.info("Obfuscation successful.")
            return obfuscated_description
        except Exception as e:
            logging.error(f"An error occurred during obfuscation: {e}")
            return "Obfuscated Description"
