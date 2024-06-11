import os
import pandas as pd
import json

def get_ans_idx(opt):
    if opt == 'A':
        return 'op1'
    if opt == 'B':
        return 'op2'
    if opt == 'C':
        return 'op3'
    else:
        return 'op4'

def csv_to_json_mmlu(csv_file_path, json_file_path, difficulty):
    df = pd.read_csv(csv_file_path)

    if os.path.exists(json_file_path):
        with open(json_file_path, 'r') as json_file:
            existing_records = json.load(json_file)
    else:
        existing_records = []

    records = []

    cnt = 50
    prefix = len(existing_records) + 1
    for index, row in df.iterrows():
        record = {
            'key': index + prefix,
            'prompt': row['prompt'],
            'answer': row[get_ans_idx(row['ans'])],
            'difficulty': difficulty  # high -> more difficult
        }
        records.append(record)
        cnt -= 1
        if cnt <= 0:
            break

    existing_records.extend(records)

    with open(json_file_path, 'w') as json_file:
        json.dump(existing_records, json_file, indent=4)

def csv_to_json_mathwell(csv_file_path, json_file_path, difficulty):
    df = pd.read_csv(csv_file_path)

    if os.path.exists(json_file_path):
        with open(json_file_path, 'r') as json_file:
            existing_records = json.load(json_file)
    else:
        existing_records = []

    records = []

    cnt = 100
    prefix = len(existing_records) + 1
    for index, row in df.iterrows():
        record = {
            'key': index + prefix,
            'prompt': row['question'],
            'answer': row['answer'],
            'difficulty': difficulty  # high -> more difficult
        }
        records.append(record)
        cnt -= 1
        if cnt <= 0:
            break

    existing_records.extend(records)

    with open(json_file_path, 'w') as json_file:
        json.dump(existing_records, json_file, indent=4)

json_file_mmlu = '/home/grimmyshini/CS4NLP-Project/datasets/fomatted_prompts_mmlu.json'
json_file_mathwell = '/home/grimmyshini/CS4NLP-Project/datasets/fomatted_prompts_mathwell.json'

base_path_mmlu = '/home/grimmyshini/CS4NLP-Project/datasets/MMLU-Math'
base_path_mathwell = '/home/grimmyshini/CS4NLP-Project'

# csv_to_json_mmlu(base_path_mmlu + '/test/abstract_algebra_test.csv', json_file_mmlu, 4)
# csv_to_json_mmlu(base_path_mmlu + '/test/college_mathematics_test.csv', json_file_mmlu, 3)
# csv_to_json_mmlu(base_path_mmlu + '/test/high_school_mathematics_test.csv', json_file_mmlu, 2)
# csv_to_json_mmlu(base_path_mmlu + '/test/high_school_statistics_test.csv', json_file_mmlu, 2)
# csv_to_json_mmlu(base_path_mmlu + '/val/elementary_mathematics_val.csv', json_file_mmlu, 1)

csv_to_json_mathwell(base_path_mathwell + '/MATHWELL/data/sgsm.csv', json_file_mathwell, 1)
