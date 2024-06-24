#!/bin/bash

# Predefined list of directories
directories=(
#     "datasets/InfoToIfeval/response/infobench_subset"
#     "datasets/MMLU_InfoBench/response/mmlu_info"
    "datasets/MMLU_InfoBench_Complex/response"
    # Add more directories as needed
)

# API key
api_key="ollama"

# Iterate through each directory in the list
for dir in "${directories[@]}"; do
    # Find all output.jsonl files within the directory at any depth
    files=$(find "$dir" -type f -name "output.jsonl")

    # Iterate through each found file
    for file in $files; do
        # Get the parent directory of the file
        parent_dir=$(dirname "$file")

        # Determine the model based on the parent directory name
        if [[ "$parent_dir" == *"gpt4"* ||  "$parent_dir" == *"gpt4o"* ]]; then
            model="llama3"
            echo "Evaluating $file"
            python InfoBench/evaluation.py --api_key "$api_key" --model "$model" --input "$file" --output_dir "$parent_dir" --temperature 0
        fi
    done
done