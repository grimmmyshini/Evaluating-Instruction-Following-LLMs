import json
from pathlib import Path
from colorama import Fore, Style, init

def evaluate_main(response_file: Path, model_name, infobench):
    with open(response_file, 'r') as json_file:
        df = [json.loads(line) for line in json_file]

    followed = 0
    instructions_followed = 0
    total_instructions = 0
    instruction_per_prompt = 0
    total_prompts = 0
    followed_per_type = {}
    print(f"{response_file}")

    for row in df:
        if infobench:
            all_instructions = row['eval']
            instruction_labels = [item[0] for item in row['decomposed_questions']]
            follows_all = all_instructions.count(True) == len(all_instructions)
        else:
            all_instructions = row['follow_instruction_list']
            instruction_labels = [item.split(':')[0] for item in row['instruction_id_list']]
            follows_all = row['follow_all_instructions']

        # assert len(all_instructions) == len(instruction_labels) and len(all_instructions) != 0
        # if len(all_instructions) != len(instruction_labels) or len(all_instructions) == 0:
        #     continue
        assert len(all_instructions) == len(instruction_labels) and len(all_instructions) != 0, f"{row, file}"
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

    init()

    # Define color constants for easy reference
    HEADER = Fore.YELLOW + Style.BRIGHT
    HIGHLIGHT = Fore.CYAN + Style.BRIGHT
    RESET = Style.RESET_ALL

    print(f"{HEADER}{'Analysis Results':^40}{RESET}")
    print(f"{'='*40}")
    print(f"{HIGHLIGHT}Model: {model_name}{RESET}")
    print(f"{HIGHLIGHT}Response File: {response_file}{RESET}")
    print(f"{'-'*40}")

    assert total_prompts != 0, f"{response_file}"
    total_accuracy = followed / total_prompts
    instructions_per_prompt = instruction_per_prompt / total_prompts
    
    print(f"{HIGHLIGHT}{'Total Accuracy:':<30}{RESET} {total_accuracy:.2%}")
    print(f"{HIGHLIGHT}{'Total Instructions Followed:':<30}{RESET} {instructions_followed} out of {total_instructions}")
    print(f"{HIGHLIGHT}{'Instructions Followed per Prompt:':<30}{RESET} {instructions_per_prompt:.2%}")
    print(f"{'-'*40}")

    print(f"{HEADER}{'Accuracy per Instruction Type':^40}{RESET}")
    print(f"{'-'*40}")
    for key, item in followed_per_type.items():
        accuracy = item['followed'] / item['count']
        print(f"{HIGHLIGHT}{key:<30}{RESET} {accuracy:.2%}")

    print(f"{'='*40}\n")


datasets = (
    "datasets/IfevalToInfo/response",
    "datasets/MATHWELL_Info/response",
    "datasets/MMLU_InfoBench/response",
    "datasets/InfoToIfeval/response",
    "datasets/MMLU_Ifeval/response",
    "datasets/MATHWELL_Ifeval/response"
    )

for dataset in datasets:
    datas = Path(dataset)
    evaluate_files_info = datas.rglob('*_DecomposeEval.jsonl')
    evaluate_files_ifeval = datas.rglob('eval_results_strict.jsonl')

    allowed_models = ['gemma', 'gpt4', 'gpt4o', 'llama3', 'mistral']

    for file in evaluate_files_info:
        if file.parent.stem in allowed_models:
            evaluate_main(file, file.parent.stem, True)

    for file in evaluate_files_ifeval:
        if file.parent.stem in allowed_models:
            evaluate_main(file, file.parent.stem, False)
