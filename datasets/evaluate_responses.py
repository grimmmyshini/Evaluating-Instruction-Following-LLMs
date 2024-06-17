import json
from pathlib import Path


def evaluate_main(response_file: Path, model_name, infobench):
    with open(response_file, 'r') as json_file:
        df = [json.loads(line) for line in json_file]

    followed = 0
    instructions_followed = 0
    total_instructions = 0
    instruction_per_prompt = 0
    total_prompts = 0
    followed_per_type = {}
    for row in df:
        if infobench:
            all_instructions = row['eval']
            instruction_labels = [item[0] for item in row['question_label']]
            follows_all = all_instructions.count(True) == len(all_instructions)
        else:
            all_instructions = row['follow_instruction_list']
            instruction_labels = row['instruction_id_list']
            follows_all = row['follow_all_instructions']

        # assert len(all_instructions) == len(instruction_labels) and len(all_instructions) != 0
        if len(all_instructions) != len(instruction_labels) or len(all_instructions) == 0:
            continue
        if follows_all:
            followed += 1
        total_prompts += 1
        instructions_followed += all_instructions.count(True)
        total_instructions += len(all_instructions)
        instruction_per_prompt += all_instructions.count(True)/len(all_instructions)
        for i, instr in enumerate(instruction_labels):
            if instr not in followed_per_type:
                followed_per_type[instr] = {"followed": 0, "count": 0}
            followed_per_type[instr]['count'] += 1
            if all_instructions[i]:
                followed_per_type[instr]['followed'] += 1

    print("Analysis results for ",  response_file.stem, " model ", model_name)
    print("Total accuracy: ", followed/total_prompts)
    print("Total instructions followed: ",
          instructions_followed, " out of ", total_instructions)
    print("Instruction followed per prompt: ",
          instruction_per_prompt/total_prompts)
    print("Accuracy per instruction type:\n")
    for key, item in followed_per_type.items():
        print(key, " : ", item['followed']/item['count'])
    print("\n\n")


datasets = Path('/home/grimmyshini/CS4NLP-Project/datasets')
evaluate_files_info = datasets.rglob('*_DecomposeEval.jsonl')
evaluate_files_ifeval = datasets.rglob('eval_results_strict.jsonl')

for file in evaluate_files_info:
    evaluate_main(file, file.parent.stem, True)

for file in evaluate_files_ifeval:
    evaluate_main(file, file.parent.stem, False)
