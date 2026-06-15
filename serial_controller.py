import json
import time
import threading
from config import serial_port, serial_baud, serial_command
from kinematics import desk_to_motor_functions

try:
    import serial
    serial_avaliable = True
except ImportError:
    serial_avaliable = False

class SerialController:
    """
    Translates ORION action JSON into RP2040 commands

    Full command set:

    TENDON SERVOS (3x MG996R):
    {"cmd": "tendon", "cable": 0, "angle": 90}
    {"cmd": "tendon", "cable": 1, "angle": 45}
    {"cmd": "tendon", "cable": 2, "angle": 135}

    LAZY SUSAN (1x MG996R):
    {"cmd": "rotate", "angle": 90}

    CLAW (4x MG90S):
    {"cmd": "claw", "state": "open"}
    {"cmd": "claw", "state": "close", "force" : 0.5}

    SENSORS (4x FSR402)
    {"cmd" : "fsr", "finger": 0} ==> returns {"fsr": 0, "value": 412}

    EMERGENCY STOP:
    {"cmd": "estop"}

    STOW (hardcoded safe position):
    {"cmd": "stow"}

    """
    def __init__(self, port = serial_port, baud = serial_baud, command = serial_command):
        self.port = port
        self.baud = baud
        self.command = command
        self.conn = None
        self.connected = False
        self._lock = threading.Lock()

        if not self.command:
            self._connect()
        else:
            print("[SERIAL] command mode active")

    def _connect(self):
        if not serial_avaliable:
            self.command = True
            return
        
        try:
            self.conn = serial.Serial(self.port, self.baud, timeout = 1)
            time.sleep(2)
            self.connected = True
        except Exception as e:
            print(f"[SERIAL] Failed: {e}. Switching to command")
            self.command = True

    def send(self, cmd_dict): #sends encoded json files from orion to the hardware
        msg = json.dumps(cmd_dict) + "\n" #if this doesnt work change to \r

        if self.command:
            print(f"[SERIAL COMMAND]: {msg.strip()}")
            return True
        
        if not self.connected:
            print("[SERIAL] Disconnected. Attempting reconnection")
            self._connect()
            if not self.connected:
                print("[SERIAL] Reconnect failed")
                return False
        
        try:
            with self._lock:
                self.conn.write(msg.encode())
                self.conn.flush()
            return True
        except Exception as e:
            print(f"[SERIAL] Error: {e}")
            return False
        
    def read_response(self, timeout = 2.0): #reads encoded json files from orion
        if self.command:
            return {"status" : "ok"}
        if not self.connected:
            return None
        try:
            start = time.time()
            while time.time() - start < timeout:
                if self.conn.in_waiting:
                    line = self.conn.readline().decode().strip()
                    return json.loads(line)
                time.sleep(0.05)
        except Exception as e:
            print(f"[SERIAL] Read Error: {e}")
        return None
    
    #__________Tendon control_____________

    def set_tendon(self, cable, angle):
        #pulls 1 tendon cable (0, 1 or 2)
        assert cable in (0, 1, 2), "cable must be 0, 1, or 2"
        assert 0 <= angle <= 180, "angle must be 0-180"
        return self.send({"cmd": "tendon", "cable" : cable, "angle": angle})
    
    def set_all_tendons(self, angles):
        #sets all 3 tendon cable angles
        assert len(angles) == 3
        for i, angle in enumerate(angles):
            self.set_tendon(i, angle)

    #__________Lazy susan_____________________

    def rotate(self, angle):
        #rotates lazy susan 0-180 degrees
        return self.send({"cmd": "rotate", "angle": angle})
    
    #__________claw____________________________

    def open_claw(self):
        return self.send({"cmd": "claw", "state": "open"})
    
    def close_claw(self, force):
        #closes claw with fsr feedback
        #stops each finger if fsr threshold is exceeded
        return self.send({"cmd": "claw", "state": "close", "force": force})
    
    #____________stow______________________________
   
    def stow(self):
        #folds arm up
        return self.send({"cmd" : "stow"})
   
    #_____________sequences_______________________

    def grab_sequence(self, desk_x, desk_y, force = 0.5):
        #Grab sequence steps:
        #1. stow arm
        #2. open claw
        #3. lower/extend the arm to the object
        #4. close the claw using the correct force using feedback from the fsr finger sensors

        cmds = desk_to_motor_functions(desk_x, desk_y)

        print(f"[SERIAL] Grab: tendons = {cmds['tendon_angles']}, lazy susan = {cmds['lazy_susan_angle']} force = {force}")
       
        #stow first
        self.stow()
        time.sleep(2)

        #rotate lazy susan
        self.rotate(cmds['lazy_susan_angle'])
        time.sleep(1)

        #open claw
        self.open_claw()
        
        #extend the spine
        self.set_all_tendons(cmds['tendon_angles'])
        time.sleep(1.5)

        #close claw
        self.close_claw(force)
        time.sleep(1)

        return True
    
    def drop_sequence(self):
        #drops object
        self.open_claw()
        time.sleep(1)
        self.stow()

    def estop(self):
        #emergency stop
        return self.send({"cmd": "estop"})

    def close(self):
        #close operations
        if self.conn and self.connected:
            self.conn.close()
            self.connected = False

#singleton
controller = SerialController()

def test_serial():
    print("Serial Controller Test\n")
    c = SerialController(command=True)

    print("1. Stow")
    c.stow()

    print("\n2. Set tendons: ")
    c.set_all_tendons([45, 90, 45])

    print("\n3. Close claw (gentle): ")
    c.close_claw(0.3)

    print("\n4. Full grab sequence: ")
    c.grab_sequence(
        desk_x = 20,
        desk_y = 20,
        force = 0.3,
    )
          
    print("\n5. Drop sequence: ")
    c.drop_sequence()

    print("\n6. Emergency stop:")
    c.estop()

    print("\n7. Close")
    c.close()
    
    print("\nAll tests passed")


if __name__ == "__main__":
    test_serial()
    


