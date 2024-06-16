import json
import os
from pathlib import Path

from tqdm import tqdm


# Function to read a single line from JSONL file
def read_single_line(file):
    line = file.readline()
    if line:
        return json.loads(line)
    return None

def get_language(lang_id):
    return ""

# Function to process data one line at a time and create a new JSONL file
def process_data(input_file_path, output_file_path):
    # Ensure the output file exists and create an empty set for processed prompts
    if os.path.exists(output_file_path):
        with open(output_file_path, 'r') as file:
            processed_data = [json.loads(line) for line in file]
            processed_prompts = {entry['prompt'] for entry in processed_data}
    else:
        processed_prompts = set()

    input_data = []
    # Open input and output files
    with open(input_file_path, 'r') as infile:
        while True:
            item = read_single_line(infile)

            if not item:
                break

            input_data.append(item)

    count = 0

    for item in tqdm(input_data):
        prompt = item['prompt']
        if prompt not in processed_prompts:
            prompt_split = prompt.split("  ", 1)
            
            inp = prompt_split[0]
            instructions = prompt_split[1]
            difficulty = item["difficulty"]

            questions = []
            labels = []
            for instr, kwarg in zip(item['instruction_id_list'], item['kwargs']):
                if instr == 'punctuation:no_comma':
                    questions.append("Is the response free from any commas?")
                    labels.append(["Format"])
                elif instr == 'detectable_format:number_highlighted_sections':
                    questions.append(f"Are exactly {kwarg['num_highlights']} sections highlighted using markdown, i.e *highlighted section*, in the response?")
                    labels.append(["Format"])
                elif instr == 'length_constraints:number_words':
                    questions.append(f"Does the response contain {kwarg['relation']} {kwarg['num_words']} words?")
                    labels.append(["Length"])
                elif instr == 'detectable_content:number_placeholders':
                    questions.append(f"Does the response contain exactly {kwarg['num_placeholders']} placeholders in square brackets (e.g. [name])?")
                    labels.append(["Format"])
                elif instr == 'combination:repeat_prompt':
                    questions.append(f"Does the response contain the prompt: '{kwarg['prompt_to_repeat']}'?")
                    labels.append(["Content"])
                elif instr == 'detectable_format:title':
                    questions.append(f"Does the response contain a title wrapped in double angular brackets i.e <<title>>?")
                    labels.append(["Format"])
                elif instr == 'change_case:english_lowercase':
                    questions.append(f"Is the entire response in lowercase English letters?")
                    labels.append(["Linguistic"])
                elif instr == 'detectable_format:number_bullet_lists':
                    questions.append(f"Does the response contain exactly {kwarg['num_bullets']} bullet points in markdown format'?")
                    labels.append(["Format"])
                elif instr == 'change_case:english_capital':
                    questions.append(f"Is the entire response in capital English letters?")
                    labels.append(["Linguistic"])
                elif instr == 'detectable_format:multiple_sections':
                    f"Are there exactly {kwarg['num_sections']} sections in the response each marked with {kwarg['section_spliter']} X, (where X is the index of the section)?"
                    labels.append(["Format"])
                elif instr == 'change_case:capital_word_frequency':
                    questions.append(f"Does the response contain {kwarg['capital_relation']} {kwarg['capital_frequency']} words with all capital letters?")
                    labels.append(["Content"])
                elif instr == 'startend:quotation':
                    questions.append(f"Is the whole response wrapped with double quotation marks.")
                    labels.append(["Format"])
                elif instr == 'keywords:existence':
                    questions.append(f"Does the response contain the keywords '{', '.join(kwarg['keywords'])}'?")
                    labels.append(["Format"])
                elif instr == 'detectable_format:json_format':
                    questions.append(f"Is the response in json format'?")
                    labels.append(["Format"])
                elif instr == 'length_constraints:number_paragraphs':
                    questions.append(f"Does the response contain {kwarg['num_paragraphs']} paragraphs seperated by the markdown divider: ***?")
                    labels.append(["Format"])
                elif instr == 'combination:two_responses':
                    questions.append(f"Does the response contain two parts separated by 6 asterisk symbols: ******?")
                    labels.append(["Format"])
                elif instr == 'language:response_language':
                    questions.append(f"Is the response in {get_language(kwarg['language'])} language?")
                    labels.append(["Linguistic"])
                elif instr == 'keywords:letter_frequency':
                    questions.append(f"Does the response contain {kwarg['let_relation']} {kwarg['let_frequency']} counts of the letter {kwarg['letter']}?")
                    labels.append(["Content"])
                elif instr == 'startend:end_checker':
                    questions.append(f"Does the response end with: '{kwarg['end_phrase']}'?")
                    labels.append(["Content"])
                elif instr == 'keywords:forbidden_words':
                    questions.append(f"Does the response refrain from including the keywords: '{', '.join(kwarg['forbidden_words'])}'?")
                    labels.append(["Content"])
                elif instr == 'keywords:frequency':
                    questions.append(f"Does the response contain the keyword '{kwarg['keyword']}' {kwarg['relation']} {kwarg['frequency']} times?")
                    labels.append(["Content"])
                elif instr == 'length_constraints:number_sentences':
                    questions.append(f"Does the response contain {kwarg['relation']} {kwarg['num_sentences']} sentences'?")
                    labels.append(["Length"])
                elif instr == 'detectable_content:postscript':
                    questions.append(f"Does the response contain a poscript starting with '{kwarg['postscript_marker']}'?")
                    labels.append(["Content", "Format"])
                elif instr == 'length_constraints:nth_paragraph_first_word':
                    questions.append(f"Does paragraph {kwarg['nth_paragraph']} of {kwarg['num_paragraphs']} of the response start with the word '{kwarg['first_word']}'?")
                    labels.append(["Content"])
                elif instr == 'detectable_format:constrained_response':
                    questions.append(f"Is the response either 'My answer is yes.', 'My answer is no.' or 'My answer is maybe.'?")
                    labels.append(["Format"])
                elif instr == 'detectable_format:highlight_steps':
                    questions.append(f"Does the response use markdown to highlight steps (i.e. **Step i:**)?")
                    labels.append(["Format"])
                elif instr == 'detectable_format:highlight_answer':
                    questions.append(f"Is the final answer highlighted in bold?")
                    labels.append(["Format"])
                elif instr == 'detectable_content:equation_answer':
                    questions.append(f"Is the mathematical equation wrapped in a box using Latex style formatting?")
                    labels.append(["Content"])
                elif instr == 'detectable_content:answer_round':
                    questions.append(f"Is the answer {kwarg['correct_ans']} (i.e {'truncated' if kwarg['type'] == 'Truncate' else 'rounded'} to {kwarg['decimal_places']} decimal place)?")
                    labels.append(["Content"])
                elif instr == 'detectable_content:python_answer':
                    questions.append(f"Does the response contain a python function named '{kwarg['name']}'?")
                    labels.append(["Content"])
                else:
                    raise NotImplementedError(f"{instr} -> {kwarg}")

            
            new_entry = {
                "id": "",
                "input": inp, 
                "category": "", 
                "instruction": instructions, 
                "decomposed_questions": questions, 
                "subset": "", 
                "question_label": labels,
                "difficulty": difficulty
            }
            with open(output_file_path, 'a') as outfile:
                outfile.write(json.dumps(new_entry) + '\n')
            processed_prompts.add(prompt)

            

def generate_info(input_file_path, output_path):
    output_path.mkdir(exist_ok=True)
    output_file_path = output_path / input_file_path.name

    process_data(input_file_path, output_file_path)

input_path = Path('datasets/MMLU_Ifeval_Complex')
output_path = Path('datasets/MMLU_InfoBench_Complex')

for input_file_path in input_path.glob("mat_*.jsonl"):
    print(input_file_path)
    generate_info(input_file_path, output_path)