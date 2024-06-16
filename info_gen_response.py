import json
import os
from pathlib import Path
from utils.chat import chat
from tqdm import tqdm

def gen_infobench_response(input_file : str, output_dir : str, model : str):
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    output_path /= model
    output_path.mkdir(exist_ok=True)
    output_file = output_path / Path(input_file).name
    # Helper function to read JSONL file into a list of dictionaries
    def read_jsonl(file_path):
        with open(file_path, 'r') as f:
            return [json.loads(line.strip()) for line in f]

    # Helper function to write dictionary as JSONL line to a file
    def append_jsonl(file_path, data):
        with open(file_path, 'a') as f:
            f.write(json.dumps(data) + '\n')

    # Read input and output files
    input_data = read_jsonl(input_file)
    output_data = read_jsonl(output_file) if output_file.exists() else []

    # Extract existing IDs from the output file
    existing_messages = {(item['input'] + "\n" + item['instruction']) for item in output_data}

    # Process each data point in the input file
    for i, data_point in enumerate(tqdm(input_data)):
        message = data_point['input'] + "\n" + data_point['instruction']
        
        if message in existing_messages:
            continue

        # Send the concatenated message to the chat API
        api_response = chat(model, message=message)

        # Update the data point with the response and a unique ID
        data_point['output'] = api_response
        data_point['id'] = f"{i + 1}"
        # The evaluation script uses the id which is why we need a unique ID

        # Append the updated data point to the output file
        append_jsonl(output_file, data_point)

input_file = 'datasets/MMLU_InfoBench/mmlu_info.jsonl'
output_dir = 'datasets/MMLU_InfoBench/response'

with open("config.json", 'r') as file:
    data = json.load(file)

    for model in data["models"]:
        print(f"Running model {model}")
        gen_infobench_response(input_file, output_dir, model)
