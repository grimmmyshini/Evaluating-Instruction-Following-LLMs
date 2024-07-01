import json
from pathlib import Path


def read_and_trim_json(file_path):
    with open(file_path, 'r') as file:
        data =  [json.loads(line) for line in file]

    with open(file_path, 'w') as file:
        for item in data[:46]:
            file.write(json.dumps(item) + '\n')


datasets = Path('datasets/MMLU_Ifeval_Complex')
evaluate_files_ifeval = datasets.rglob('*.jsonl')

for file in evaluate_files_ifeval:
    print(file)
    read_and_trim_json(file)
