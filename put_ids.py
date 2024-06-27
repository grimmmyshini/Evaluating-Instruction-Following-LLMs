# import json

# input_file_path = 'datasets/IfevalToInfo/response/IFEvaltoInfo/gemma/output.jsonl'
# output_file_path = 'datasets/IfevalToInfo/response/IFEvaltoInfo/gemma/output_with_ids.jsonl'

# with open(input_file_path, 'r') as infile, open(output_file_path, 'w') as outfile:
#     for i, line in enumerate(infile, start=1):
#         record = json.loads(line)
#         record['id'] = i
#         outfile.write(json.dumps(record) + '\n')

# print(f"Updated file saved to {output_file_path}")

import json
import os

base_dir = 'datasets/IfevalToInfo/response/IFEvaltoInfo'

# List of model directories
model_dirs = [
    'gemma',
    'gpt4',
    'gpt4o',
    'llama3',
    'mistral'
]

for model in model_dirs:
    input_file_path = os.path.join(base_dir, model, 'llama3_DecomposeEval.jsonl')
    output_file_path = os.path.join(base_dir, model, 'llama3_DecomposeEval.jsonl')
    
    # Check if the input file exists
    if not os.path.exists(input_file_path):
        print(f"Input file {input_file_path} not found.")
        continue
    str = ""
    with open(input_file_path, 'r') as infile:
        for i, line in enumerate(infile, start=1):
            record = json.loads(line)
            record['id'] = f"{i}"
            str += json.dumps(record) + '\n'
    with open(output_file_path, 'w') as outfile:
        outfile.write(str)

    print(f"Updated file for {model} saved to {output_file_path}")
