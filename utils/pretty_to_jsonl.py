import json

def convert_pretty_jsonl_to_proper_jsonl(pretty_jsonl_file_path, proper_jsonl_file_path):
    with open(pretty_jsonl_file_path, 'r') as pretty_file, open(proper_jsonl_file_path, 'w') as proper_file:
        buffer = ""
        for i, line in enumerate(pretty_file):
            stripped_line = line.strip()
            if stripped_line:  # Ignore empty lines
                buffer += stripped_line
                if line.rstrip() == '}':
                    try:
                        json_data = json.loads(buffer)
                        proper_file.write(json.dumps(json_data) + '\n')
                    except json.JSONDecodeError as e:
                        print(f"JSON at {i}: {buffer}")
                        print(f"Error: {e}")
                        exit(1)
                    buffer = ""

# Example usage
pretty_jsonl_file_path = 'instruction_following_eval/data/IFEvaltoInfo.jsonl'
proper_jsonl_file_path = 'instruction_following_eval/data/IFEvaltoInfo_proper.jsonl'
convert_pretty_jsonl_to_proper_jsonl(pretty_jsonl_file_path, proper_jsonl_file_path)