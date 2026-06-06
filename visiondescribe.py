#if an objedct is held up to the webcam, it will describe the object in the webcame
#uses llava phi 3 by microsoft

import ollama
import cv2
import base64
import time

#converts cv2 frame to base64 string for LLaVA to use
def frame_to_base64(frame):
    _, buffer = cv2.imencode(".jpg", frame)
    return base64.b64encode(buffer).decode("utf-8")

#captures single frame from webcam
def capture_frame():
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    time.sleep(2)
    cap.release()
    if not ret:
        return None
    return frame

#main file
#sends camera fram to LLaVA with a question, returns answer as string
def describe_webcam(query = "what do you see on the desk?", frame = None):
    
    if frame is None:
        frame = capture_frame()
    if frame is None:   
        return "I couldn't access the camera"
    
    image_base64 = frame_to_base64(frame)

    try:
        response = ollama.chat(model = "llava-phi3", 
            messages = [{ 
                    "role": "user", "content": query, "images": [image_base64]
                }
            ]                         
        )
        return response["message"]["content"].strip()
        
    
    except Exception:
        return f"Vision error: {Exception}"
    
    

#testing vision
def test_vision():
    print("Put something in front of your camera\n")

    testcases = [
        "what objects do you see?",
        "what is the color of the smaller object" #its the blue side of a rubix cube btw
    ]

    for question in testcases:
        print(f"Question: {question}")
        answer = describe_webcam(question)
        print(f"Response: {answer}\n")



if __name__ == "__main__":
    test_vision()

    


