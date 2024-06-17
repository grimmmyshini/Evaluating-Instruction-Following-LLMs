import itertools
from langchain_community.llms import Ollama # type: ignore
from pathlib import Path
from subprocess import run
import json
import random
import instructions
import instructions_registry as ir
from tqdm import tqdm
import numpy as np

# Math specifc instructions
math_instr = {
    'highlight_steps': {'type': ir._FORMAT, 'class': instructions.StepsChecker, 'args': {'min_steps': None, 'max_steps': None}},
    'highlight_answer': {'type': ir._FORMAT, 'class': instructions.AnswerHighlightChecker, 'args': {}},
    'equation_answer': {'type': ir._CONTENT, 'class': instructions.EquationAnswerChecker, 'args': {}},
    'answer_round': {'type': ir._CONTENT, 'class': instructions.AnswerRoundChecker, 'args': {'decimal_places': None, 'type': None}},
    'python_answer': {'type': ir._CONTENT, 'class': instructions.PythonFunctionChecker, 'args': {}}
}

# All instructs that we can apply to math prompts
math_instrs_ok = {
    'highlight_steps': {'type': ir._FORMAT, 'class': instructions.StepsChecker},
    'highlight_answer': {'type': ir._FORMAT, 'class': instructions.AnswerHighlightChecker},
    'equation_answer': {'type': ir._CONTENT, 'class': instructions.EquationAnswerChecker},
    'answer_round': {'type': ir._CONTENT, 'class': instructions.AnswerRoundChecker},
    'python_answer': {'type': ir._CONTENT, 'class': instructions.PythonFunctionChecker},
    # 'response_language': {'type': ir._LANGUAGE, 'class': instructions.ResponseLanguageChecker},
    'number_sentences': {'type': ir._LENGTH, 'class': instructions.NumberOfSentences},
    'multiple_sections': {'type': ir._FORMAT, 'class': instructions.SectionChecker},
    'number_paragraphs': {'type': ir._LENGTH, 'class': instructions.ParagraphChecker},
    'existence': {'type': ir._KEYWORD, 'class': instructions.KeywordChecker},
    'frequency': {'type': ir._KEYWORD, 'class': instructions.KeywordFrequencyChecker},
    # 'number_words': {'type': ir._LENGTH, 'class': instructions.NumberOfWords},
    'nth_paragraph_first_word': {'type': ir._LENGTH, 'class': instructions.ParagraphFirstWordCheck},
    'forbidden_words': {'type': ir._KEYWORD, 'class': instructions.ForbiddenWords},
    'two_responses': {'type': ir._COMBINATION, 'class': instructions.TwoResponsesChecker},
    'repeat_prompt': {'type': ir._COMBINATION, 'class': instructions.RepeatPromptThenAnswer},
    'end_checker': {'type': ir._STARTEND, 'class': instructions.EndChecker},
    'title': {'type': ir._FORMAT, 'class': instructions.TitleChecker},
    'letter_frequency': {'type': ir._KEYWORD, 'class': instructions.LetterFrequencyChecker},
    'english_capital': {'type': ir._CHANGE_CASES, 'class': instructions.CapitalLettersEnglishChecker},
    'english_lowercase': {'type': ir._CHANGE_CASES, 'class': instructions.LowercaseLettersEnglishChecker},
    'no_comma': {'type': ir._PUNCTUATION, 'class': instructions.CommaChecker},
    'capital_word_frequency': {'type': ir._CHANGE_CASES, 'class': instructions.CapitalWordFrequencyChecker},
    'quotation': {'type': ir._STARTEND, 'class': instructions.QuotationChecker}
}

opt_list = list(math_instr.keys())


def add_constraints_to_prompts(prompt_file):
    with open(prompt_file, 'r') as json_file:
        df = json.load(json_file)

    for row in df:
        print("Current Prompt")
        print(row['prompt'])
        res_prompt = row['prompt']
        instr_id = 0

        while True:
            print("Select Instruction to add:")
            for i, opt in enumerate(opt_list):
                print(i, " ", opt)
            print(len(opt_list), " Move to next prompt")

            print("Enter Selection: ")
            idx = int(input())
            if idx >= len(opt_list):
                break

            instr = math_instr[opt_list[idx]]
            val = instr['class'](instr_id)
            args = []
            for arg in instr['args']:
                print(arg, " (Hit enter for 'None'): ")
                arg_ch = input()
                if arg_ch == '':
                    args.append(None)
                else:
                    try:
                        args.append(int(arg_ch))
                    except:
                        args.append(arg_ch)
            res_prompt += " " + val.build_description(*args)
            print("Resulting prompt: ")
            print(res_prompt)


