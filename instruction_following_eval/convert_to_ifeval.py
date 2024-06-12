from langchain_community.llms import Ollama
from subprocess import run
import json
import random
import instructions
import instructions_registry as ir
from tqdm import tqdm

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


def add_constraints_to_prompts_automatic(prompt_file, store_file):
    with open(prompt_file, 'r') as json_file:
        df = json.load(json_file)

    conflicts = ir.conflict_make(ir.INSTRUCTION_CONFLICTS)
    key = 0
    records = []
    for row in tqdm(df):
        instr_id = 0
        limit = random.choice(range(2, 5))
        prompt = row['prompt'] + ' '
        constraint_list = []
        conflict_list = []
        instruction_id_list = []
        kwargs = []
        while instr_id < limit:
            choices = set(math_instrs_ok.keys()).difference(conflict_list)
            if len(choices) == 0:
                break
            constraint = random.choice(list(choices))
            type_constraint = math_instrs_ok[constraint]['type'] + constraint

            if type_constraint in conflict_list or constraint in constraint_list:
                continue
            if constraint == 'answer_round' and '.' not in row['answer']:
                continue

            constraint_list += [constraint]
            conflict_list += conflicts[type_constraint]
            instruction_id_list += [type_constraint]
            const_obj = math_instrs_ok[constraint]['class'](instr_id)
            instr_id += 1

            if constraint == 'repeat_prompt':
                prompt += ' ' + const_obj.build_description(
                    prompt_to_repeat=prompt)
            elif constraint == 'answer_round':
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
            'kwargs': kwargs
        }
        records += [record]
        key += 1

    with open(store_file, 'w') as json_file:
        json.dump(records, json_file, indent=4)


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


init_prompts = '/home/grimmyshini/CS4NLP-Project/datasets/fomatted_prompts_mathwell.json'
store_prompts = '/home/grimmyshini/CS4NLP-Project/datasets/constrained_prompts_mathwell.json'
store_responses = '/home/grimmyshini/CS4NLP-Project/datasets/responses_mathwell_llama3.json'
# add_constraints_to_prompts_automatic(init_prompts, store_prompts)

# evaluate_prompts(store_prompts, store_responses, "llama3")
