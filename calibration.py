import cv2
import numpy as np
import json 

real_world_points = np.float32([[12, 11],
                                [29, 11],
                                 [12, 28],
                                  [29, 28], ])

num_points = 4 #min number of points needed to click for calibration

clicked_points = [] #used to store the points clicked by the user

def click_event(event, x, y, flags, params): #records the pixel coordinates of the point when you click on it
    if event == cv2.EVENT_LBUTTONDOWN:
        if len(clicked_points) < num_points:
            clicked_points.append([x,y])
            print(f"point {len(clicked_points)} ({x}, {y})")


def save_calibration(camera_name = "main"):
    """
    camera_name = "left", "right", or "claw"
    saves to calibration_{camera_name}.json
    """

    pixel_points = np.float32(clicked_points)

    H, status = cv2.findHomography(pixel_points, real_world_points)

    if H is None:
        print("ERROR: Could not calculate homography")
        return
    
    filename = f"calibration_{camera_name}.json"
    calib_data = {
        "homo_matrix": H.tolist(),
        "pixel_points": pixel_points.tolist(),
        "real_world_points": real_world_points.tolist(),
        "camera": camera_name
    }

    with open(filename, "w") as file:
        json.dump(calib_data, file, indent = 4)

    print(f"Calibration saved to {filename}")

def main(): 
    cap = cv2.VideoCapture(0) 
    cv2.namedWindow('Calibration')
    cv2.setMouseCallback('Calibration', click_event)

    print("Orion Calibration Tool:")
    print(f"Click on your {num_points} in the following order to calibrate")
    print("top left, top right, bottom left, bottom right")
    print("press s to save and q to quit")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        for i, (px, py) in enumerate(clicked_points): #essentially highlights the already clicked points
            cv2.circle(frame, (px, py), 6, (0,255,0), -1)
            cv2.putText(frame, str(i+1), (px+ 10, py - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        remaining = num_points - len(clicked_points)
        
        if remaining > 0:
            message = f"Click {remaining} more points"
        else:
            message = "Calibration points clicked, Press S to save"
        
        cv2.putText(frame, message, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 200, 255), 2)

        cv2.imshow("Calibration", frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord("s") and len(clicked_points) == num_points:
            save_calibration()
            break
        elif key == ord("q"):
            print("Quitted")
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    import sys 
    cam_name = sys.argv[1] if len(sys.argv) > 1 else "main"
    print(f"Calibrating {cam_name} camera")
    main(cam_name)



        






