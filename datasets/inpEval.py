# import json

# # Load the JSON file containing prompts and responses
# def load_responses(file_path):
#     with open(file_path, 'r') as file:
#         responses = json.load(file)
#     return responses

# # Load the JSONL file containing objects
# def load_jsonl(file_path):
#     with open(file_path, 'r') as file:
#         lines = file.readlines()
#     objects = [json.loads(line.strip()) for line in lines]
#     return objects

# # Save the merged JSONL file
# def save_jsonl(objects, output_file_path):
#     with open(output_file_path, 'w') as file:
#         for obj in objects:
#             file.write(json.dumps(obj) + '\n')

# # Main function
# def main():
#     # Paths to the input files and the output file
#     responses_file_path = 'InfoBench/responses.json'
#     jsonl_file_path = 'instruction_following_eval/data/IFEvaltoInfo.jsonl'
#     output_file_path = 'finalInput.jsonl'
    
#     # Load responses and JSONL objects
#     responses = load_responses(responses_file_path)
#     objects = load_jsonl(jsonl_file_path)
    
#     # Create a dictionary for quick lookup of responses by instruction
#     response_dict = {item['instruction']: item['response'] for item in responses}
    
#     # Merge responses into JSONL objects
#     for obj in objects:
#         instruction = obj.get('instruction')
#         if instruction in response_dict:
#             obj['output'] = response_dict[instruction]
    
#     # Save the merged objects to the output JSONL file
#     save_jsonl(objects, output_file_path)

# if __name__ == "__main__":
#     main()
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