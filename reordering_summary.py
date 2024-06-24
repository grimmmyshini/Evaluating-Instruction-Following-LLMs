from pathlib import Path
import json
import matplotlib.pyplot as plt
from collections import Counter

# Directories to process (manually listed, excluding those with partwise and partwise_aided suffix)
directories = [
    'mathwell_combi_0',
    'mathwell_combi_1',
    'mathwell_combi_2',
    'mathwell_combi_3',
    'mathwell_combi_4',
    'mathwell_combi_5'
]
# Base directory path
base_dir = Path('datasets/ReorderingAnalysis_Ifeval/response')

# Models to process
models = ['gemma', 'llama3', 'mistral']
filename = 'eval_results_strict.jsonl'

# Function to read jsonl file
def read_jsonl_file(filepath):
    with filepath.open('r', encoding='utf-8') as file:
        return [json.loads(line) for line in file]

# Function to calculate the percentage of True values in follow_instruction_list
def calculate_true_percentage(follow_instruction_list):
    true_count = sum(follow_instruction_list)
    total_count = len(follow_instruction_list)
    return (true_count / total_count * 100) if total_count > 0 else 0

def truncate_to_two_decimals(value):
    return int(value * 100) / 100.0

# Initialize histogram data
histogram_data = {model: {0.0: 0, 33.33: 0, 66.66: 0, 100.0: 0} for model in models}

def update_hist_data(max_min_differences, model):
    for diff in max_min_differences:
        histogram_data[model][diff] += 1

# Loop through each model
for model in models:
    print(f"Processing model: {model}")

    # Read the output.jsonl files for the current model from all directories and store percentages
    all_percentages = []

    for directory in directories:
        path = base_dir / directory / model / filename
        content = read_jsonl_file(path)
        percentages = [calculate_true_percentage(item['follow_instruction_list']) for item in content]
        all_percentages.append(percentages)

    # Ensure all jsonl files have the same number of datapoints
    num_datapoints = len(all_percentages[0])
    for percentages in all_percentages:
        assert len(percentages) == num_datapoints, "Mismatch in number of datapoints"

    # Calculate the difference between the maximum and minimum percentages for each datapoint
    max_min_differences = []

    for i in range(num_datapoints):
        percentages = [percentages[i] for percentages in all_percentages]
        max_min_difference = max(percentages) - min(percentages)
        max_min_difference_truncated = truncate_to_two_decimals(max_min_difference)
        max_min_differences.append(max_min_difference_truncated)

    # Update histogram data for the current model
    update_hist_data(max_min_differences, model)

    # Output the differences for the current model (optional)
    for idx, difference in enumerate(max_min_differences):
        print(f"Datapoint {idx + 1}: Max-Min Percentage Difference = {difference:.2f}%")
    
    print("\n")  # Add a newline for readability between models

# Generate and save a multi-bar histogram for all models
plt.figure(figsize=(6, 5))

# Define width of the bars
bar_width = 0.2
# Define the positions of the bars on the x-axis
positions = list(range(len(histogram_data[models[0]].keys())))

# Plotting bars for each model
for idx, model in enumerate(models):
    differences, frequencies = zip(*sorted(histogram_data[model].items()))
    print(differences, frequencies)
    bar_positions = [p + bar_width * idx for p in positions]
    plt.bar(bar_positions, frequencies, width=bar_width, label=model)

# Add x-ticks and labels
plt.xlabel('Max-Min Percentage Difference')
plt.ylabel('Frequency')
plt.title('Histogram of Max-Min Percentage Differences for All Models')
plt.xticks([p + bar_width * (len(models) / 2) for p in positions], differences)

# Add legend
plt.legend()

# Save the plot
histogram_file = base_dir / 'reordering_hist.pdf'
plt.savefig(histogram_file)
plt.close()

print(f"Histogram saved to {histogram_file}")

