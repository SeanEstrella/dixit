import spacy

class TextProcessor:
    def __init__(self):
        self.nlp = spacy.load('en_core_web_sm')
    
    def remove_repetitions(self, phrase):
        """Remove repeated words within a phrase."""
        words = phrase.split()
        seen = set()
        result = []
        for word in words:
            if word.lower() not in seen:
                seen.add(word.lower())
                result.append(word)
        return ' '.join(result)
    
    def obfuscate_description(self, description, abstractor):
        """Obfuscate a text description by generating creative abstractions for each token."""
        doc = self.nlp(description)
        abstracted_phrases = (abstractor.generate_creative_abstract(token.text) for token in doc)
        processed_phrases = [self.remove_repetitions(phrase) for phrase in abstracted_phrases]
        return ' '.join(processed_phrases)