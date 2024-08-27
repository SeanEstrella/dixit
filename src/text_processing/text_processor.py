import spacy
from typing import Optional
from text_processing.abstractor import Abstractor

class TextProcessor:
    def __init__(self, nlp_model: Optional[spacy.language.Language] = None):
        """
        Initialize the TextProcessor with an NLP model.

        Args:
            nlp_model (Optional[spacy.language.Language]): A spaCy language model. Defaults to 'en_core_web_sm' if not provided.
        """
        self.nlp = nlp_model or spacy.load("en_core_web_sm")

    def remove_repetitions(self, phrase: str) -> str:
        """
        Remove repeated words within a phrase.

        Args:
            phrase (str): The input phrase from which repeated words should be removed.

        Returns:
            str: The phrase with repeated words removed.
        """
        words = phrase.split()
        unique_words = dict.fromkeys(word.lower() for word in words)
        return " ".join(unique_words)

    def obfuscate_description(self, description: str, abstractor: Abstractor) -> str:
        """
        Obfuscate a text description by generating a creative abstraction and processing it.

        Args:
            description (str): The description to be obfuscated.
            abstractor (Abstractor): The Abstractor instance used to generate creative abstractions.

        Returns:
            str: The obfuscated and processed description.
        """
        abstracted_phrase = abstractor.generate_creative_abstract(description)
        processed_phrase = self.remove_repetitions(abstracted_phrase)
        return processed_phrase
