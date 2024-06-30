import json
from pathlib import Path
from colorama import Fore, Style, init
import numpy as np

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
            instruction_labels = [item.split(':')[0] for item in row['instruction_id_list']]
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

    init()

    # Define color constants for easy reference
    HEADER = Fore.YELLOW + Style.BRIGHT
    HIGHLIGHT = Fore.CYAN + Style.BRIGHT
    RESET = Style.RESET_ALL

    # print(f"{HEADER}{'Analysis Results':^40}{RESET}")
    # print(f"{'='*40}")
    # print(f"{HIGHLIGHT}Model: {model_name}{RESET}")
    # print(f"{HIGHLIGHT}Response File: {response_file}{RESET}")
    # print(f"{'-'*40}")

    total_accuracy = followed / total_prompts
    instructions_per_prompt = instruction_per_prompt / total_prompts
    instr_following = instructions_followed / total_instructions

    # print(f"{HIGHLIGHT}{'Total Accuracy:':<30}{RESET} {total_accuracy:.2%}")
    # print(f"{HIGHLIGHT}{'Total Instructions Followed:':<30}{RESET} {instructions_followed} out of {total_instructions}")
    # print(f"{HIGHLIGHT}{'Instructions Followed per Prompt:':<30}{RESET} {instructions_per_prompt:.2%}")
    # print(f"{'-'*40}")

    # print(f"{HEADER}{'Accuracy per Instruction Type':^40}{RESET}")
    # print(f"{'-'*40}")
    # for key, item in followed_per_type.items():
    #     accuracy = item['followed'] / item['count']
    #     print(f"{HIGHLIGHT}{key:<30}{RESET} {accuracy:.2%}")

    # print(f"{'='*40}\n")
    return total_accuracy


is_infobench = False
if is_infobench:
    eval_file_glob = '*_DecomposeEval.jsonl'
    dataset_dir = 'datasets/MMLU_InfoBench_Complex'
else:
    eval_file_glob = 'eval_results_strict.jsonl'
    dataset_dir = 'datasets/MMLU_Ifeval_Complex'

def get_avg_eval(model_dir):
    run_dirs = list(model_dir.glob("run*"))
    if len(run_dirs) == 0:
        run_dirs = [model_dir]
    
    accs  = []
    for run_dir in run_dirs:
        eval_files = list(run_dir.glob(eval_file_glob))
        if len(eval_files) != 1:
            raise Exception(f"Need 1 {eval_file_glob} file, found {len(eval_files)} at {run_dir}")
        accuracy = evaluate_main(eval_files[0], model_dir.stem, is_infobench)
        accs.append(accuracy * 100)
    
    avg = np.mean(accs)
    std = np.std(accs)
    ptp = np.ptp(accs)
    se = np.square(std) / len(accs)
    return {
        "mean" : avg,
        "std"  : std,
        "se"   : se,
        "ptp"  : ptp
    }


latex_fmt = False
labels = {
    'gpt4'   : 'GPT4', 
    'gpt4o'  : 'GPT4o',
    'llama3' : 'LLaMA3',
    'mistral': 'Mistral',
    'gemma'  : 'Gemma'
}
allowed_models = list(labels.keys())
comp_levels = list(range(1, 7))
diffs = list(range(1, 5))
print(' ' * (10 + 3), "  Complexity Levels  ")#, "   Respective Std Dev                            Respective Ranges")
print(' ' * (10 + 3), "".join((f"{i}      " for i in comp_levels)))#, "".join((f"{i}      " for i in comp_levels)), "".join((f"{i}      " for i in comp_levels)))
for model in allowed_models:
    for d in diffs:
        if d == 3:
            diff = 4
        elif d == 4:
            diff = 3
        else:
            diff = d
        stds = []
        ptps = []
        for comp in comp_levels:
            model_dir = Path(f'{dataset_dir}/response/mat_d{diff}_c{comp}/{model}')
            out = get_avg_eval(model_dir)
            stds.append(out["std"])
            ptps.append(out["ptp"])
            # printing logic
            if comp == comp_levels[0]:
                if diff == 1:
                    print(labels[model].ljust(10), end='')
                    print(f'{"& " if latex_fmt else ""}I   ', end='')
                else:
                    print(' ' * 10, end='')
                if diff == 2:
                    print(f'{"& " if latex_fmt else ""}II  ', end='')
                if diff == 3:
                    print(f'{"& " if latex_fmt else ""}IV  ', end='')
                if diff == 4:
                    print(f'{"& " if latex_fmt else ""}III ', end='')
            
            print((f"{'& \\colorbypct{' if latex_fmt else ''}{int(np.round(out["mean"])):2}{'} $\\pm ' if latex_fmt else ' ±'}{int(np.round(out["std"])):1}{'$' if latex_fmt else ''}  ").ljust(4), end='')
        print(f"\\\\ {'\\hline' if d == diffs[-1] else '\\cline{2-8}'}" if latex_fmt else "")#, " ".join([f'{(f"{std:3.2f}"):<6}' for std in stds]), " ".join([f'{(f"{ptp:3.2f}"):<6}' for ptp in ptps]))


# for file in evaluate_files_info:
#     if file.parent.stem in allowed_models:
#         evaluate_main(file, file.parent.stem, True)

# for file in evaluate_files_ifeval:
#     evaluate_main(file, file.parent.stem, False)
