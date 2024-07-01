#!/bin/bash

directories=(
    "datasets/MATHWELL_Info_Ifeval"
    "datasets/MMLU_Info_Ifeval"
    "datasets/MATHWELL_Ifeval"
    "datasets/MMLU_Ifeval"
    "datasets/InfoToIfeval/response/infoToIfeval"
    "datasets/IfevalToInfo/response/ifeval_subset"
    "datasets/MMLU_Ifeval_Complex"
    "datasets/ReorderingAnalysis_Ifeval"
)



for BASE_DIR in "${directories[@]}"; do
    find "$BASE_DIR" -type f -name "output.jsonl" | while read -r OUTPUT_JSONL_FILE; do
        RUN_DIR=$(dirname "$OUTPUT_JSONL_FILE")
        if [[ $RUN_DIR == */run* ]]; then
            PARENT_DIR=$(dirname "$RUN_DIR")
        else
            PARENT_DIR="$RUN_DIR"
        fi

        GRAND_PARENT_DIR=$(dirname "$PARENT_DIR")
        GRAND_PARENT_DIR_NAME=$(basename "$GRAND_PARENT_DIR")

        # Remove "_partwise" and "_partwise_aided" suffixes if present
        CLEANED_DIR_NAME=${GRAND_PARENT_DIR_NAME/_aided/}
        CLEANED_DIR_NAME=${CLEANED_DIR_NAME/_partwise/}

        INPUT_DATA_FILE="$BASE_DIR/$CLEANED_DIR_NAME.jsonl"
        OUTPUT_JSONL_DIR="$RUN_DIR"

        if [[ -f "$INPUT_DATA_FILE" ]]; then
            echo "Processing: $GRAND_PARENT_DIR_NAME"

            python3 -m instruction_following_eval.evaluation_main \
                --input_data="$INPUT_DATA_FILE" \
                --input_response_data="$OUTPUT_JSONL_FILE" \
                --output_dir="$OUTPUT_JSONL_DIR"
        else
            echo "Input data file not found: $INPUT_DATA_FILE"
        fi
    done
done
