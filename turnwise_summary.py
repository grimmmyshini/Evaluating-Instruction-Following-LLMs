from pathlib import Path
import json
import csv

# Define the base directory
base_dir = Path("datasets/ReorderingAnalysis_Ifeval/response")

# Function to calculate the percentage of true values in follow_instruction_list per data point
def calculate_percentage_following_instructions(file_path):
    percentages = []
    
    with file_path.open('r') as file:
        for line in file:
            data = json.loads(line)
            follow_instruction_list = data['follow_instruction_list']
            percentage = sum(follow_instruction_list) / len(follow_instruction_list) * 100
            percentages.append(percentage)
    
    return percentages

# Collecting the results
results = {}

# Iterate through each main directory (e.g., mathwell_combi_0, mathwell_combi_1, etc.)
for combi_dir in base_dir.iterdir():
    if combi_dir.is_dir():
        # Determine the suffix (if any)
        if "_partwise_aided" in combi_dir.name:
            suffix = "one at a time (aided)"
        elif "_partwise" in combi_dir.name:
            suffix = "one at a time"
        else:
            suffix = "all at once"
        
        # Initialize results for this suffix if not already present
        if suffix not in results:
            results[suffix] = {}
        
        # Iterate through each subdirectory (one for each model)
        for model_dir in combi_dir.iterdir():
            if model_dir.is_dir() and not "gpt" in model_dir.name:
                # Path to the eval_results_strict.jsonl file
                eval_file_path = model_dir / "eval_results_strict.jsonl"
                
                if eval_file_path.exists():
                    # Calculate the percentages for this file
                    percentages = calculate_percentage_following_instructions(eval_file_path)
                    
                    # Initialize results for this model if not already present
                    if model_dir.name not in results[suffix]:
                        results[suffix][model_dir.name] = []
                    
                    # Extend the model's list with the percentages
                    results[suffix][model_dir.name].extend(percentages)

# Calculate the averages for each model and suffix
averages = {}
for suffix, models in results.items():
    averages[suffix] = {}
    for model, percentages in models.items():
        averages[suffix][model] = sum(percentages) / len(percentages) if percentages else 0

# Write the results to a CSV file
csv_file = base_dir / "results.csv"
with csv_file.open('w', newline='') as file:
    writer = csv.writer(file)
    
    # Write the header
    headers = ["Model"] + list(averages.keys())
    writer.writerow(headers)
    
    # Write the data rows
    all_models = set(model for models in averages.values() for model in models)
    for model in sorted(all_models):
        row = [model] + [f"{averages[suffix].get(model, 0):.2f}" for suffix in headers[1:]]
        writer.writerow(row)

print(f"Results have been written to {csv_file}")
