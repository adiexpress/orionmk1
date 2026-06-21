import cv2
from config import is_pi

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
       -USB index 2 = claw camera
        
        """
        for attr, index, name in [
            ("overhead_cam", 0, "Overhead"),
            ("base_cam", 1, "Base"),
            ("claw_cam", 2, "Claw")
        ]:
            try:
                cam = cv2.VideoCapture(index)
                if cam.isOpened():
                    setattr(self, attr, cam)
                    print(f"{name} USB Camera started (index{index})")
                else:
                    print(f"[CAMERA] {name} USB not found")
                    setattr(self, attr, None)
            except Exception as e:
                print(f"[CAMERA] {name} USB failed: {e}")
                setattr(self, attr, None)
        

    def _init_mac(self):
        """
        Mac/Dev setup:
        -Index 0 = overhead cam (laptop webcam)
        -Index 1 = base cam (external webcam)
        -Index 2 = simulates claw (second external)
         
        """
        for attr, index, name in [
            ("overhead_cam", 0, "Overhead"),
            ("base_cam", 1, "Base"),
            ("claw_cam", 2, "Claw")
        ]:
            cam = cv2.VideoCapture(index)
            if cam.isOpened():
                setattr(self, attr, cam)
                print(f"{name} camera started at {index} index")
            else:
                setattr(self, attr, None)
                print(f"[CAMERA] {name} USB failed:")

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
        ret, frame = self.claw_cam.read()
        return frame if ret else None
 
        
    def get_all_frames(self):
        return {
            "overhead": self.get_overhead_frame(),
            "base": self.get_base_frame(),
            "claw": self.get_claw_frame()
        }

    def release(self):
        for cam in [self.overhead_cam, self.base_cam, self.claw_cam]:
            if cam:
                cam.release()
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






    


        
