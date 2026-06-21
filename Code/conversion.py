import cv2
import numpy as np
import json

def load_homo_matrix(path = "calibration.json"): #loads the saved config from the calibration
    with open(path, "r") as file:
        data = json.load(file)
    return np.float32(data["homo_matrix"])

def pixel_conversion(px,py,H): #px and py are the pixel coords we are trying to convert
#converts  pixel coords into real world cm

    pixel_point = np.float32([[[px, py]]])
    real_point = cv2.perspectiveTransform(pixel_point, H)

    real_x = round(float(real_point[0][0][0]), 1)
    real_y = round(float(real_point[0][0][1]), 1)

    return real_x, real_y

def box_center(bbox):
   #gets the center pixel to use for the template measurement
    x1, y1, x2, y2 = bbox
    return (x1+x2)//2, (y1+y2)//2



    
