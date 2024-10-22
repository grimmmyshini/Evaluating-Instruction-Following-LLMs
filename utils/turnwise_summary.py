from pathlib import Path
import json
import csv
import numpy as np

# Define the base directory
base_dir = Path("datasets/ReorderingAnalysis_Ifeval/response/mathwell_combi_1")

# Function to calculate the percentage of true values in follow_instruction_list per data point
def calc_percentage_following_instrs(file_path):
    percentages = []
    
    with file_path.open('r') as file:
        for line in file:
            data = json.loads(line)
            follow_instruction_list = data['follow_instruction_list']
            percentage = int(sum(follow_instruction_list) == len(follow_instruction_list))
            percentages.append(percentage)
    
    return percentages

def get_avg_following_instructions(model_dir):
    all_percentages = []
    for run_dir in model_dir.glob("run*"):
        eval_file_path = run_dir / "eval_results_strict.jsonl"
        assert eval_file_path.exists(), f"{run_dir} doesnt have eval_results_strict file"
        # Calculate the percentages for this file
        percentages = calc_percentage_following_instrs(eval_file_path)

        all_percentages.append(percentages)
    
    num_datapoints = len(all_percentages[0])
    for percentages in all_percentages:
        assert len(percentages) == num_datapoints, "Mismatch in number of datapoints"

    all_sum = []
    for percentages in all_percentages:
        all_sum.append(np.sum(percentages))

    return {
        "sum" : all_sum
    }

# Collecting the results
results = {}

# Iterate through each main directory (e.g., mathwell_combi_0, mathwell_combi_1, etc.)
for suff in ["", "_partwise", "_partwise_aided"]:
    combi_dir = base_dir.parent / (base_dir.name + suff)
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
                output = get_avg_following_instructions(model_dir)

                # Initialize results for this model if not already present
                if model_dir.name not in results[suffix]:
                    results[suffix][model_dir.name] = []
                    
                    # Extend the model's list with the percentages
                results[suffix][model_dir.name].extend(output["sum"])

# Calculate the averages for each model and suffix
averages = {}
for suffix, models in results.items():
    averages[suffix] = {}
    for model, percentages in models.items():
        assert len(percentages) != 0
        print(suffix, model, len(percentages))
        averages[suffix][model] = {}
        averages[suffix][model]["mean"] = np.mean(percentages)
        averages[suffix][model]["se"] = np.std(percentages) / np.sqrt(len(percentages))
        averages[suffix][model]["ptp"] = np.ptp(percentages)
        averages[suffix][model]["std"] = np.std(percentages)

# Write the results to a CSV file
csv_file = base_dir.parent.parent / "results.csv"
with csv_file.open('w', newline='') as file:
    writer = csv.writer(file)
    
    # Write the header
    headers = ["Model"] + list(averages.keys())
    writer.writerow(headers)
    
    # Write the data rows
    all_models = set(model for models in averages.values() for model in models)
    for model in sorted(all_models):
        row = [model] + [f" {int(np.round(averages[suffix][model]["mean"])):2} ±{int(np.round(averages[suffix][model]["std"])):1}" for suffix in headers[1:]]
        writer.writerow(row)

print(f"Results have been written to {csv_file}")
