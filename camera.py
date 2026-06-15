import cv2
from config import is_pi
if is_pi:
    from picamera2 import Picamera2, Preview

class CameraSystem:
    def __init__(self):
        self.overhead_cam = None
        self.base_cam = None
        self.claw_cam = None

        if is_pi:
            self._init_pi()
        else:
            self._init_mac()

    def _init_pi(self):
        """
        Pi 5 setup:
       -USB index 0 = overhead
       -USB index 1 = base camera
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
        
        #for usb (overhead and base cams)
        try:
            self.overhead_cam = cv2.VideoCapture(0)
            if self.overhead_cam.isOpened():
                print("Overhead USB camera started (index 0)")
            else:
                print("[CAMERA] Overhead USB failed:")
                self.overhead_cam = None
        except Exception as e:
            print(f"[CAMERA Overhead USB failed: {e}")

        try:
            self.base_cam = cv2.VideoCapture(1)
            if self.base_cam.isOpened():
                print("Base USB camera started (index 1)")
            else:
                print("[CAMERA] Base USB not found")
                self.base_cam = None
        except Exception as e:
            print(f"[CAMERA] Base USB failed")

    def _init_mac(self):
        """
        Mac/Dev setup:
        -Index 0 = overhead cam (laptop webcam)
        -Index 1 = base cam (external webcam)
        -Claw cam not simulated
         
        """
        self.overhead_cam = cv2.VideoCapture(0)
        if self.overhead_cam.isOpened():
            print("Dev overhead camera started (index 0)")
        else:
            print("[CAMERA] No camera at index 0")
            self.overhead_cam = None

        self.base_cam = cv2.VideoCapture(1)
        if self.base_cam.isOpened():
            print("Dev base camera started (index 1)")
        else:
            print("[CAMERA] No camera at index 1")
            self.base_cam = None

        self.claw_cam = None
        print("No claw cam in dev mode")

#_____________ Frame capture_________________

    def get_overhead_frame(self):
        if self.overhead_cam is None:
            return None
        ret, frame = self.overhead_cam.read()
        return frame if ret else None
    
    def get_base_frame(self):
        if self.base_cam is None:
            return None
        ret, frame = self.base_cam.read()
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
            "overhead": self.get_overhead_frame(),
            "base": self.get_base_frame(),
            "claw": self.get_claw_frame()
        }

    def release(self):
        if self.claw_cam:
            if is_pi:
                self.claw_cam.stop()
            else:
                self.claw_cam.release()

        if self.base_cam:
                self.base_cam.release()
        if self.overhead_cam:
                self.overhead_cam.release()
        print("All cameras released")

#testing

def test_cameras():

    print("Camera system test\n")

    cams = CameraSystem()
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






    


        
