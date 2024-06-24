import json
import os

def count_tries_till_following(file_path):
    # Open and load the JSON file
    with open(file_path, 'r') as file:
        data = json.load(file)

    # Initialize counters
    count_1 = 0
    count_null = 0
    count_greater_than_1 = 0

    # Iterate through each item in the JSON data
    for item in data:
        tries = item.get("tries_till_following")

        # Check and count the values
        if tries == 1:
            count_1 += 1
        elif tries is None:
            count_null += 1
        else: 
            count_greater_than_1 += 1

    return count_1, count_null, count_greater_than_1

def save_counts_to_model_folder(model_dir, counts):
    # Save counts to a file in the model directory
    file_path = os.path.join(model_dir, "accuracy_counts.txt")
    with open(file_path, 'w') as file:
        file.write(f"Count of 'tries_till_following' == 1: {counts[0]}\n")
        file.write(f"Count of 'tries_till_following' is null: {counts[1]}\n")
        file.write(f"Count of 'tries_till_following' > 1: {counts[2]}\n")

# Base directory for the models
base_dir = 'datasets/RepromptingAnalysis/response'  # Update this with the actual base directory
model_dirs = ["gemma", "mistral", "llama3"]

# Process each model's evaluation results
for model in model_dirs:
    model_eval_path = os.path.join(base_dir, model, "eval_results.json")
    
    if os.path.exists(model_eval_path):
        # Get the counts for this model's data
        counts = count_tries_till_following(model_eval_path)
        
        # Save the counts to this model's folder
        save_counts_to_model_folder(os.path.join(base_dir, model), counts)
        print(f"Counts saved for {model}.")
    else:
        print(f"No eval_results.json found for {model}.")