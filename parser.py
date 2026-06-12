#just a small test run to see if itll respond

import requests
import json
import re
from locations import get_locations

ollama_port = "http://localhost:11434/api/generate"

#!!! place to change model, was: phi3:mini, now is: mistral:7b, try next: llama3.1:8b
model = "qwen2.5:3b-instruct"

system_prompt  = """
You are ORION, an octopus-inspired robotic arm assistant. Parse user voice commands into JSON actions for controlling the arm or answering questions.

Output ONLY a single valid JSON object. No explanations, markdown, code blocks, or extra text.

For questions, answer directly, concisely, and efficiently.

Available actions and formats:

User: "grab my phone"
{"action":"grab","target":"phone","coordinates":[18.3,14.7],"claw_force":0.5}

Synonyms for grab: pick up, get, fetch, retrieve.

User: "put it in the bin"
{"action":"move_to","location":"bin","coordinates":[8.2,24.1]}

Synonyms for move_to: move to, throw, move, take it, put, (use these when followed by a location).

User: "drop it right here"
{"action":"drop"}

User: "stow the arm away"
{"action":"stow"}

Synonyms for stow: put away, fold up, retract, go away.

User: "what is this?"
{"action":"describe","query":"what is this?"}

User: "grab that thing"
{"action":"clarify","message":"did you want me to grab the phone or the pen?"}

User: "How do magnets work?"
{"action":"chat","response":"Magnets work through..."}

User: "Where is my bin?"
{"action":"where_is","target":"bin"}

Claw force scale:
- fragile (phone, pen): 0.3
- normal (cup, mouse): 0.6
- heavy (book, keyboard): 0.9

Rules:
- Output only valid JSON.
- If the target exists in world_state, use its coordinates.
- If a command is unclear, use:
  {"action":"clarify","message":"..."}
- If no object is specified for a grab action, use clarify.
- General questions or conversation not involving object manipulation use:
  {"action":"chat","response":"..."}
- If an object is named but not found in world_state, still use the appropriate action and set:
  "coordinates": null
- Do not use describe or clarify solely because coordinates are unknown.
- If you have a question about something, use clarify, not chat
"""



def ask_phi3(prompt, system = system_prompt):
    response = requests.post(ollama_port, json = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "system": system,
        "options": {
            "temperature": 0.2, #changes temp to make it less sporadic (test 0.2 or 0.3)
            "top_p": 0.5,
            "num_predict": 100,
            "stop": ["\n\n", "---", "Voice command"]#stop it frrom hallucinating
        }
        
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
        "phone": {"bbox": [245, 312, 489, 701], "confidence": 0.91, "desk_coords": [18.3, 14.7]},
        "cup": {"bbox": [100, 200, 180, 300], "confidence": 0.86, "desk_coords": [8.1, 24.2]}

    }

    test_commands = [
        "grab my phone",
       "throw it in the bin",
       "where is sid_house",
    ]
    
    print("Parser test")

    for command in test_commands:
        print(f"Command: '{command}'")
        result = parse_command(command, test_world_state)
        print(f"Action: {result}") 


if __name__ == "__main__":
    test_parser()
