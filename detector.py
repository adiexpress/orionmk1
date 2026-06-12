# from ultralytics import YOLO
# import cv2
# import pandas as pd

# #loads model
# model = YOLO('yolov8n.pt')

# priority_objects = {"person", "cell phone", "cup", "keyboard", "mouse", "pen", "book", "hand"} #making a list of priority objects that it detects so it doesnt waste time on other stuff

# name_mapping = {"person" : "person",
#     "cell phone": "phone", #name mapping 
#                 "cup": "cup",
#                 "keyboard": "keyboard",
#                 "mouse": "mouse",
#                 "pen": "pen",
#                 "book": "book",
#                 "hand": "hand",
#                 }

# #detecting objects via webcam;
# def detect_objects(frame):
    
#     results = model(frame, verbose=False)
#     detections = []
#     world_state = {}
    
#     for result in results:
#         for box in result.boxes:
#             class_id = int(box.cls[0])
#             confidence = float(box.conf[0].item())
#             label = model.names[class_id]

#             if label not in priority_objects:
#                 continue

#             if confidence > 0.5:
#                 fname = name_mapping[label]
#                 x1, y1, x2, y2 = map(int, box.xyxy[0])
            
#                 world_state[fname] = {"bbox" : [x1,y1,x2,y2], "confidence": round(confidence, 2)} #creates the world state var
            
#                 detections.append((fname, confidence))
#                 cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
#                 cv2.putText(frame, f"{fname} {confidence:.2f}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
#     return frame, detections, world_state

# #opens webcam and allows user to quit when q is pressed
# def main():
#     cap = cv2.VideoCapture(0)
#     frame_count = 0

#     while True:
#         ret, frame = cap.read()
#         if not ret:
#             break
        
#         frame, detections, world_state = detect_objects(frame) #detects objects in the frame and returns the frame with bounding boxes and the detections list
        
#         if frame_count % 20 == 0 and world_state: #limits the terminal spam by only calling world state every 20 frames
#             print("World state: ", world_state)
        
#         frame_count += 1

        
#         cv2.imshow("ORION", frame)
         
        
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break

#     cap.release()
#     cv2.destroyAllWindows()


# if __name__ == "__main__":   
#     main()

#going to upgrade to the hailo v8 version
import cv2
import numpy as np
from config import is_pi, detection_confidence, priority_objects, name_mapping

#coco classes (all 80)
coco_classes = [
    'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck',
    'boat', 'traffic light', 'fire hydrant', 'stop sign', 'parking meter', 'bench',
    'bird', 'cat', 'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra', 'giraffe',
    'backpack', 'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee', 'skis', 'snowboard', 
    'sports ball', 'kite', 'baseball bat', 'baseball glove', 'skateboard', 'surfboard', 
    'tennis racket', ' bottle', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl', 
    'banana', 'apple', 'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza', 'donut',
    'cake', 'chair', 'couch', 'potted plant', 'bed', 'dining table', 'toilet', 'tv', 'laptop',
    'mouse', 'remote', 'keyboard', 'cell phone', 'microwave', 'oven', 'toaster', 'sink', 'refridgerator',
    'book', 'clock', 'vase', 'scissors', 'teddy bear', 'hair drier', 'toothbrush'
]
    
if is_pi:
    from hailo_platform import (
        HEF, Device, VDevice, 
        InputVStreamParams, OutputVStreamParams,
        FormatType, HailoStreamInterface,
        InferVStreams, ConfigureParams
    )

    HEF_path = "yolov8n.hef" #from hailo model zoo

    _hef = HEF(HEF_path)
    _device = Device.scan()
    _target = VDevice(device_ids=_device)
    _configure_params = ConfigureParams.create_from_hef(_hef, interface = HailoStreamInterface.PCIe)

    _network_group = _target.configure(_hef, _configure_params)[0]
    _network_group_params = _network_group.create_params()
    _input_info = _hef.get_input_vstream_infos()
    _output_info = _hef.get_output_vstream_infos()
    _input_vstream_params = InputVStreamParams.make_from_network_group(_network_group, quantized = False, format_type = FormatType.FLOAT32)
    _output_vstream_params = OutputVStreamParams.make_from_network_group(_network_group, quantized = False, format_type = FormatType.FLOAT32)

    #input shape for yolov8 is 640x640
    _input_h = _input_info.shape[0]
    _input_w = _input_info.shape[1]
    print(f"Hailo-8 Ready. Input shape: {_input_h}x{_input_w}")

else:
    from ultralytics import YOLO
    _cpu_model = YOLO("yolov8n.pt")
    print("CPU YOLOv8n loaded (dev mode)")

#inferences


def detect_objects(frame):
    if is_pi:
        return _detect_hailo(frame)
    else:
        return _detect_cpu(frame)


def _detect_hailo(frame):
    world_state = {}
    detections = []

    orig_h, orig_w = frame.shape[:2]

    resized = cv2.resize(frame, (_input_w, _input_h))

    #convert to float32
    input_data = {_input_info.name: np.expand_dims(resized.astype(np.float32), axis = 0)}

    with InferVStreams(_network_group, _input_vstream_params, _output_vstream_params, tf_nms_format = True) as infer_pipeline:
        with _network_group.activate(_network_group_params):
            output_data = infer_pipeline.infer(input_data)

    #scale back up to original frame size
    scale_x = orig_w / _input_w
    scale_y = orig_h / _input_h

    for key in output_data.keys():
        output = output_data[key][0]
        num_classes = output.shape[0]
        num_detections = output.shape[2]

        for class_id in range(num_classes):
            class_name = coco_classes[class_id] if class_id < len(coco_classes) else "unknown"

            if class_name not in priority_objects:
                continue
            
            for det_id in range(num_detections):
                bbox = output[class_id, :, det_id]
                confidence = float(bbox[4])

                if confidence < detection_confidence:
                    continue

                y2, x2, y1, x1 = bbox[:4]

                x1 = int(x1 * _input_w * scale_x)
                y1 = int(y1 * _input_h * scale_y)
                x2 = int(x2 * _input_w * scale_x)
                y2 = int(y2 * _input_h * scale_y)

                #clamp to frame bounds
                x1 = max(0, min(x1, orig_w))
                y1 = max(0, min(y1, orig_h))
                x2 = max(0, min(x2, orig_w))
                y2 = max(0, min(y2, orig_h))

                friendly_name = name_mapping.get(class_name, class_name)

                world_state[friendly_name] = {
                    "bbox": [x1, y1, x2, y2],
                    "confidence": round(confidence, 2)

                }

                detections.append((friendly_name, confidence))

                #draw the frame
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2. putText(frame, f"{friendly_name} {confidence:.2f}", (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    return frame, world_state, detections           












    