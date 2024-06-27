import json
import os
from pathlib import Path

from tqdm import tqdm
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

            

def generate_response(input_file_path, output_path, run=None):
    with open("config.json", 'r') as file:
        data = json.load(file)

        output_path.mkdir(exist_ok=True)
        for model in data["models"]:
            if "gpt" in model: continue # FIXME: Remove line
            print(f"Running model {model}")
            output_dir_path = output_path / model
            output_dir_path.mkdir(exist_ok=True)
            if run is None:
                output_file_path = output_dir_path / "output.jsonl"
            else:
                (output_dir_path / f"run{run}").mkdir(exist_ok=True)
                output_file_path = output_dir_path / f"run{run}" / "output.jsonl"
            process_data(input_file_path, output_file_path, model)

# input_path = Path('datasets/MMLU_Ifeval_Complex')
# output_path = Path('datasets/MMLU_Ifeval_Complex/response')

input_dirs = ['datasets/MMLU_Ifeval_Complex'] #, 'datasets/MATHWELL_Ifeval', 'datasets/MMLU_Ifeval', 'datasets/InfoToIfeval', 'datasets/ReorderingAnalysis_Ifeval']

for run in range(1, 6):
    print(f"\n====================Run {run}==================\n")
    for input_dir in input_dirs:
        print(f"Generating responses for jsonl files in {input_dir} directory")
        input_path = Path(input_dir)
        response_path = input_path / "response"
        response_path.mkdir(exist_ok=True)
        for input_file_path in input_path.glob("*.jsonl"):
            output_path = response_path / input_file_path.stem
            generate_response(input_file_path, output_path, run=run)