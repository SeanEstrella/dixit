import openai
import os
import time
from functools import lru_cache

class Abstractor:
    def __init__(self, api_key=None, model_name="gpt-4o-mini"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        openai.api_key = self.api_key
        self.model_name = model_name

    @lru_cache(maxsize=1000)
    def generate_creative_abstract(self, word):
        """Generate abstract language using OpenAI's GPT-4."""
        prompt = (
            "You are a creative and imaginative storyteller. Given the word '{word}', create a single word or "
            "a very short phrase (1-3 words) that is unique, abstract, and sparks the imagination. "
            "The phrase should avoid common or repetitive patterns and instead focus on diversity and novelty."
        ).format(word=word)
        
        retries = 3
        for attempt in range(retries):
            try:
                response = openai.ChatCompletion.create(
                    model=self.model_name,
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