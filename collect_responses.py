import json
from utils.chat import chat

# Function to process each prompt and get a response
def process_prompt(model, prompt):
    response = chat(model, message=prompt)
    return response

# Load the JSON file
def load_prompts(file_path):
    with open(file_path, 'r') as file:
        prompts=[]
        for line in file:
            current_line = line.strip()
            prompts.append(json.loads(current_line))
    return prompts
        # current_json = ''
        #     for line in input_file:
        #         current_json += line.strip()
        #         try:
        #             entry = json.loads(current_json)
        #             instructions.append({"instruction": entry["instruction"]})
        #             current_json = ''
        #         except json.JSONDecodeError:
        #             # Continue reading lines until a complete JSON object is formed
        #             continue

# Save responses to a JSON file
def save_responses(responses, output_file):
    with open(output_file, 'w') as file:
        json.dump(responses, file, indent=4)

# Main function
def main():
    # Path to the JSON file
    input_file_path = 'InfoBench/extracted_instructions.jsonl'
    output_file_path = 'InfoBench/responses_gemma.json'
    model = "gemma"
    # Load prompts
    prompts = load_prompts(input_file_path)
    
    # Process each prompt and collect responses
    responses = []
    for prompt in prompts:
        response = process_prompt(model, prompt['instruction'])
        responses.append({'instruction': prompt['instruction'], 'response': response})
    
    # Save all responses to the output file
    save_responses(responses, output_file_path)
    print("Responses saved to", output_file_path)

if __name__ == "__main__":
    main()
