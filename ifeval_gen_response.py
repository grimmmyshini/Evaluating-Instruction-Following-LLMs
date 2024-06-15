import json
import os
from pathlib import Path
from utils.chat import chat


# Function to read a single line from JSONL file
def read_single_line(file):
    line = file.readline()
    if line:
        return json.loads(line)
    return None

# Function to process data one line at a time and create a new JSONL file
def process_data(input_file_path, output_file_path, model):
    # Ensure the output file exists and create an empty set for processed prompts
    if os.path.exists(output_file_path):
        with open(output_file_path, 'r') as file:
            processed_data = [json.loads(line) for line in file]
            processed_prompts = {entry['prompt'] for entry in processed_data}
    else:
        processed_prompts = set()

    # Open input and output files
    with open(input_file_path, 'r') as infile:
        while True:
            item = read_single_line(infile)
            if not item:
                break
            
            prompt = item['prompt']
            if prompt not in processed_prompts:
                response = chat(model, message=prompt)
                new_entry = {
                    "prompt": prompt,
                    "response": response
                }
                with open(output_file_path, 'a') as outfile:
                    outfile.write(json.dumps(new_entry) + '\n')
                processed_prompts.add(prompt)

# Example usage
input_file_path = Path('datasets/InfoToIfeval/infoToIfeval.jsonl')
output_path = Path('datasets/InfoToIfeval/response')

with open("config.json", 'r') as file:
    data = json.load(file)

    output_path.mkdir(exist_ok=True)
    for model in data["models"]:
        print(f"Running model {model}")
        output_dir_path = output_path / model
        output_file_path = output_dir_path / (input_file_path.stem + f"_{model}" + ".jsonl")
        process_data(input_file_path, output_file_path, model)
