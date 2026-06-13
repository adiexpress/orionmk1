from detector import detect_objects
from camera import CameraSystem
from config import detection_confidence

def merge_world_states(states: list[dict]) -> dict:
    """
    Merge world states from multiple cameras

    Priority: claw -> left -> right

    When same object detected by multiple cameras:
    -keep highest confidence score
    -average coordinates if confidence is within 0.1 of each other
    -otherwise trust the higher confidence detection's coordinates
    """

    merged = {}

    for state in states:
        if not state:
            continue

        for obj_name, data in state.items():
            if obj_name not in merged:
                #if object isnt in merged, add ot
                merged[obj_name] = data.copy()
            else:
                existing = merged[obj_name]
                incoming = data
                existing_confidence = existing["confidence"]
                incoming_confidence = incoming["confidence"]

                #if both cameras confidence score is within 0.1 - average coordinates
                if abs(existing_confidence - incoming_confidence) <= 0.1:
                    if "desk_coords" in existing and "desk_coords" in incoming:
                        #averaging coordinates
                        merged[obj_name]["desk_coords"] = [
                            (existing["desk_coords"][0] + incoming["desk_coords"][0]) / 2,
                            (existing["desk_coords"][1] + incoming("desk_coords")[1]) / 2,
                        ]

                    #keep higher confidence value
                    merged[obj_name]["confidence"] = max(existing_confidence, incoming_confidence)

                #if incoming is more confident, keep that, else stick with existing
                elif incoming_confidence > existing_confidence:
                    merged[obj_name] = incoming.copy()

    return merged

def run_detection(camera_system: CameraSystem, homographies: dict) -> tuple: 
    #Run detection on all 3 cameras and return merged world state.

    from conversion import pixel_conversion, box_center 

    frames = camera_system.get_all_frames()
    annotated_frames = {}
    states = []

    camera_priority = ["claw", "left", "right"]

    for cam_name in camera_priority:
        frame = frames.get(cam_name)

        if frame is None:
            states.append({})

        try:
            annotated, detections, world_state = detect_objects(frame)
            annotated_frames[cam_name] = annotated

            #add desk coords using camera homography   
            H = homographies.get(cam_name)
            if H is not None:
                for obj_name, data in world_state.items():
                    if "bbox" not in data:
                        continue
                    cx, cy = box_center(data["bbox"])
                    desk_x, desk_y = pixel_conversion(cx, cy, H)
                    world_state[obj_name]["desk_coords"] = [desk_x, desk_y]
                    world_state[obj_name]["desk_coords"] = cam_name

            states.append(world_state)
        
        except Exception as e:
            print(f"[MULTI DETECTOR] {cam_name} camera failed: {e}")
            states.append({})
    
    merged = merge_world_states(states)
    return annotated_frames, merged

def load_all_homographies():
    #load calibration matricies
    #each camera will have its own calibration.json file
    #returns {camera_name: H_matrix} or None if not calibrated

    import json
    import numpy as np
    import os

    calibration_files = {
        "left": "calibration_left.json",
        "right": "calibration_right.json",
        "claw": "calibration_claw.json"
    }

    homographies = {}

    for cam_name, filepath in calibration_files.items():
        if not os.path.exists(filepath):
            print(f"[MULTI DETECTOR] No calibration for {cam_name} camera")
            homographies[cam_name] = None
            continue

        try:
            with open(filepath, "r") as file:
                data = json.load(file)
            homographies[cam_name] = np.float32(data["homo_matrix"])
            print(f"[MULTI DETECTOR] Loaded calibration for {cam_name} camera")
        except Exception:
            print(f"[MULTI DETECTOR] Failed to load calibration for {cam_name}")
            homographies[cam_name] = None

    return homographies