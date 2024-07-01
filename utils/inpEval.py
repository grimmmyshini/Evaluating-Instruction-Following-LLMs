import json

# Assuming 'data1.json' contains the list of dictionaries with 'instruction' and 'response'
# and 'data2.json' contains the list of dictionaries that need the 'response' field added
with open('datasets/IfevalToInfo/response/IFEvaltoInfo/gpt4o/responses.jsonl', 'r') as file:
    data1 = json.load(file)

# Create a dictionary to map 'instruction' to 'response' for quick lookup
instruction_to_response = {item['instruction']: item['response'] for item in data1}

updated_data = []
with open('datasets/IfevalToInfo/IFEvaltoInfo.jsonl', 'r') as file:
    for line in file:
        item = json.loads(line)
        instruction = item['instruction']
        if instruction in instruction_to_response:
            item['output'] = instruction_to_response[instruction]
        updated_data.append(item)

# Saving the modified data2 to a new file or you can overwrite the old one
with open('datasets/IfevalToInfo/response/IFEvaltoInfo/gpt4o/output.jsonl', 'w', encoding='utf-8') as file:
    for item in updated_data:
        json.dump(item, file, ensure_ascii=False)
        file.write('\n')

print("The merge is complete.")