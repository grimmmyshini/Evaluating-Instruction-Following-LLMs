import json

def convert_jsonl_to_pretty_jsonl(input_file_path, output_file_path):
    with open(input_file_path, 'r') as input_file, open(output_file_path, 'w') as output_file:
        for line in input_file:
            try:
                data = json.loads(line.strip())
                pretty_json = json.dumps(data, indent=4)
                output_file.write(pretty_json + '\n')
            except json.JSONDecodeError:
                print(f"Invalid JSON line: {line.strip()}")

# Example usage
input_file_path = 'datasets/InfoBench/infoToIfeval_invalid.jsonl'
output_file_path = 'datasets/InfoBench/infoToIfeval_invalid_pretty.jsonl'
convert_jsonl_to_pretty_jsonl(input_file_path, output_file_path)
