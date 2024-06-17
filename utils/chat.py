import json
import os
from openai import OpenAI
from glob import glob
import warnings

_models = dict()

def _init():
    global _models
    key_files = glob("*.key")
    keys = dict()
    for file in key_files:
        with open(file, 'r') as f:
            name = os.path.splitext(file)[0]
            keys[name] = f.readline().strip()
            if keys[name] is None or keys[name] == "":
                raise Exception(f"The {file} is empty or corrupt")
            
    # ollama is an exception
    keys["ollama"] = "ollama"
        
    warned = []
    with open('config.json', 'r') as f:
        config_data = json.load(f)
        for model in config_data["models"].keys():
            _models[model] = config_data["models"][model]
            try:
                _models[model]["api_key"] = keys[_models[model]["api_key"]]
            except KeyError as e:
                _models[model]["api_key"] = Exception(f"Please supply a {e.args[0]}.key file to use this model.")
                if not e.args[0] in warned:
                    warned.append(e.args[0])
                    print(f"\tWarning: {e.args[0]}.key file not present. Using a model that needs this key will raise an Exception.")


_init()

def chat(model, messages=[], message="", choice=0):
    global _models
    assert model in _models.keys(), f"Please supply a valid model from config.json. Supplied: {model}"
    assert ((messages == []) ^ (message == "")), f"Supply either the 'messages' arg ({('supplied' if (messages == []) else 'not supplied' )}) or the 'message' arg ({('supplied' if (messages == []) else 'not supplied') }){(' not both.')}"
    

    model = _models[model]
    
    if messages == []:
        messages=[
            {"role" : "user", "content" : message}
        ]
    
    if isinstance(model["api_key"], Exception):
        raise model["api_key"]

    client = OpenAI(
        base_url = model["base_url"] if model["base_url"] != "" else None,
        api_key = model["api_key"],
    )
    
    response = client.chat.completions.create(
        model=model["model_name"],
        messages=messages
    )
    return response.choices[choice].message.content