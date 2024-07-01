#!/bin/bash

# Base directory for input data and response data
base_dir="datasets/MMLU_Ifeval_Complex"
input_data_dir="${base_dir}"
response_data_dir="${base_dir}/response"

# Iterate over all directories in response_data_dir
for dir in ${response_data_dir}/mat_d*; do
    if [ -d "$dir" ]; then
        # Extracting the directory name
        dir_name=$(basename $dir)
        
        # Path to the input data file
        input_data_file="${input_data_dir}/${dir_name}.jsonl"
        
        # Iterate over all models in the current directory
        for model_dir in ${dir}/*; do
            if [ -d "$model_dir" ]; then
                # Extracting the model name
                model_name=$(basename $model_dir)
                
                for run_dir in ${model_dir}/*; do
                    # Path to the response data file
                    response_data_file="${run_dir}/output.jsonl"
                    output_dir="${run_dir}"

                    # Ensure output directory exists
                    mkdir -p $output_dir

                    # Run the python command
                    python3 -m instruction_following_eval.evaluation_main \
                        --input_data=$input_data_file \
                        --input_response_data=$response_data_file \
                        --output_dir=$output_dir
                done
            fi
        done
    fi
done