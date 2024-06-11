import json

# Define the path to the JSON Lines file and the output JSON file
input_jsonl_path = 'finalInput.jsonl'
output_json_path = 'InfoBench/model/output.json'

# Read the JSON Lines file and collect all objects into a list
data = []
with open(input_jsonl_path, 'r', encoding='utf-8') as file:
    for line in file:
        json_object = json.loads(line)
        data.append(json_object)

# Write the list of JSON objects to a standard JSON file
with open(output_json_path, 'w', encoding='utf-8') as file:
    json.dump(data, file, indent=4, ensure_ascii=False)

print(f"Conversion complete. The JSON file has been saved to {output_json_path}.")