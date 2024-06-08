import pandas as pd
import instructions
import instructions_registry as ir
# {"key":, "prompt":, "instruction_id_list": ["type:instr_name"], "kwargs": [{"arg1": "val1"}]}
# Math specifc instructions
math_instr = {
    'highlight_steps':{'type':ir._FORMAT, 'class':instructions.StepsChecker, 'args':{'min_steps':None, 'max_steps':None}},
    'highlight_answer':{'type':ir._FORMAT, 'class':instructions.AnswerHighlightChecker, 'args':{}},
    'equation_answer':{'type':ir._CONTENT, 'class':instructions.EquationAnswerChecker, 'args':{}},
    'answer_round':{'type':ir._CONTENT, 'class':instructions.AnswerRoundChecker, 'args':{'decimal_places':None, 'type':None}},
    'python_answer':{'type':ir._CONTENT, 'class':instructions.PythonFunctionChecker, 'args':{}}
}
opt_list = list(math_instr.keys())

if __name__ == "__main__":
    df = pd.read_csv('/home/grimmyshini/CS4NLP-Project/datasets/MMLU-Math/test/abstract_algebra_test.csv')
    for _, row in df.iterrows():
        print("Current Prompt")
        print(row['prompt'])
        # promt_result = """ """
        # instr = instructions.PythonFunctionChecker(0)
        # instr.build_description()
        # print(instr.check_following(promt_result))
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
