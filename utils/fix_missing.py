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

    with open(json_file_path, 'r') as json_file:
        existing_records = json.load(json_file)

    cnt = -1
    start = 0
    idx = -1
    records = []
    index = 0
    exist_count = 0
    while index < len(existing_records):
        row = existing_records[index]
        if row['difficulty'] != difficulty and cnt < 0 or exist_count > 49:
            records.append(row)
            index += 1
            continue

        if row['difficulty'] == difficulty and cnt < 0:
            cnt = 201
            continue

        if row['key'] == cnt:
            records.append(row)
            index += 1
            exist_count += 1
        else:
            ch = 'A'

            while ch != 'y':

                idx += 1
                if start + idx >= len(df):
                    print("PRompts over!!!")
                    break
                if 'Which of the following' in df.loc[start + idx]['prompt'] or 'which of the following' in df.loc[start + idx]['prompt'] or df.loc[start + idx]['prompt'][-1] == ':':
                    continue
                print(df.loc[start + idx]['prompt'])
                print('Ok? (y for yes, otherwise any key)')
                ch = input()

            if start + idx >= len(df):
                print("PRompts over!!!")
                break

            record = {
                'key': cnt,
                'prompt': df.loc[start + idx]['prompt'],
                'answer': df.loc[start + idx][get_ans_idx(df.loc[start + idx]['ans'])],
                'difficulty': difficulty  # high -> more difficult
            }
            records.append(record)
        cnt += 1

    with open(json_file_path, 'w') as json_file:
        json.dump(records, json_file, indent=4)


def extend_elementary(csv_file_path, json_file_path, difficulty):
    df = pd.read_csv(csv_file_path)

    with open(json_file_path, 'r') as json_file:
        existing_records = json.load(json_file)

    cnt = len(existing_records)
    start = 5
    idx = -1
    while cnt <= 250:
        ch = 'A'

        while ch != 'y':

            idx += 1
            if start + idx >= len(df):
                print("PRompts over!!!")
                break
            if 'Which of the following' in df.loc[start + idx]['prompt'] or 'which of the following' in df.loc[start + idx]['prompt'] or df.loc[start + idx]['prompt'][-1] == ':':
                continue
            print(df.loc[start + idx]['prompt'])
            print('Ok? (y for yes, otherwise any key)')
            ch = input()
            # ch = 'y'

        if start + idx >= len(df):
            print("Prompts over!!!")
            break

        record = {
            'key': cnt,
            'prompt': df.loc[start + idx]['prompt'],
            'answer': df.loc[start + idx][get_ans_idx(df.loc[start + idx]['ans'])],
            'difficulty': difficulty  # high -> more difficult
        }
        existing_records.append(record)
        cnt += 1

    with open(json_file_path, 'w') as json_file:
        json.dump(existing_records, json_file, indent=4)


json_file_mmlu = '/home/grimmyshini/CS4NLP-Project/datasets/fomatted_prompts_mmlu.json'

base_path_mmlu = '/home/grimmyshini/CS4NLP-Project/datasets/MMLU-Math'

# csv_to_json_mmlu(base_path_mmlu + '/test/abstract_algebra_test.csv', json_file_mmlu, 4)
# csv_to_json_mmlu(base_path_mmlu + '/test/college_mathematics_test.csv', json_file_mmlu, 3)
# csv_to_json_mmlu(base_path_mmlu + '/test/high_school_mathematics_test.csv', json_file_mmlu, 2)
# csv_to_json_mmlu(base_path_mmlu + '/test/high_school_statistics_test.csv', json_file_mmlu, 2)
# csv_to_json_mmlu(base_path_mmlu +
#                  '/test/elementary_mathematics_test.csv', json_file_mmlu, 1)

extend_elementary(base_path_mmlu +
                 '/test/elementary_mathematics_test.csv', json_file_mmlu, 1)
