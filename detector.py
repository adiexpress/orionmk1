from ultralytics import YOLO
import cv2
import pandas as pd

#loads model
model = YOLO('yolov8n.pt')

priority_objects = {"person", "cell phone", "cup", "keyboard", "mouse", "pen", "book", "hand"} #making a list of priority objects that it detects so it doesnt waste time on other stuff

name_mapping = {"person" : "person",
    "cell phone": "phone", #name mapping 
                "cup": "cup",
                "keyboard": "keyboard",
                "mouse": "mouse",
                "pen": "pen",
                "book": "book",
                "hand": "hand",
                }

#detecting objects via webcam;
def detect_objects(frame):
    
    results = model(frame)
    detections = []
    world_state = {}
    
    for result in results:
        for box in result.boxes:
            class_id = int(box.cls[0])
            confidence = float(box.conf[0].item())
            label = model.names[class_id]

            if label not in priority_objects:
                continue

            if confidence > 0.5:
                fname = name_mapping[label]
                x1, y1, x2, y2 = map(int, box.xyxy[0])
            
            world_state[fname] = {"box" : [x1,y1,x2,y2], "confidence": round(confidence, 2)} #creates the world state var
            
            detections.append((fname, confidence))
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, f"{fname} {confidence:.2f}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
    return frame, detections, world_state

#opens webcam and allows user to quit when q is pressed
def main():
    cap = cv2.VideoCapture(0)
    frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame, detections, world_state = detect_objects(frame) #detects objects in the frame and returns the frame with bounding boxes and the detections list
        
        if frame_count % 20 == 0 and world_state: #limits the terminal spam by only calling world state every 20 frames
            print("World state: ", world_state)
        
        frame_count += 1

        
        cv2.imshow("ORION", frame)
        
        if detections:
            print("Detections:", detections) #if there are detections, print them 
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":   
    main()

    









    