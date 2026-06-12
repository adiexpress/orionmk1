import cv2
from config import is_pi
import platform
if is_pi:
    from picamera2 import Picamera2, Preview

class CameraSystem:
    def __init__(self):
        self.right_cam = None
        self.left_cam = None
        self.claw_cam = None

        if is_pi:
            self._init_pi()
        else:
            self._init_mac()

    def _init_pi(self):
        """
        Pi 5 setup:
       -USB index 0 = left end camera
       -USB index 1 = right end camera
       -CAM0 CSI = claw camera
        
        """
        #for csi claw cam on the claw
        try:
            self.claw_cam = Picamera2(camera_num = 0)
            config = self.claw_cam.create_preview_configuration(
                main = {"size": (640, 480), "format": "RGB888"} #must be rgb for hailo8
            )
            self.claw_cam.configure(config)
            self.claw_cam.start()
            print("Claw CSI camera started (CAMO)")
        except Exception as e:
            print(f"[CAMERA] Claw CSI failed: {e}")
        
        #for usb (left and right rail cams)
        try:
            self.left_cam = cv2.VideoCapture(0)
            if self.left_cam.isOpened():
                print("Left rail USB camera started (index 0)")
            else:
                print("[CAMERA] Left USB failed:")
                self.left_cam = None
        except Exception as e:
            print(f"[CAMERA Left USB failed")

        try:
            self.right_cam = cv2.VideoCapture(1)
            if self.right_cam.isOpened():
                print("Right rail USB camera started (index 1)")
            else:
                print("[CAMERA] Left rail USB not found")
                self.right_cam = None
        except Exception as e:
            print(f"[CAMERA] Left USB failed")

    def _init_mac(self):
        """
        Mac/Dev setup:
        -Index 0 = left camera (laptop webcam)
        -Index 1 = right camera (external webcam)
        -Claw cam not simulated
         
        """
        self.left_cam = cv2.VideoCapture(0)
        if self.left_cam.isOpened():
            print("Dev left camera started (index 0)")
        else:
            print("[CAMERA] No camera at index 0")
            self.left_cam = None

        self.right_cam = cv2.VideoCapture(1)
        if self.right_cam.isOpened():
            print("Dev right camera started (index 1)")
        else:
            print("[CAMERA] No camera at index 0")

        self.claw_cam = None
        print("No claw cam in dev mode")

#_____________ Frame capture_________________

    def get_left_frame(self):
        if self.left_cam is None:
            return None
        ret, frame = self.left_cam.read()
        return frame if ret else None
    
    def get_right_frame(self):
        if self.right_cam is None:
            return None
        ret, frame = self.right_cam.read()
        return frame if ret else None
    
    def get_claw_frame(self):
        if self.claw_cam is None:
            return None
        if is_pi:
            try:
                return self.claw_cam.capture_array()
            except Exception:
                return None
        else:
            ret, frame = self.claw_cam.read()
            return frame if ret else None
        
    def get_all_frames(self):
        return {
            "left": self.get_left_frame(),
            "right": self.get_right_frame(),
            "claw": self.get_claw_frame()
        }

    def release(self):
        if is_pi:
            if self.claw_cam:
                self.claw_cam.stop()
            else:
                self.claw_cam.release()

        if self.right_cam:
                self.right_cam.release()
        if self.left_cam:
                self.left_cam.release()
        print("All cameras released")

#testing

def test_cameras():

    print("Camera system test\n")

    cams = CameraSystem
    frames = cams.get_all_frames()

    for name, frame in frames.items():
        if frame is not None:
            print(f"{name}: {frame.shape}")
            cv2.imwrite(f"test_{name}.jpg", frame)
            print(f"    Saved test_{name}.jpg")
        else:
            print(f"{name}: no frame")
    
    cams.release()
    print("\nTested all cams")


if __name__ == "__main__":
    test_cameras()






    


        
