# #!/bin/bash

# # Predefined list of directories
# directories=(
#     "datasets/MMLU_Ifeval_Complex/response"
#     # Add more directories as needed
# )

# # Iterate through each directory in the list
# for dir in "${directories[@]}"; do
#     # Find all output.jsonl files within the directory at any depth
#     files=$(find "$dir" -type f -name "output.jsonl")

#     # Iterate through each found file
#     for file in $files; do
#         # Get the parent directory of the file
#         parent_dir=$(dirname "$file")

#         # Determine the model based on the parent directory name
#         if [[ "$parent_dir" == *"llama3"* ]]; then
#             model="mistral"
#         else
#             model="llama3"
#         fi

#         # Run the Python command
#         echo "Evaluating $file"
#         python3 -m instruction_following_eval.evaluation_main --input_data=datasets/MMLU_Ifeval/mmlu_ifval.jsonl --input_response_data=datasets/MMLU_Ifeval/response/mmlu_ifval/mistral/output.jsonl --output_dir=datasets/MMLU_Ifeval/response/mmlu_ifval/mistral
#     done
# done


# #!/bin/bash

# # Base directory for input data and response data
# input_data_dir="datasets/MMLU_Ifeval_Complex/response"
# output_base_dir="datasets/MMLU_Ifeval_Complex/response"

# # Iterate over all directories in input_data_dir
# for dir in ${input_data_dir}/mat_d*; do
#     if [ -d "$dir" ]; then
#         # Extracting the directory name
#         dir_name=$(basename $dir)
        
#         # Iterate over all models in the current directory
#         for model_dir in ${dir}/*; do
#             if [ -d "$model_dir" ]; then
#                 # Extracting the model name
#                 model_name=$(basename $model_dir)
                
#                 # Set the path for the JSON input and output files
#                 input_json="${dir}/${dir_name}.jsonl"
#                 output_json="${model_dir}/output.jsonl"
#                 output_dir="${output_base_dir}/${dir_name}/${model_name}"
                
#                 # Ensure output directory exists
#                 mkdir -p $output_dir
                
#                 # Run the python command
#                 python3 -m instruction_following_eval.evaluation_main \
#                     --input_data=$input_json \
#                     --input_response_data=$output_json \
#                     --output_dir=$output_dir
#             fi
#         done
#     fi
# done

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
                
                # Path to the response data file
                response_data_file="${model_dir}/output.jsonl"
                output_dir="${model_dir}"
                
                # Ensure output directory exists
                mkdir -p $output_dir
                
                # Run the python command
                python3 -m instruction_following_eval.evaluation_main \
                    --input_data=$input_data_file \
                    --input_response_data=$response_data_file \
                    --output_dir=$output_dir
            fi
        done
    fi
done