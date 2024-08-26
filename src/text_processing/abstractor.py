import openai
import os
import time

class Abstractor:
    def __init__(self, api_key=None, model_name="gpt-4o-mini"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("API key is required for OpenAI")
        openai.api_key = self.api_key
        self.model_name = model_name

    def generate_creative_abstract(self, description, other_cards=None):
        other_cards_description = " | ".join(other_cards or [])

        prompt = (
            f"You are a storyteller in a creative and abstract game called Dixit. Your goal is to give a clue for "
            f"the following image description: '{description}'. The clue should be poetic, abstract, and evocative, "
            f"yet concise and complete. Please avoid using the phrase 'Whispers of Grace' or any similar phrases. "
            f"Generate a unique phrase or word (1-3 words) that captures the essence of your card while making it challenging for others to guess correctly. "
            f"Avoid using common phrases or too obvious clues. Think creatively to strike a balance between clarity and mystery."
        )

        retries = 3
        for attempt in range(retries):
            try:
                response = openai.ChatCompletion.create(
                    model=self.model_name,
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=20,
                    temperature=0.9,
                    top_p=0.8,
                )
                generated_clue = response.choices[0].message['content'].strip()

                if generated_clue.lower() != "whispers of grace":
                    return generated_clue
            except openai.error.RateLimitError:
                if attempt < retries - 1:
                    print(f"Rate limit exceeded. Retrying in {2 ** attempt} seconds...")
                    time.sleep(2 ** attempt)
                else:
                    raise
            except Exception as e:
                print(f"An error occurred: {e}")
                return "Abstract Clue"
        return "Fallback Clue"
