#just a small test run to see if itll respond

import requests
import json
import re
from locations import get_locations

ollama_port = "http://localhost:11434/api/generate"
model = "phi3:mini"

system_prompt  = """
You are ORION, an octopus-inspired robotic arm assistant. Your job
is to parse voice commands into JSON actions to control the arm and answer general questions.

Output ONLY a single JSON object. No long explanations, code blocks, markdowns, or preambles.
Just the raw JSON

When answering questions, be sure to clearly identify the question and find the most efficient way to answer it, no long rambles or paragraphs unless necessary.

Be concise and minimal with your words and answer directly, no dancing around the question.

Avaliable actions and their exact format:

{"action": "grab", "target": "phone", "coordinates": [18.3, 14.7], "claw force": 0.5}
{"action": "move_to", "location": "bin", "coordinates": [8.2, 24.1]}
{"action": "drop}
{"action": "stow}
{"action": "describe", "query": "what is this?"}
{"action": "clarify", "message": "did you want me to grab the phone or the pen?"}
{"action": "chat", "response": "the answer to the question here"}
{"action": "where_is", "target": "sid_house, "coordinates": [20000.0, 40000.0]}

Claw force required scale:
- fragile objects (phone, pen): 0.3
- normal objects (cup, mouse): 0.6
- heavy objects (book, keyboard): 0.9

Rules:
- only output the valid JSON and nothing else
- if the target object is in world_state, use its given coordinates
- if the user's command is unclear, ask for clarification through the clarify action
- if no object is directly specified to grab, ask for clarification by using clarify
- if the command is a general question or conversational topic not related to grabbing or moving objects, use the chat action and answer it in the response field
"""



def ask_phi3(prompt, system = system_prompt):
    response = requests.post(ollama_port, json = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "system": system,
        
        }) 
    
    return response.json()["response"].strip()

def parse_command(transcribed_text, world_state ={}):
    prompt = f"""
voice command: "{transcribed_text}"
current world state: {json.dumps(world_state)}

Output the JSON action now:
"""
    

    raw = ask_phi3(prompt)
    print(f"raw output: {raw}")
    #strips markdown code blocks
    raw = re.sub(r"'''json|'''", "", raw).strip()

    # extracts only the JSON object and ignores everythign after
    match = re.search(r'\{.*?\}', raw, re.DOTALL)

    if not match:
        print(f"No JSON found in output: {raw}")
        return None

    raw = match.group(0)

    #fixes claw force key if model uses spaces instead of underscore
    raw = raw.replace('"claw force"', '"claw_force"')   
    
    
    
    try:
        action = json.loads(raw)
        action = resolve_coordinates(action, world_state)
        return action
    except json.JSONDecodeError:
        print(f"Failed to parse json: {raw}")
        return None

def resolve_coordinates(action, world_state):
    # fills coords for actions that dont yet have them, checks world state first then named locations

    if action.get("action") == "move_to":
        locations_name = action.get("location", "")
        coords = get_locations(locations_name)

        if coords:
            action["coordinates"] = coords
        else:
            action = {"action": "clarify", "message": f"I don't know where {locations_name} is"}
    

    elif action.get("action") == "grab":
        target = action.get("target", "")
        
        if target in world_state:
            action["coordinates"] = world_state[target]["desk_coords"]
        else:
            coords = get_locations(target)
            action["coordinates"] = coords
    
    
    elif action.get("action") == "where_is":
        target = action.get("target", "")
        coords = get_locations(target)
        action["coordinates"] = coords


    return action
#testing

def test_parser():
    test_world_state = {
        "phone": {"box": [245, 312, 489, 701], "confidence": 0.91, "desk_coords": [18.3, 14.7]},
        "cup": {"box": [100, 200, 180, 300], "confidence": 0.86, "desk_coords": [8.1, 24.2]}

    }

    test_commands = [
        "grab my phone",
       "throw it in the bin",
       "where is sid_house",
    #     "put the arm away",
    #     "what is this thing",
    #     "grab that thing on my desk",
    #     "how do magnets work",
    #     "what is the area of great britain in kilometers",
    ]
    
    print("Parser test")

    for command in test_commands:
        print(f"Command: '{command}'")
        result = parse_command(command, test_world_state)
        print(f"Action: {result}") 


if __name__ == "__main__":
    test_parser()
