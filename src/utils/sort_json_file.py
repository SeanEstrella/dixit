import json
import re

def sort_key(key):
    """Extract numeric value from the image filename for sorting."""
    match = re.search(r'(\d+)', key)
    return int(match.group(1)) if match else key

def sort_json_file(input_file, output_file):
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    # Sort the dictionary by the numeric value in the filename
    sorted_data = dict(sorted(data.items(), key=lambda item: sort_key(item[0])))
    
    with open(output_file, 'w') as f:
        json.dump(sorted_data, f, indent=4)
    
    print(f"JSON file sorted and saved to {output_file}")

if __name__ == "__main__":
    input_file = 'data/cards_captions.json'
    output_file = 'data/cards_captions_sorted.json'
    
    sort_json_file(input_file, output_file)
