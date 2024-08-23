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
        """Obfuscate a text description by generating a single creative abstraction for the entire description."""
        abstracted_phrase = abstractor.generate_creative_abstract(description)
        
        processed_phrase = self.remove_repetitions(abstracted_phrase)
        
        return processed_phrase