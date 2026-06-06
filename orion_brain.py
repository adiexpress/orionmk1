#this is orion's brain 
#main file that wires everything together(voice, parsing, action handling)
#run this file to start orion

import json
import cv2
import threading
from voice import voice_command
from parser import parse_command
from detector import detect_objects, model, name_mapping, priority_objects #bruh
from speech import speak
from conversion import load_homo_matrix, pixel_conversion, box_center
from visiondescribe import describe_webcam
import time

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
        force = action.get("claw_force")
        
        #handles grab even when coords are null
        if coords is None:
            speak(f"I can't see your {target} right now")
        else:
            speak(f"Grabbing {target}")


        print(f"[GRAB] target = {target} coords = {coords} force = {force}")

    elif action_type == "move_to":
        location = action.get("location")
        coords = action.get("coordinates")
        speak(f"Moving object to {location}")
        print(f"[MOVE] location = {location} coords = {coords}")
    
    elif action_type == "drop":
        speak("[DROP] dropping object")
    
    elif action_type == "stow":
        speak("[STOW] stowing arm")
    
   #added describe webcam function so that orion actually sees what is on the desk and describes it
    elif action_type == "describe":
        query = action.get("query", "What do you see?")
        speak("Let me take a look")
        answer = describe_webcam(query)
        speak(answer)
        print(f"[DESCRIBE] {answer}'")
    
    elif action_type == "clarify":
        message = action.get("message")
        speak(f"{message}")
        print(f"[CLARIFY] {message}")

    elif action_type == "chat":
        response = action.get("response")
        speak(f"{response}")
        print(f"[CHAT] {response}")

    elif action_type == "where_is":
        
        from locations import get_locations
        
        target = action.get("target", "")
        coords = get_locations(target)

        if coords:
            speak(f"{target} is at {coords}")
        else:
            speak(f"No {target} location saved")

        print(f"[WHERE IS] target = {target} coords = {coords}")

    else:
        speak(f"[UNKNOWN] {action}")

#camera thread function
H = load_homo_matrix()
camera_running = True
world_state = {}  # Initialized world state


# 1. MOVED TO BACKGROUND: Voice listening and command execution
def voice_command_loop():
    global camera_running, world_state

    speak("Welcome home sir")
    print("Say wake word + command. Ctrl+C to stop\n")


    try:
        while camera_running:


            # printing current world_state
            print(f"Current world state: {list(world_state.keys())}")

            # listen for voice command
            command = voice_command()
            if not command:
                continue

            print(f"\nParsing: '{command}'")

            # parse command with current world state
            action = parse_command(command, world_state)

            # after parsing the action, making sure the model knows what to do for each one
            handle_action(action)
            print()

    except KeyboardInterrupt:
        camera_running = False
        speak("\n\nOrion Stopped")


# 2. KEPT ON MAIN THREAD: OpenCV GUI and Frame Capture
def main():
    global world_state, camera_running

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: could not open camera")
        return

    print("Camera started")

    # Start the voice command system in the background thread
    voice_thread = threading.Thread(target=voice_command_loop, daemon=True)
    voice_thread.start()

    try:
        while camera_running:


            ret, frame = cap.read()
            if not ret:
                continue
            try:
                frame, detections, new_state = detect_objects(frame)

                # update world state with desk coords
                for obj_name, data in new_state.items():
                    cx, cy = box_center(data["bbox"])
                    desk_x, desk_y = pixel_conversion(cx, cy, H)
                    new_state[obj_name]["desk_coords"] = [desk_x, desk_y]

                # Safely hand off state data to the background voice loop
                world_state = new_state

                # Show camera feed safely on the main OS thread
                cv2.imshow("ORION Vision", frame)

                # Handle windows/macOS keyboard break safely
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    camera_running = False
                    break
            except Exception as e:
                pass


    except KeyboardInterrupt:
        print("\nStopping via terminal interrupt...")
    finally:
        camera_running = False
        cap.release()
        cv2.destroyAllWindows()
        speak("\n\nOrion Stopped")


if __name__ == "__main__":
    main()





