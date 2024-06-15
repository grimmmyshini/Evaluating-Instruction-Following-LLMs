from datasets import load_dataset
import json

# Load the dataset
dataset = load_dataset("kqsong/InFoBench")

# Define the output file name
output_file = "datasets/InfoBench/dataset.jsonl"

# Open the file in write mode
with open(output_file, 'w') as f:
    # Iterate over each sample in the dataset
    for sample in dataset['train']:
        # Convert the sample to a JSON string and write it to the file
        f.write(json.dumps(sample) + '\n')

print(f"Dataset saved to {output_file}")