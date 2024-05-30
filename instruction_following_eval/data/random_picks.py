import json
import random

def pick_random_samples(file_path, num_samples):
    samples = []
    with open(file_path, 'r') as file:
        for line in file:
            sample = json.loads(line)
            samples.append(sample)
    # print(len(samples))
    random_samples = random.sample(samples, num_samples)
    return random_samples

file_path = '/Users/piyushigoyal/Documents/ETH-Zurich/SEM 2/CSNLP/Project/CS4NLP-Project/datasets/InfoBench/dataset.jsonl'
num_samples = 100

random_samples = pick_random_samples(file_path, num_samples)
output_file_path = '/Users/piyushigoyal/Documents/ETH-Zurich/SEM 2/CSNLP/Project/CS4NLP-Project/datasets/InfoBench/infobench_subset.jsonl'
with open(output_file_path, 'w') as output_file:
    for sample in random_samples:
        output_file.write(json.dumps(sample) + '\n')
