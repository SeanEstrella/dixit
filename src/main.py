import os

from text_processing.description_obfuscator import DescriptionObfuscator

# Initialize the DescriptionObfuscator
description_obfuscator = DescriptionObfuscator(api_key=os.getenv("OPENAI_API_KEY"), model_name="gpt-4o-mini")

# Example description to obfuscate
description = "A pair of pink ballet shoes on a wooden floor."

# Obfuscate the description
obfuscated_description = description_obfuscator.obfuscate(description)

# Print the result
print("Original Description:", description)
print("Obfuscated Description:", obfuscated_description)