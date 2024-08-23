import openai
import os
import spacy
import time
from nltk.corpus import wordnet as wn
from functools import lru_cache

nlp = spacy.load('en_core_web_sm')

openai.api_key = os.getenv("OPENAI_API_KEY")

@lru_cache(maxsize=1000)
def generate_creative_abstract(word):
    """Generate abstract language using OpenAI's GPT-4."""
    prompt = (
        "You are a storyteller in the game Dixit. Given the word '{word}', create a single word or "
        "a very short phrase (1-3 words) that is mysterious, poetic, and sparks imagination. "
        "The response should be concise, unique, and open to interpretation. Avoid using quotes, "
        "and ensure the output is simple yet profound."
    ).format(word=word)
    
    retries = 3
    for attempt in range(retries):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=20,
                temperature=0.7,
            )
            return response.choices[0].message['content'].strip()
        except openai.error.RateLimitError:
            if attempt < retries - 1:
                print(f"Rate limit exceeded. Retrying in {2 ** attempt} seconds...")
                time.sleep(2 ** attempt)
            else:
                raise

def obfuscate_description(description):
    """Obfuscate a text description by generating creative abstractions for each token."""
    doc = nlp(description)
    return ' '.join(generate_creative_abstract(token.text) for token in doc)

if __name__ == "__main__":
    original_description = "A pair of pink ballet shoes on a wooden floor."
    obfuscated_description = obfuscate_description(original_description)

    print("Original:", original_description)
    print("Obfuscated:", obfuscated_description)