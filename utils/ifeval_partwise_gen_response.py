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
def process_data(input_file_path, output_file_path, model, mode="all"):
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
            inp = item['prompt_list'][0]
            messages = []
            response = None
            response_list = []

            if mode == "aided":
                aid = True
            
            if mode == "all":
                messages = [{"role": "user", "content": prompt}]
                response = chat(model, messages=messages)
                response_list.append(response)
            else:
                for i, instr in enumerate(item['prompt_list']):
                    if aid and i > 1:
                        content = instr.strip() + "\nFollow all pervious requests as well."
                    else:
                        content = instr.strip()
                    messages.append({"role": "user", "content": content})
                    response = chat(model, messages=messages)
                    response_list.append(response)
                    messages.append({"role": "assistant", "content": response})

            new_entry = {
                "prompt": prompt,
                "response": response,
                "response_list": response_list
            }
            with open(output_file_path, 'a') as outfile:
                outfile.write(json.dumps(new_entry) + '\n')
            processed_prompts.add(prompt)

            

def generate_response(input_file_path, output_path, run=None, mode="all"):
    with open("config.json", 'r') as file:
        data = json.load(file)

        output_path.mkdir(exist_ok=True)
        for model in data["models"]:
            if "gpt" in model: continue
            print(f"Running model {model}")
            output_dir_path = output_path / model
            output_dir_path.mkdir(exist_ok=True)
            if run is None:
                output_file_path = output_dir_path / "output.jsonl"
            else:
                run_path = output_dir_path / f"run{run}"
                run_path.mkdir(exist_ok=True)
                output_file_path = run_path / "output.jsonl"
            process_data(input_file_path, output_file_path, model, mode=mode)

# input_path = Path('datasets/MMLU_Ifeval_Complex')
# output_path = Path('datasets/MMLU_Ifeval_Complex/response')

input_dirs = ['datasets/ReorderingAnalysis_Ifeval']

for run in range(1, 6):
    for input_dir in input_dirs:
        print(f"Generating responses for jsonl files in {input_dir} directory")
        input_path = Path(input_dir)
        response_path = input_path / "response"
        response_path.mkdir(exist_ok=True)
        for input_file_path in input_path.glob("*.jsonl"):
            output_path = response_path / input_file_path.stem
            generate_response(input_file_path, output_path, run=run)
            output_path = response_path / (input_file_path.stem + "_partwise")
            generate_response(input_file_path, output_path, run=run, mode="step")
            output_path = response_path / (input_file_path.stem + "_partwise_aided")
            generate_response(input_file_path, output_path, run=run, mode="aided")