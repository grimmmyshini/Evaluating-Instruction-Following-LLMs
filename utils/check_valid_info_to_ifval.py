import json
import os

def process_jsonl_files(input_file_path, valid_file_path, invalid_file_path):
    processed_lines = set()
    
    # Read already processed lines from valid and invalid files
    if os.path.exists(valid_file_path):
        with open(valid_file_path, 'r') as valid_file:
            for line in valid_file:
                try:
                    data = json.loads(line)
                    processed_lines.add(line)
                except json.JSONDecodeError:
                    continue

    if os.path.exists(invalid_file_path):
        with open(invalid_file_path, 'r') as invalid_file:
            for line in invalid_file:
                try:
                    data = json.loads(line)
                    processed_lines.add(line)
                except json.JSONDecodeError:
                    continue

    # Read and process the input file
    with open(input_file_path, 'r') as input_file:
        for line_number, line in enumerate(input_file, start=1):
            if line.strip() == "":
                continue  # skip empty lines

            if line in processed_lines:
                continue  # skip already processed lines
            
            try:
                data = json.loads(line)
                if 'instruction_id_list' in data and isinstance(data['instruction_id_list'], list):
                    print(f"Line {line_number}:")
                    print(json.dumps(data, indent=4))
                    if data['instruction_id_list']:
                        user_input = input("Do you want to mark it as valid? (default: Yes) [Y/n]: ").strip().lower()
                        if user_input in ['n', 'no']:
                            with open(invalid_file_path, 'a') as invalid_file:
                                invalid_file.write(json.dumps(data) + '\n')
                        else:
                            with open(valid_file_path, 'a') as valid_file:
                                valid_file.write(json.dumps(data) + '\n')
                    else:
                        user_input = input("Do you want to mark it as valid? (default: No) [y/N]: ").strip().lower()
                        if user_input in ['y', 'yes']:
                            with open(valid_file_path, 'a') as valid_file:
                                valid_file.write(json.dumps(data) + '\n')
                        else:
                            with open(invalid_file_path, 'a') as invalid_file:
                                invalid_file.write(json.dumps(data) + '\n')
                else:
                    print(f"Line {line_number} does not have a valid instruction_id_list field.")
                    with open(invalid_file_path, 'a') as invalid_file:
                        invalid_file.write(json.dumps(data) + '\n')
            except json.JSONDecodeError:
                print(f"Invalid JSON line at line {line_number}: {line.strip()}")
                with open(invalid_file_path, 'a') as invalid_file:
                    invalid_file.write(line)

input_file_path = 'datasets/InfoBench/infoToIfeval.jsonl'
valid_file_path = 'datasets/InfoBench/infoToIfeval_valid.jsonl'
invalid_file_path = 'datasets/InfoBench/infoToIfeval_invalid.jsonl'
process_jsonl_files(input_file_path, valid_file_path, invalid_file_path)