def add_constraints_to_prompts_automatic(prompt_file, store_file, low = 2, high = 5):
    with open(prompt_file, 'r') as json_file:
        df = json.load(json_file)

    conflicts = ir.conflict_make(ir.INSTRUCTION_CONFLICTS)
    key = 0
    records = []
    for row in tqdm(df):
        instr_id = 0
        limit = random.choice(range(low, high))
        prompt = row['prompt'] + ' '
        constraint_list = []
        conflict_list = []
        instruction_id_list = []
        kwargs = []
        while instr_id < limit:
            choices = set(math_instrs_ok.keys()).difference([conflict.split(':')[1] for conflict in conflict_list])
            if len(choices) == 0:
                break
            constraint = random.choice(list(choices))
            type_constraint = math_instrs_ok[constraint]['type'] + constraint
            if constraint == 'answer_round':
                try:
                    ans = float(row['answer'])
                except:
                    conflict_list += [type_constraint]
                    continue
                if '.' not in row['answer']:
                    continue
            if type_constraint in conflict_list or constraint in constraint_list:
                continue
            constraint_list += [constraint]
            conflict_list += conflicts[type_constraint]
            conflict_list += [type_constraint]
            instruction_id_list += [type_constraint]
            const_obj = math_instrs_ok[constraint]['class'](instr_id)
            instr_id += 1

            if constraint == 'repeat_prompt':
                prompt += ' ' + const_obj.build_description(
                    prompt_to_repeat=prompt)
            elif constraint == 'answer_round':
                print(row['answer'], row['answer'].split('.'))
                max = len(row['answer'].split('.')[1])
                round_to = random.choice(range(1, max)) if max > 1 else 1
                type_of = random.choice(["Round", "Truncate"])
                ans = float(row['answer'])
                prompt += ' ' + const_obj.build_description(ans, round_to, type_of)
            else:
                prompt += ' ' + const_obj.build_description()
            args = const_obj.get_instruction_args()
            if args:
                kwargs += [args]
            else:
                kwargs += [{}]

        # Can also add logic to generate responses with gpt

        # {"key":, "prompt":, "instruction_id_list": ["type:instr_name"], "kwargs": [{"arg1": "val1"}]}
        record = {
            'key': key,
            'prompt': prompt,
            'instruction_id_list': instruction_id_list,
            'kwargs': kwargs,
            'difficulty': row['difficulty']
        }
        records += [record]
        key += 1

    with open(store_file, 'w') as json_file:
        json.dump(records, json_file, indent=4)


