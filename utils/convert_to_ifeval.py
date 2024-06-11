import json
import random
import pandas as pd
import instruction_following_eval.instructions as instructions
import instruction_following_eval.instructions_registry as ir

# Math specifc instructions
math_instr = {
    'highlight_steps':{'type':ir._FORMAT, 'class':instructions.StepsChecker, 'args':{'min_steps':None, 'max_steps':None}},
    'highlight_answer':{'type':ir._FORMAT, 'class':instructions.AnswerHighlightChecker, 'args':{}},
    'equation_answer':{'type':ir._CONTENT, 'class':instructions.EquationAnswerChecker, 'args':{}},
    'answer_round':{'type':ir._CONTENT, 'class':instructions.AnswerRoundChecker, 'args':{'decimal_places':None, 'type':None}},
    'python_answer':{'type':ir._CONTENT, 'class':instructions.PythonFunctionChecker, 'args':{}}
}

# All instructs that we can apply to math prompts
math_instrs_ok = {
 'highlight_steps':{'type':ir._FORMAT, 'class':instructions.StepsChecker},
 'highlight_answer':{'type':ir._FORMAT, 'class':instructions.AnswerHighlightChecker},
 'equation_answer':{'type':ir._CONTENT, 'class':instructions.EquationAnswerChecker},
 'answer_round':{'type':ir._CONTENT, 'class':instructions.AnswerRoundChecker},
 'python_answer':{'type':ir._CONTENT, 'class':instructions.PythonFunctionChecker},
 'response_language':{'type':ir._LANGUAGE, 'class':instructions.ResponseLanguageChecker},
 'number_sentences':{'type':ir._LENGTH, 'class':instructions.NumberOfSentences},
 'multiple_sections':{'type':ir._FORMAT, 'class':instructions.SectionChecker},
 'number_paragraphs':{'type':ir._LENGTH, 'class':instructions.ParagraphChecker},
 'existence':{'type':ir._KEYWORD, 'class':instructions.KeywordChecker},
 'frequency':{'type':ir._KEYWORD, 'class':instructions.KeywordFrequencyChecker},
 'number_words':{'type':ir._LENGTH, 'class':instructions.NumberOfWords},
 'nth_paragraph_first_word':{'type':ir._LENGTH, 'class':instructions.ParagraphFirstWordCheck},
 'forbidden_words':{'type':ir._KEYWORD, 'class':instructions.ForbiddenWords},
 'two_responses':{'type':ir._COMBINATION, 'class':instructions.TwoResponsesChecker},
 'repeat_prompt':{'type':ir._COMBINATION, 'class':instructions.RepeatPromptThenAnswer},
 'end_checker':{'type':ir._STARTEND, 'class':instructions.EndChecker},
 'title':{'type':ir._FORMAT, 'class':instructions.TitleChecker},
 'letter_frequency':{'type':ir._KEYWORD, 'class':instructions.LetterFrequencyChecker},
 'english_capital':{'type':ir._CHANGE_CASES, 'class':instructions.CapitalLettersEnglishChecker},
 'english_lowercase':{'type':ir._CHANGE_CASES, 'class':instructions.LowercaseLettersEnglishChecker},
 'no_comma':{'type':ir._PUNCTUATION, 'class':instructions.CommaChecker},
 'capital_word_frequency':{'type':ir._CHANGE_CASES, 'class':instructions.CapitalWordFrequencyChecker},
 'quotation':{'type':ir._STARTEND, 'class':instructions.QuotationChecker}
}

opt_list = list(math_instr.keys())

def add_constraints_to_prompts(prompt_file):
    with open(prompt_file, 'r') as json_file:
        df = json.load(json_file)

    for _, row in df.iterrows():
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
    for _, row in df.iterrows():
        instr_id = 0
        limit = random.choice(range(1, 5))
        prompt = row['prompt']
        print("Initial prompt \n", prompt)

        constraint_list = []
        conflict_list = []
        instruction_id_list = []
        kwargs = []
        while instr_id < limit:
            constraint = random.choice(math_instrs_ok.keys())
            if constraint in conflict_list or constraint in constraint_list:
                continue

            conflict_list += conflicts[constraint]
            constraint_list += [constraint]
            instruction_id_list += [math_instrs_ok[constraint]['type'] + constraint]
            const_obj = math_instrs_ok[constraint]['class'](instr_id)
            instr_id += 1

            kwargs += [const_obj.get_instruction_args()]
            prompt += const_obj.build_description()

        print("Final prompt: \n", prompt)

        # {"key":, "prompt":, "instruction_id_list": ["type:instr_name"], "kwargs": [{"arg1": "val1"}]}
        record = {
            'key' : key,
            'prompt': prompt,
            'instruction_id_list': instruction_id_list,
            'kwargs': kwargs
        }
        records += [record]

        if key >= 10:
            break

    with open(store_file, 'w') as json_file:
        json.dump(records, json_file, indent=4)

init_prompts = '/home/grimmyshini/CS4NLP-Project/datasets/fomatted_prompts_mathwell.json'
store_prompts = '/home/grimmyshini/CS4NLP-Project/datasets/constrained_prompts_mathwell.json'
add_constraints_to_prompts_automatic(init_prompts, store_prompts)
