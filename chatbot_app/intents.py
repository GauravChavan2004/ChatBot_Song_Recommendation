import json

def load_intents():
    try:
        with open('./chatbot_app/intents.json') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Error: intents.json file not found")
        return {}
    except json.JSONDecodeError:
        print("Error: invalid JSON in intents.json file")
        return {}

intents = load_intents()