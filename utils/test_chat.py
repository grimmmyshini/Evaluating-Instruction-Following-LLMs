from chat import chat
import json

with open("config.json", 'r') as file:
    data = json.load(file)
    for model in data["models"]:
        response = chat(model, message="Do you know about ChatGPT?")              # Single message API
        print(f"Model: {model}\tType: Single Message\nResponse:\n{response}")

        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Do you know about ChatGPT?"},
        ]
        response = chat(model, messages=messages)                                 # Chat format API
        print(f"Model: {model}\tType: Chat format\nResponse:\n{response}")