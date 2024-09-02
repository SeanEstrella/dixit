import openai
import os
import time
import logging
import random
from typing import List, Optional

RETRIES = 3
DEFAULT_MODEL = "gpt-4"

logger = logging.getLogger('clue_generator')


class ClueGenerator:
    def __init__(self, api_key: Optional[str] = None, model_name: str = DEFAULT_MODEL, max_tokens: int = 20, temperature: float = 0.9, top_p: float = 0.8):
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.top_p = top_p
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("API key is required for OpenAI.")


        openai.api_key = self.api_key
        self.model_name = model_name
        logger.info(f"ClueGenerator initialized with model: {self.model_name}")

    def generate_clue(
        self,
        description: str,
        other_cards: Optional[List[str]] = None,
        banned_phrases: Optional[List[str]] = None
    ) -> str:
        if banned_phrases is None:
            banned_phrases = ["whispers of grace"]

        other_cards_description = " | ".join(other_cards or [])
        base_prompt = (
            f"You are a storyteller in a creative and abstract game called Dixit. Your goal is to give a clue for "
            f"the following image description: '{description}'. The clue should be poetic, abstract, and evocative, "
            f"yet concise and complete. Generate a unique phrase or word (1-3 words) that captures the essence of your card while making it challenging for others to guess correctly. "
            f"Avoid using common phrases or too obvious clues. Think creatively to strike a balance between clarity and mystery."
        )

        alternative_prompts = [
            base_prompt,
            f"Generate a poetic clue for: '{description}' that is mysterious yet meaningful.",
            f"Think creatively and provide an abstract clue for the following image: '{description}'.",
            f"Provide a unique and challenging clue for: '{description}' in just a few words."
        ]

        for attempt in range(RETRIES):
            prompt = random.choice(alternative_prompts) 
            try:
                logger.debug(f"Attempt {attempt + 1} to generate a clue.")
                response = openai.ChatCompletion.create(
                    model=self.model_name,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    top_p=self.top_p,
                )
                generated_clue = response.choices[0].message["content"].strip()

                if all(
                    banned.lower() not in generated_clue.lower()
                    for banned in banned_phrases
                ):
                    logger.info("Clue generated successfully.")
                    return generated_clue
                else:
                    logger.warning(f"Generated clue contained banned phrases: {generated_clue}")

            except openai.error.RateLimitError:
                if attempt < RETRIES - 1:
                    wait_time = 2 ** attempt + random.uniform(0, 1)
                    logger.warning(
                        f"Rate limit exceeded. Retrying in {wait_time:.2f} seconds..."
                    )
                    time.sleep(wait_time)
                else:
                    logger.error("Rate limit exceeded after multiple retries.")
                    raise
            except openai.error.OpenAIError as e:
                logger.error(f"OpenAI API error occurred: {e}")
                if attempt == RETRIES - 1:
                    return self.generate_fallback_clue(description)
            except Exception as e:
                logger.error(f"An unexpected error occurred: {e}")
                return self.generate_fallback_clue(description)

        logger.warning("Returning fallback clue after all retries.")
        return self.generate_fallback_clue(description)


    def generate_fallback_clue(self, description: str) -> str:
        """
        Generate a more dynamic fallback clue if all attempts fail.

        Args:
            description (str): The main description.

        Returns:
            str: A more creative fallback clue.
        """
        keywords = self.extract_keywords(description)

        if len(keywords) < 2:
            keywords.extend(["something", "mystical"])

        templates = [
            f"A glimpse of {keywords[0]}...",
            f"What if it was {keywords[1]}?",
            f"Imagine something with {keywords[0]}...",
            f"A scene with {keywords[0]} and {keywords[1]}...",
        ]
        fallback_clue = random.choice(templates)
        logger.info(f"Generated fallback clue: {fallback_clue}")
        return fallback_clue

    def extract_keywords(self, description: str) -> List[str]:
        """
        Simple keyword extraction from the description.

        Args:
            description (str): The main description.

        Returns:
            List[str]: A list of key words or phrases.
        """
        from sklearn.feature_extraction.text import CountVectorizer
        vectorizer = CountVectorizer(stop_words='english', max_features=2)
        X = vectorizer.fit_transform([description])
        return vectorizer.get_feature_names_out()