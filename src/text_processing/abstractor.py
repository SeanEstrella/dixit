import openai
import os
import time
import logging
import random
from typing import List, Optional

RETRIES = 3
DEFAULT_MODEL = "gpt-4"

logger = logging.getLogger('text_processing')

class Abstractor:
    def __init__(self, api_key: Optional[str] = None, model_name: str = DEFAULT_MODEL):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            logger.error("API key is required for OpenAI.")
            raise ValueError("API key is required for OpenAI")

        openai.api_key = self.api_key
        self.model_name = model_name
        logger.info(f"Abstractor initialized with model: {self.model_name}")

    def generate_creative_abstract(
        self,
        description: str,
        other_cards: Optional[List[str]] = None,
        banned_phrases: Optional[List[str]] = None,
        max_tokens: int = 20,
        temperature: float = 0.9,
        top_p: float = 0.8
    ) -> str:
        """
        Generate a creative and abstract clue for a given description.

        Args:
            description (str): The main description for which the clue is generated.
            other_cards (Optional[List[str]]): Descriptions of other cards, if any.
            banned_phrases (Optional[List[str]]): Phrases that should be avoided in the clue.
            max_tokens (int): Maximum number of tokens for the generated clue.
            temperature (float): Sampling temperature.
            top_p (float): Nucleus sampling.

        Returns:
            str: A creative and abstract clue.
        """
        if banned_phrases is None:
            banned_phrases = ["whispers of grace"]

        other_cards_description = " | ".join(other_cards or [])
        prompt = (
            f"You are a storyteller in a creative and abstract game called Dixit. Your goal is to give a clue for "
            f"the following image description: '{description}'. The clue should be poetic, abstract, and evocative, "
            f"yet concise and complete. Generate a unique phrase or word (1-3 words) that captures the essence of your card while making it challenging for others to guess correctly. "
            f"Avoid using common phrases or too obvious clues. Think creatively to strike a balance between clarity and mystery."
        )

        for attempt in range(RETRIES):
            try:
                logger.debug(f"Attempt {attempt + 1} to generate a clue.")
                response = openai.ChatCompletion.create(
                    model=self.model_name,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens,
                    temperature=temperature,
                    top_p=top_p,
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
                    return "Abstract Clue"
            except Exception as e:
                logger.error(f"An unexpected error occurred: {e}")
                return "Abstract Clue"

        logger.warning("Returning fallback clue after all retries.")
        return "Fallback Clue"
