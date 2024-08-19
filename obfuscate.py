import openai
import os
import spacy
import time
from nltk.corpus import wordnet as wn

nlp = spacy.load('en_core_web_sm')

openai.api_key = os.environ.get('OPENAI_API_KEY')

def get_hypernym(word):
    """Get a more general term using WordNet."""
    synsets = wn.synsets(word)
    if synsets:
        hypernyms = synsets[0].hypernyms()
        if hypernyms:
            return hypernyms[0].lemmas()[0].name().replace('_', ' ')
    return word

def generate_creative_abstract(word):
    """Generate abstract language using OpenAI's GPT-3.5-turbo."""
    try:
        prompt = f"We are playing Dixit and you are a storyteller. Please hallucinate. From this phrase make a new phrase in 1 word or less to win the round '{word}': "
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=50,
            temperature=0.7,
        )
        return response.choices[0].message['content'].strip()
    except openai.error.RateLimitError:
        print("Rate limit exceeded. Waiting before retrying...")
        time.sleep(60)  
        return generate_creative_abstract(word)

def abstract_word(word, pos, abstracted_words):
    """Abstract a word using a combination of hypernyms and GPT-3.5-turbo."""
    if pos in ['NOUN', 'VERB', 'ADJ'] and word not in abstracted_words:
        hypernym = get_hypernym(word)
        abstracted_word = generate_creative_abstract([hypernym])
        abstracted_words[word] = abstracted_word
        return abstracted_word
    return word

def obfuscate_description(description):
    doc = nlp(description)
    obfuscated_words = {}
    
    for token in doc:
        obfuscated_word = abstract_word(token.text, token.pos_, obfuscated_words)
        obfuscated_words[token.text] = obfuscated_word
    
    return ' '.join(obfuscated_words.get(token.text, token.text) for token in doc)

original_description = "A pair of pink ballet shoes on a wooden floor."
obfuscated_description = generate_creative_abstract(original_description)

print("Original:", original_description)
print("Obfuscated:", obfuscated_description)
