from pathlib import Path
import json
import matplotlib.pyplot as plt
import numpy as np

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

def get_stat_percentages(model_dir):
    all_percentages = []
    run_list = list(model_dir.glob("run*"))
    for run_dir in run_list:
        content = read_jsonl_file(run_dir / filename)
        percentages = [calculate_true_percentage(item['follow_instruction_list']) for item in content]
        all_percentages.append(percentages)
    
    num_datapoints = len(all_percentages[0])
    for percentages in all_percentages:
        assert len(percentages) == num_datapoints, "Mismatch in number of datapoints"

    all_mean = []
    all_std = []
    all_ptp = []
    for i in range(num_datapoints):
        percentages = [percentages[i] for percentages in all_percentages]
        all_mean.append(np.mean(percentages))
        all_std.append(np.std(percentages))
        all_ptp.append(np.ptp(percentages))
    
    print("PTP:", " ".join([f"{item:.2f}" for item in all_ptp]))
    
    return all_mean, all_std, all_ptp


def truncate_to_two_decimals(value):
    return int(value * 100) / 100.0

# Initialize histogram data
histogram_data = {model: {} for model in models}

def update_hist_data(max_min_differences, model):
    for diff in max_min_differences:
        if diff not in histogram_data[model]:
            for mod in models:
                histogram_data[mod][diff] = 0
        histogram_data[model][diff] += 1

# Loop through each model
for model in models:
    print(f"Processing model: {model}")

    # Read the output.jsonl files for the current model from all directories and store percentages
    all_means = []
    all_stds = []
    all_ptps = []

    for directory in directories:
        path = base_dir / directory / model
        means, stds, ptps = get_stat_percentages(path)
        all_means.append(means)
        all_stds.append(stds)
        all_ptps.append(ptps)
        

    # Ensure all jsonl files have the same number of datapoints
    num_datapoints = len(all_means[0])
    for means, stds, ptps in zip(all_means, all_stds, all_ptps):
        assert len(means) == num_datapoints and len(stds) == num_datapoints and len(ptps) == num_datapoints, "Mismatch in number of means/stds/ptps"

    # Calculate the difference between the maximum and minimum percentages for each datapoint
    max_min_differences = []
    max_min_stds = []
    max_min_ptps = []

    for i in range(num_datapoints):
        percentages = [percentages[i] for percentages in all_means]
        stds = [std[i] for std in all_stds]
        ptps = [ptp[i] for ptp in all_ptps]
        max_ind = np.argmax(percentages)
        min_ind = np.argmin(percentages)
        max_min_difference = percentages[max_ind] - percentages[min_ind]
        max_min_std = np.sqrt(np.square(stds[max_ind]) + np.square(stds[min_ind]))
        max_min_ptp = ptps[max_ind] + ptps[min_ind]
        max_min_difference_truncated = truncate_to_two_decimals(max_min_difference)
        max_min_std_truncated = truncate_to_two_decimals(max_min_std)
        max_min_ptp_truncated = truncate_to_two_decimals(max_min_ptp)
        max_min_differences.append(max_min_difference_truncated)
        max_min_stds.append(max_min_std_truncated)
        max_min_ptps.append(max_min_ptp_truncated)

    # Update histogram data for the current model
    update_hist_data(max_min_differences, model)

    # Output the differences for the current model (optional)
    for idx, (difference, std, ptp) in enumerate(zip(max_min_differences, max_min_stds, max_min_ptps)):
        print(f"Datapoint {idx + 1}: Max-Min Percentage Difference = {difference:.2f}%   Std = {std:.2f}%   PTP = {ptp:.2f}%")
    
    print(f"Max std_dev: {np.max(max_min_stds)}   ptp:{np.max(max_min_ptps)}\n")

# Generate and save a multi-bar histogram for all models
plt.figure(figsize=(6, 5))

# Define width of the bars
bar_width = 0.2
# Define the positions of the bars on the x-axis
positions = list(range(len(histogram_data[models[0]].keys())))

# Plotting bars for each model
colors = ["#84DCCF", "#3A405A", "#EA526F"]
for idx, model in enumerate(models):
    differences, frequencies = zip(*sorted(histogram_data[model].items()))
    frequencies = np.array(frequencies)
    freq_pct = frequencies / np.sum(frequencies) * 100
    print(differences, freq_pct, frequencies)
    bar_positions = [p + bar_width * idx for p in positions]
    plt.bar(bar_positions, freq_pct, width=bar_width, label=model, color=colors[idx])

# Add x-ticks and labels
plt.xlabel('Difference in Per Prompt Acc.')
plt.ylabel('% datapoints')
plt.title('Freq. of Diff. in Per Prompt Acc. per Model with Instr. Reordering')
plt.xticks([p + bar_width * (len(models) / 2) for p in positions], differences)

# Add legend
plt.legend()
plt.tight_layout()

# Save the plot
histogram_file = base_dir / 'reordering_hist.pdf'
plt.savefig(histogram_file)
plt.close()

print(f"Histogram saved to {histogram_file}")

