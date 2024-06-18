import itertools
from langchain_community.llms import Ollama # type: ignore
from pathlib import Path
from subprocess import run
import json
from tqdm import tqdm
from utils.chat import chat
from instruction_following_eval.convert_to_ifeval import math_instrs_ok
import instruction_following_eval.instructions


def analysis2(prompt_file, store_files):
    with open(prompt_file, 'r') as json_file:
        df = json.load(json_file)

    records =  [[], [], [], [], []] # 5 x 100
    for row in tqdm(df):
        index_list = [0, 1, 2]
        permutation_list = list(itertools.permutations(index_list, 3))[1:]
        for i, perm in enumerate(permutation_list):
            instruction_id_list = [row['instruction_id_list'][idx] for idx in perm]
            kwargs = [row['kwargs'][idx] for idx in perm]
            prompt_list = [row['prompt_list'][0]]
            prompt_list += [row['prompt_list'][idx + 1] for idx in perm]
            prompt = ""
            for item in prompt_list:
                prompt += item

            records[i] += [{
            'key': row['key'],
            'prompt': prompt,
            'prompt_list': prompt_list,
            'instruction_id_list': instruction_id_list,
            'kwargs': kwargs,
            'difficulty': row['difficulty']
            }]

    for i, record in enumerate(records):
        with open(store_files[i+1], 'w') as json_file:
            json.dump(record, json_file, indent=4)

# analysis_2_prompts_base = '/home/grimmyshini/CS4NLP-Project/datasets/ReorderingAnalysis'
# analysis_2_prompts = [analysis_2_prompts_base + '/mathwell_combi_' + str(i) + '.json' for i in range(0, 6)]
# add_constraints_to_prompts_separated(init_prompts, analysis_2_prompts[0], 3, 4)
# analysis2(analysis_2_prompts[0], analysis_2_prompts)

def check_following(row, response):
    strict_following = True
    follow_per_instruction = []
    for instr_id, instr in enumerate(row['instruction_id_list']):
        instr_cls = math_instrs_ok[instr.split(':')[1]]['class'](instr_id)
        instr_cls.build_description(**row['kwargs'][instr_id])
        following = instr_cls.check_following(response)
        strict_following &= following
        follow_per_instruction += [following]
    return strict_following, follow_per_instruction

def analysis3(blind, prompt_file, store_file, model):
    with open(prompt_file, 'r') as json_file:
        df = json.load(json_file)

    record = []
    for row in tqdm(df):
        messages = []
        response = None
        response_list = []
        strict = False
        per_instr = []
        content = row['prompt']
        for i in range(0, 5):
            messages.append({"role": "user", "content": content})
            response = chat(model, messages=messages)
            response_list.append(response)
            messages.append({"role": "assistant", "content": response})
            strict, per_instr = check_following(row, response)
            if strict:
                break
            else:
                if blind:
                    messages = []
                    content = row['prompt']
                else:
                    not_followed = [i for i in range(len(row['instruction_id_list'])) if not per_instr[i]]
                    content = "You did not follow the following instructions: "
                    for i, idx in enumerate(not_followed):
                        content += str(i + 1) + ") " + row['instruction_id_list'][idx] + " \n"
                    content += "Regenerate a response that follows these instructions as well as the ones mentioned before."
        print(None if not strict else len(response_list))
        record += [{
            'key': row['key'],
            'prompt': row['prompt'],
            'prompt_list': row['prompt_list'],
            'response_list': response_list,
            'tries_till_following': None if not strict else len(response_list),
            'follow_all_instructions': strict,
            'follow_instruction_list': per_instr,
            'instruction_id_list': row['instruction_id_list'],
            'kwargs': row['kwargs'],
            'difficulty': row['difficulty']
        }]

    with open(store_file, 'w') as json_file:
            json.dump(record, json_file, indent=4)

analysis_3_prompts = '/home/grimmyshini/CS4NLP-Project/datasets/RepromptingAnalysis/mathwell_separated.json'
analysis_3_response = '/home/grimmyshini/CS4NLP-Project/datasets/RepromptingAnalysis/response/'
store_file = '/eval_results.json'
model = "llama3"


analysis3(True, analysis_3_prompts, analysis_3_response + model + store_file, model)
# analysis3(False, analysis_3_prompts, analysis_3_response + model + store_file, model)