def add_constraints_to_prompts_by_number(prompt_file, store_file):
    with open(prompt_file, 'r') as json_file:
        df = json.load(json_file)

    conflicts = ir.conflict_make(ir.INSTRUCTION_CONFLICTS)
    key = 0
    records = []

    diff_freq = {}

    for row in tqdm(df):
        try:
            diff_freq[row["difficulty"]] += 1
        except KeyError:
            diff_freq[row["difficulty"]] = 0

    min_all = np.min(list(diff_freq.values()))
    print(f"Using {min_all} data points from each of these difficulties: {list(diff_freq.keys())}")

    lim_range = range(6, 0, -1)

    for key in diff_freq:
        diff_freq[key] = min_all
        for limit in lim_range:
            file_path = Path(store_file).with_stem(f"mat_d{key}_c{limit}")
            if file_path.exists():
                file_path.unlink()

    for row in tqdm(df):
        if diff_freq[row["difficulty"]] <= 0:
            continue

        limit = list(lim_range)[0]
        instr_id = 0
        prompt = row['prompt'] + ' '
        constraint_list = []
        conflict_list = []
        instruction_id_list = []
        kwargs = []
        var_instr_records = []
        while instr_id < limit:
            choices = set(math_instrs_ok.keys()).difference([conflict.split(':')[1] for conflict in conflict_list])
            if len(choices) == 0:
                break

            constraint = random.choice(list(choices))
            type_constraint = math_instrs_ok[constraint]['type'] + constraint
            if constraint == 'answer_round':
                try:
                    ans = float(row['answer'])
                except:
                    conflict_list += [type_constraint]
                    continue
                if '.' not in row['answer']:
                    continue
            if type_constraint in conflict_list or constraint in constraint_list:
                continue
            constraint_list += [constraint]
            conflict_list += conflicts[type_constraint]
            conflict_list += [type_constraint]
            instruction_id_list += [type_constraint]
            const_obj = math_instrs_ok[constraint]['class'](instr_id)
            instr_id += 1

            if constraint == 'repeat_prompt':
                prompt += ' ' + const_obj.build_description(
                    prompt_to_repeat=prompt)
            elif constraint == 'answer_round':
                print(row['answer'], row['answer'].split('.'))
                max = len(row['answer'].split('.')[1])
                round_to = random.choice(range(1, max)) if max > 1 else 1
                type_of = random.choice(["Round", "Truncate"])
                ans = float(row['answer'])
                prompt += ' ' + const_obj.build_description(ans, round_to, type_of)
            else:
                prompt += ' ' + const_obj.build_description()
            args = const_obj.get_instruction_args()
            if args:
                kwargs += [args]
            else:
                kwargs += [{}]

            record = {
                'key': key,
                'prompt': prompt,
                'instruction_id_list': instruction_id_list.copy(),
                'kwargs': kwargs.copy(),
                'difficulty': row['difficulty']
            }

            var_instr_records.append(record)


        if len(var_instr_records) != limit:
            continue

        # Can also add logic to generate responses with gpt

        # {"key":, "prompt":, "instruction_id_list": ["type:instr_name"], "kwargs": [{"arg1": "val1"}]}

        for i in lim_range:
            file_path = Path(store_file).with_stem(f"mat_d{row['difficulty']}_c{i}")
            with open(file_path, 'a') as json_file:
                json_file.write(json.dumps(var_instr_records[i - 1]) + '\n')

        key += 1
        diff_freq[row["difficulty"]] -= 1

def get_response(model, prompt):
    try:
        llm = Ollama(model=model)
    except:
        cmd = ['ollama', 'pull', model]
        run(cmd, check=True)
        llm = Ollama(model=model)

    return llm.invoke(prompt)


def evaluate_prompts(prompt_file, store_file, model, redo = False):
    with open(prompt_file, 'r') as json_file:
        df = json.load(json_file)

    with open(store_file, 'r') as json_file:
        records = json.load(json_file)

    cnt = 0

    if redo or len(records) == 0:
        last_key = -1
    else:
        last_key = records[-1]['key']

    for i, row in enumerate(tqdm(df)):
        if i <= last_key:
            continue
        prompt = row['prompt']
        response = get_response(model, prompt)
        strict_following = True
        follow_per_instruction = []

        # {"key":, "prompt":, "instruction_id_list": ["type:instr_name"], "kwargs": [{"arg1": "val1"}]}
        for instr_id, instr in enumerate(row['instruction_id_list']):
            instr_cls = math_instrs_ok[instr.split(':')[1]]['class'](instr_id)
            instr_cls.build_description(**row['kwargs'][instr_id])
            following = instr_cls.check_following(response)
            strict_following &= following
            follow_per_instruction += [following]

        record = {
            'key': row['key'],
            'prompt': row['prompt'],
            'instruction_id_list': row['instruction_id_list'],
            'kwargs': row['kwargs'],
            'response': response,
            'strict_following': strict_following,
            'follow_per_instruction': follow_per_instruction
        }
        records += [record]
        if strict_following:
            cnt += 1

        with open(store_file, 'w') as file:
            json.dump(records, file, indent=4)

        print("Accuracy: ", cnt/(i + 1))


