import json
import os
from pathlib import Path

from tqdm import tqdm
from chat import chat


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

    input_data = []
    # Open input and output files
    with open(input_file_path, 'r') as infile:
        while True:
            item = read_single_line(infile)

            if not item:
                break

            input_data.append(item)

    for item in tqdm(input_data):
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

            

def generate_response(input_file_path, output_path):
    with open("config.json", 'r') as file:
        data = json.load(file)

        output_path.mkdir(exist_ok=True)
        for model in data["models"]:
            output_dir_path = output_path / model
            output_dir_path.mkdir(exist_ok=True)
            if "Complex" in str(input_file_path):
                if model == "gpt4": continue
                for run in range(1, 6):
                    (output_dir_path / f"run{run}").mkdir(exist_ok=True)
                    output_file_path = output_dir_path / f"run{run}" / "output.jsonl"
                    print(f"Saving to {output_file_path}")
                    process_data(input_file_path, output_file_path, model)
            else:
                output_file_path = output_dir_path / "output.jsonl"
                print(f"Saving to {output_file_path}")
                process_data(input_file_path, output_file_path, model)
                

# input_path = Path('datasets/MMLU_Ifeval_Complex')
# output_path = Path('datasets/MMLU_Ifeval_Complex/response')

inputs = ['datasets/MMLU_Ifeval_Complex', 'datasets/MATHWELL_Ifeval', 'datasets/MMLU_Ifeval', 'datasets/IfevalToInfo/ifeval_subset.jsonl', 'datasets/InfoToIfeval/infoToIfeval.jsonl']


for input in inputs:
    print(f"Generating responses for jsonl files in {input} directory")
    input_path = Path(input)
    if input_path.is_dir():
        response_path = input_path / "response"
        files = input_path.glob("*.jsonl")
    else:
        response_path = input_path.parent / "response"
        files = [input_path]
    
    response_path.mkdir(exist_ok=True)
    for input_file_path in files:
        output_path = response_path / input_file_path.stem
        generate_response(input_file_path, output_path)