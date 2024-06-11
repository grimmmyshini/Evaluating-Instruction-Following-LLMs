import json

# def extract_instructions(input_file, output_file):
#     instructions = []
#     with open(input_file, 'r') as f:
#         for line in f:
#             data = json.loads(line)
#             instruction = data.get('instruction', None)
#             if instruction:
#                 instructions.append(instruction)
    
#     with open(output_file, 'w') as f:
#         for instruction in instructions:
#             f.write(instruction + '\n')

# if __name__ == "__main__":
#     input_file = "instruction_following_eval/data/IFEvaltoInfo.jsonl"
#     output_file = "instruction_following_eval/data/instructions.txt"
#     extract_instructions(input_file, output_file)

# Path to the input JSONL file
input_file_path = "instruction_following_eval/data/IFEvaltoInfo.jsonl"

# Path to the output JSONL file
output_file_path = "instruction_following_eval/data/extracted_instructions.jsonl"

# Read the input JSONL file
instructions = []

# Read the input JSONL file
with open(input_file_path, 'r') as input_file:
    current_json = ''
    for line in input_file:
        current_json += line.strip()
        try:
            entry = json.loads(current_json)
            instructions.append({"instruction": entry["instruction"]})
            current_json = ''
        except json.JSONDecodeError:
            # Continue reading lines until a complete JSON object is formed
            continue

# Saving the instructions to another file
with open(output_file_path, 'w') as output_file:
    for instruction in instructions:
        output_file.write(json.dumps(instruction) + '\n')