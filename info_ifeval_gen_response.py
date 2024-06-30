from pathlib import Path
import json

all_paths = [
    {
        "info_ifeval": "datasets/MMLU_Info_Ifeval/response/mmlu_info_ifeval",
        "ifeval": "datasets/MMLU_Ifeval/response/mmlu_ifval",
        "info": "datasets/MMLU_InfoBench/response/mmlu_info"
    },
    {
        "info_ifeval": "datasets/MATHWELL_Info_Ifeval/response/mathwell_info_ifeval",
        "ifeval": "datasets/MATHWELL_Ifeval/response/mathwell_ifeval",
        "info": "datasets/MATHWELL_Info/response/mathwell_info"
    },
]

for paths in all_paths:
    ifeval_info_path = Path(paths["info_ifeval"])
    info_path = Path(paths["info"])
    ifeval_path = Path(paths["ifeval"])

    def read_jsonl_file(filepath):
        with filepath.open('r', encoding='utf-8') as file:
            return [json.loads(line) for line in file]

    ifeval_info_path.mkdir(parents=True)
    src = ifeval_path.parent.parent / (ifeval_path.name + ".jsonl")
    dest = ifeval_info_path.parent.parent / (ifeval_info_path.name + ".jsonl")
    dest.write_text(src.read_text())

    for model in ['gemma', 'gpt4', 'gpt4o', 'llama3', 'mistral']:
        info_file = read_jsonl_file(info_path / model / "output.jsonl")
        ifeval_file = read_jsonl_file(ifeval_path / model / "output.jsonl")
        for info_json, ifeval_json in zip(info_file, ifeval_file):
            assert info_json["input"] in ifeval_json["prompt"]
            out_json = {
                "prompt": ifeval_json["prompt"],
                "response": info_json["output"]
            }
            (ifeval_info_path / model).mkdir(exist_ok=True)
            with open(ifeval_info_path / model / "output.jsonl", "a") as f:
                f.write(json.dumps(out_json) + '\n')