def add_constraints_to_prompts_separated(prompt_file, store_file, low = 2, high = 5):
    with open(prompt_file, 'r') as json_file:
        df = json.load(json_file)

    conflicts = ir.conflict_make(ir.INSTRUCTION_CONFLICTS)
    key = 0
    records = []
    for row in tqdm(df):
        instr_id = 0
        limit = random.choice(range(low, high))
        prompt = row['prompt']
        prompt_list = [prompt]
        constraint_list = []
        conflict_list = []
        instruction_id_list = []
        kwargs = []
        while instr_id < limit:
            choices = set(math_instrs_ok.keys()).difference([conflict.split(':')[1] for conflict in conflict_list])
            if len(choices) == 0:
                break
            constraint = random.choice(list(choices))
            type_constraint = math_instrs_ok[constraint]['type'] + constraint
            if constraint == 'answer_round':
                try:
                    ans = float(row['answer'])
                except:
                    conflict_list += [type_constraint]
                    continue
                if '.' not in row['answer']:
                    continue
            if type_constraint in conflict_list or constraint in constraint_list:
                continue
            constraint_list += [constraint]
            conflict_list += conflicts[type_constraint]
            conflict_list += [type_constraint]
            instruction_id_list += [type_constraint]
            const_obj = math_instrs_ok[constraint]['class'](instr_id)
            instr_id += 1

            if constraint == 'repeat_prompt':
                instr = ' ' + const_obj.build_description(
                    prompt_to_repeat=prompt)
                prompt += instr
                prompt_list += [instr]
            elif constraint == 'answer_round':
                max = len(row['answer'].split('.')[1])
                round_to = random.choice(range(1, max)) if max > 1 else 1
                type_of = random.choice(["Round", "Truncate"])
                ans = float(row['answer'])
                instr = ' ' + const_obj.build_description(ans, round_to, type_of)
                prompt += instr
                prompt_list += [instr]
            else:
                instr = ' ' + const_obj.build_description()
                prompt += instr
                prompt_list += [instr]
            args = const_obj.get_instruction_args()
            if args:
                kwargs += [args]
            else:
                kwargs += [{}]

        # Can also add logic to generate responses with gpt

        # {"key":, "prompt":, "instruction_id_list": ["type:instr_name"], "kwargs": [{"arg1": "val1"}]}
        record = {
            'key': key,
            'prompt': prompt,
            'prompt_list': prompt_list,
            'instruction_id_list': instruction_id_list,
            'kwargs': kwargs,
            'difficulty': row['difficulty']
        }
        records += [record]
        key += 1

    with open(store_file, 'w') as json_file:
        json.dump(records, json_file, indent=4)

# 1) what makes prompts difficult? Complexity of question or complexity of added instructions.
# mmlu 1, 2, 4, 8
#    1 90
#    2 30
#    3 20
#    4
#
# 2) Does the instruction ordering matter for accuracy?
#
# 3) (not sure how to show this) how does blind re-prompting vs guided re-prompting help? My initial idea is to show the average best accuracy between reprompts. Here blind reprompts are just "try again." And guided reprompts are "No, you need to follow the instruction <instruction not followed> and any others described by the original prompt."
#
# 4) could be step by step prompting? Like instead of giving instructions altogether, we prompt the model step by step and see if that increases accuracy.
#
# 5) Look into roles in llm apis? Can roles help llms follow instructions better?

# Models                    [llama3, mistral, gemma, chatGPT4, chatGPT4o]
# Datasets
# Info dataset with ifeval      1       1       1       0          0
# ifeval dataset with info      1       0       0       0          0
# mathwell with info            0       0       0       0          0
# mathwell with ifeval          1       0       0       0          0
# mmlu with ifeval              0       0       0       0          0
# mmlu with info                0       0       0       0          0

init_prompts = '../datasets/fomatted_prompts_mathwell.json'
init_prompts_mmlu = '../datasets/fomatted_prompts_mmlu.json'

store_prompts = '../datasets/constrained_prompts_mathwell.json'
store_prompts_mmlu = '../datasets/constrained_prompts_mmlu.json'

store_complex_prompts_mmlu = '../datasets/MMLU_complexity_grid/mat.jsonl'

store_responses = '../datasets/responses_mathwell_llama3.json'
# add_constraints_to_prompts_automatic(init_prompts, store_prompts)
# add_constraints_to_prompts_automatic(init_prompts_mmlu, store_prompts_mmlu)
# add_constraints_to_prompts_automatic('/home/grimmyshini/CS4NLP-Project/datasets/fomatted_prompts_mmlu.json', '/home/grimmyshini/CS4NLP-Project/datasets/constrained_prompts_mmlu_full.json')

# evaluate_prompts(store_prompts, store_responses, "llama3")
# add_constraints_to_prompts_by_number(init_prompts_mmlu, store_complex_prompts_mmlu)

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
