#this is orion's brain 
#main file that wires everything together(voice, parsing, action handling)
#run this file to start orion

import json
import cv2
import multiprocessing as mp
from voice import voice_command
from parser import parse_command
from detector import detect_objects, model, name_mapping, priority_objects #bruh
from speech import speak
from conversion import load_homo_matrix, pixel_conversion, box_center
from visiondescribe import describe_webcam
import time
import sounddevice as sd


#global world state, all parse calls read from this so the arm always has a current position
world_state = {}

#action handler
def handle_action(action):

    #recieves an action dict that tells it what to do and does it
    #for now it just prints what happnes
    #hardware commands come later

    if action is None:
        speak("No action")
        return

    action_type = action.get("action")

    if action_type == "grab":
        target = action.get("target")
        coords = action.get("coordinates")
        force = action.get("claw_force", 0.5)

        if not target: #handles grab even with no target
            speak("Please specify target")
            return
        
        #handles grab even when coords are null
        if coords is None:
            speak(f"I can't see your {target} right now")
        else:
            speak(f"Grabbing {target}")


        print(f"[GRAB] target = {target} coords = {coords} force = {force}")

    elif action_type == "move_to":
        location = action.get("location")
        coords = action.get("coordinates")
        
        if coords is None:
            speak(f"Please specify where {location} is")
            return
        
        speak(f"Moving object to {location}")
        print(f"[MOVE] location = {location} coords = {coords}")
    
    elif action_type == "drop":
        speak("dropping object")
        print("[DROP] dropping object")
    
    elif action_type == "stow":
        speak("Stowing arm")
        print("[STOW] stowing arm")

   #added describe webcam function so that orion actually sees what is on the desk and describes it
    elif action_type == "describe":
        query = action.get("query", "What do you see?")
        speak("Let me take a look")
        try:
            answer = describe_webcam(query)
            speak(answer)
            print(f"[DESCRIBE] {answer}'")
        except Exception as e:
            speak("I couldn't access camera")
            print("Describe failed")
    
    elif action_type == "clarify":
        message = action.get("message", "Could you repeat that")
        speak(f"{message}")
        print(f"[CLARIFY] {message}")

    elif action_type == "chat":
        response = action.get("response", "")
        if not response:
            speak("I'm not quite sure")
        speak(f"{response}")
        print(f"[CHAT] {response}")

    elif action_type == "where_is":
        
        from locations import get_locations
        
        target = action.get("target", "")
        coords = get_locations(target)

        if coords:
            speak(f"{target} is at {coords[0]} centimeters by {coords[1]} centimeters")
        else:
            speak(f"No {target} location saved")

        print(f"[WHERE IS] target = {target} coords = {coords}")

    else:
        speak(f"[UNKNOWN] {action}")

#camera thread function
#  # Initialized world state

#main file
def main():

    state_queue = mp.Queue(maxsize = 10)

    #camera runs in its own process
    camera_process = mp.Process(target = camera_loop, args = (state_queue,), daemon = True)
    camera_process.start()

    world_state = {}

    time.sleep(1)
    
    
    speak("Welcome home sir")
    print("Say wake word + command. Ctrl+C to stop\n")


    try:
        while True:
            while not state_queue.empty():
                try:
                    world_state = state_queue.get_nowait()
                except:
                    pass
                # printing current world_state
            print(f"Current world state: {list(world_state.keys())}")

                # listen for voice command
            command = voice_command()
                
            if not command:
                continue

            while not state_queue.empty():
                try:
                    world_state = state_queue.get_nowait()
                except:
                    pass
                
            print(f"\nParsing: '{command}'")

            try:
                action = parse_command(command, world_state)
                if action is None:
                    speak("Clarify action")
                    continue
                    
                handle_action(action)

            except Exception as e:
                print(f"[ERROR] {e}")
                speak("Error parsing")

            print()

    except KeyboardInterrupt:
        camera_running = False
        speak("Orion Stopped")
        return

#camera loop (no webcam so no need to be on main)
def camera_loop(state_queue):
    global world_state, camera_running
    
    H = load_homo_matrix()
    camera_running = True
    world_state = {} 
    
    cap = cv2.VideoCapture(0)

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'NV12'))
    
    if not cap.isOpened():
        print("Error: could not open camera")
        return

    print("Camera started")

    while camera_running:
        ret, frame = cap.read()
        if not ret:
            continue
            
        try:
            frame, detections, new_state = detect_objects(frame)

            # update world state with desk coords
            for obj_name, data in new_state.items():
                if "bbox" not in data:
                    continue
                cx, cy = box_center(data["bbox"])
                desk_x, desk_y = pixel_conversion(cx, cy, H)
                new_state[obj_name]["desk_coords"] = [desk_x, desk_y]

                # Safely hand off state data to the background voice loop
                world_state = new_state

            try:
                state_queue.put_nowait(new_state)
            except:
                pass

        except Exception as e:
            pass
            
            time.sleep(0.05)
        
        cap.release()

if __name__ == "__main__":
    mp.set_start_method("spawn", force = True)
    main()





