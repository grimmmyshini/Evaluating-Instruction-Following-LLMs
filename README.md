<div align="center">

![Alt](assets/eth_logo.png "Title")
# Assessing Instruction Following Capabilities of Large Language Models
### [CS4NLP Spring Semester 2024](https://www.mrinmaya.io/teaching_csnlp24)
### Professor: [Mrinmaya Sachan](https://www.mrinmaya.io/)


<a href="#">
    <img src="https://img.shields.io/badge/Python-3.8--3.12-1cb855">
</a>

<br/><br/>
</div>


This project was done for the Computational Semanticts for Natural Language Processing (CS4NLP) course. 
The project aims to test the intruction following capabilities of LLMs using methods from recent research. 
It gave us new insights into the LLMs as well as the methods presented in the research.


The detailed description of the project and results are available in [this report](assets/report.pdf).

## Getting Started

The required python packages are in the `requirements.txt` file. Use a virtual environment and install them using pip:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt
```

## Experiments Overview

There are 5 experiments in the repo:

### Experiment 1: IFEval and InfoBench Evaluations

In this experiment, we aim to assess two qualities relating to the instruction following capabilities of LLMs.
First, how do different LLMs perform across domains, and second, how well are the evaluation metrics able to asses this performance.

*Experiment datasets*: 
```bash
datasets
├─── IfevalToInfo
│    ├─── ifeval_subset.jsonl
│    └─── IFEvaltoInfo.jsonl
├─── InfoToIfeval
│    ├─── infobench_subset.jsonl
│    └─── infoToIfeval.jsonl
├─── MATHWELL_Ifeval
│    └─── mathwell_ifeval.jsonl
├─── MATHWELL_Info
│    └─── mathwell_info.jsonl
├─── MMLU_Ifeval
│    └─── mmlu_ifval.jsonl
└─── MMLU_InfoBench
     └─── mmlu_info.jsonl
```

### Experiment 2: Prompt vs. Instruction Difficulty

In this experiment, we try to
assess 2 aspects that make a prompt and instruction
set 'difficult' for an LLM to follow.
The first aspect we assess is the inherent difficulty of the prompt. The second aspect we
assess is the difficulty or complexity of the instructions.

*Experiment datasets*: 
```bash
datasets
└─── MMLU_Ifeval_Complex
     ├─── mat_d1_c1.jsonl
     ├─── mat_d1_c2.jsonl
     ├─── mat_d1_c3.jsonl
     ├─── mat_d1_c4.jsonl
     ├─── mat_d1_c5.jsonl
     ├─── mat_d1_c6.jsonl
     ├─── mat_d2_c1.jsonl
     ├─── mat_d2_c2.jsonl
     ├─── mat_d2_c3.jsonl
     ├─── mat_d2_c4.jsonl
     ├─── mat_d2_c5.jsonl
     ├─── mat_d2_c6.jsonl
     ├─── mat_d3_c1.jsonl
     ├─── mat_d3_c2.jsonl
     ├─── mat_d3_c3.jsonl
     ├─── mat_d3_c4.jsonl
     ├─── mat_d3_c5.jsonl
     ├─── mat_d3_c6.jsonl
     ├─── mat_d4_c1.jsonl
     ├─── mat_d4_c2.jsonl
     ├─── mat_d4_c3.jsonl
     ├─── mat_d4_c4.jsonl
     ├─── mat_d4_c5.jsonl
     └─── mat_d4_c6.jsonl
```

### Experiment 3: Guided vs. Blind Reprompting

In this experiment we compare two types of reprompting – Guided
and Blind reprompting. Guided reprompting involves prompting the LLM to fix the specific instructions it did not previously follow. Whereas Blind reprompting refers to re-feeding the same
initial prompt back to the LLM multiple times, letting it infer the issues itself.

*Experiment datasets*: 
```bash
datasets
└─── RepromptingAnalysis
     └─── mathwell_separated.json
```

### Experiment 4: Instruction Reordering

For this experiment, we try to assess the accuracy of
instruction following over all the possible combinations of the added instruction.

*Experiment datasets*: 
```bash
datasets
└─── ReorderingAnalysis_Ifeval
     ├─── mathwell_combi_0.jsonl
     ├─── mathwell_combi_1.jsonl
     ├─── mathwell_combi_2.jsonl
     ├─── mathwell_combi_3.jsonl
     ├─── mathwell_combi_4.jsonl
     └─── mathwell_combi_5.jsonl
```

### Experiment 5: Step-by-step Prompting

In this experiment, we specifically consider two broad
ways of providing instructions to LLMs – all together or step-by-step. In the former, we simply append all instructions to the base prompt (as seen
in earlier examples) and then feed this to the LLM.
In the latter, we split the instructions over different
'steps' (each constitutes one instruction) and then
feed these and the base prompt to the LLM one by
one. We further expand this step-by-step technique
by introducing an extra statement: 'Along with this
instruction, follow all previous instructions as well'
to be appended to every instruction prompt. We
call this specific prompting method 'step-by-step
(aid)'

*Experiment datasets*: 
```bash
datasets
└─── ReorderingAnalysis_Ifeval
     └─── mathwell_combi_1.jsonl
```

## Generate responses for experiments

First install [Ollama](https://ollama.com)

Then pull the required models:
```bash
ollama pull llama3
ollama pull mistral
ollama pull gemma
```

To use GPT put the API key in a file named `openai.key` in the base directory of the repo.

Run the commands below to generate the responses for experiments 1, 2, 4, and 5
```bash
python utils/ifeval_gen_response.py 
python utils/ifeval_partwise_gen_response.py
python utils/info_gen_response.py
python utils/info_ifeval_gen_response.py
```

The response generation, evaluation and report generation is done simultaneously and can be done using the script `utils/analysis.py`.

## Evaluate the generated responses

To evaluate the responses run:
```bash
bash utils/ifeval_eval.sh
bash utils/info_eval.sh
```

## Generate the reports

### Experiment 1
This will print stats for each dataset and model:
```bash
python utils/evaluate_responses.py
```

### Experiment 2
This will print the table as seen in the paper:
```bash
python utils/evaluate_complex.py
```

### Experiment 3
This will generate the file `datasets/RepromptingAnalysis/response/<model>/eval_results.json` with the results in it:
```bash
python utils/analysis.py
```

`model` is the model set in the python script.

### Experiment 4
The command below will generate the histogram in `datasets/ReorderingAnalysis_Ifeval/reordering_hist.pdf`
```bash
python utils/reordering_summary.py
```

### Experiment 5
This will generate the results and store it in
`datasets/ReorderingAnalysis_Ifeval/results.csv`:
```bash
python utils/turnwise_summary.py
```
