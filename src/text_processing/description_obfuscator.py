from text_processing.abstractor import Abstractor
from text_processing.text_processor import TextProcessor

class DescriptionObfuscator:
    def __init__(self, api_key=None, model_name="gpt-4o-mini"):
        self.abstractor = Abstractor(api_key=api_key, model_name=model_name)
        self.text_processor = TextProcessor()
    
    def obfuscate(self, description):
        """Obfuscate the description using the abstractor and text processor."""
        return self.text_processor.obfuscate_description(description, self.abstractor)