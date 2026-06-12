import json
import time
import threading
from config import serial_port, serial_baud, serial_command

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
    {"cmd": "tof"} ==> returns {"tof_left": 120, "tof_right" : 145}

    RAIL (NEMA17 + TMC2209)
    {"cmd": "rail", "steps": 400, "direction": "left", "speed": 800}
    {"cmd": "rail_home"} #sends railway to home position

    EMERGENCY STOP:
    {"cmd": "estop"}

    STOW (hardcoded safe position):
    {"cmd": "stow}

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
        if not self.command:
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
        #needs to happen before rail movement
        return self.send({"cmd" : "stow"})
   
    #_____________rail___________________________

    def rail_home(self):
        #returns rail to the endstop and set as zero
        return self.send({"cmd": "rail_home"})
    
    def move_rail(self, steps, direction, speed = 800):
        #moves rail
        #steps = number of microsteps (80 microsteps at 1mm at 1/16 microstepping)
        #speed is in microsteps per second (default is 800 which is 10 microsteps per second)

        #always stow before rail moves
        self.stow()
        time.sleep(2)

        tof = self.query_tof()
        if tof and (tof.get("tof_left", 999) < 80 or tof.get("tof_right", 999) < 80):
            print("[SERIAL] ToF obstacle detected - rail movement stopped")
            return False
        
        return self.send({"cmd":"rail", "steps": steps, "direction": direction, "speed": speed})
    
    def move_rail_mm(self, mm, direction, speed = 800):
        #move rail by millimeters (80 microsteps = 1mm)
        steps = int(mm * 80)
        return self.move_rail(steps, direction, speed)

    #______________sensors_____________________
    
    def query_fsr(self, finger = 0):
        #reads fsr value from one finger and returns a value from 0-1023
        self.send({"cmd": "fsr", "finger": finger})
        return self.read_response()
    
    def query_tof(self):
        #read both tof obstacle sensors and returns the distance between the obstacle and the arm in mm
        self.send({"cmd": "tof"})
        return self.read_response()
    
    #_____________sequences_______________________

    def grab_sequence(self, rail_mm, rail_direction, tendon_angle, force = 0.5):
        #Grab sequence steps:
        #1. stow arm
        #2. move rail
        #3. open claw
        #4. lower/extend the arm to the object
        #5. close the claw using the correct force using feedback from the fsr finger sensors

        print(f"[SERIAL] Grab: rail = {rail_mm}mm {rail_direction}, tendons = {tendon_angle}, force = {force}")
       
        #stow first
        self.stow()
        time.sleep(2)

        #move rail
        self.move_rail_mm(rail_mm, rail_direction)
        time.sleep(2)

        #open claw
        self.open_claw()
        
        #extend the spine
        self.set_all_tendons(tendon_angle)

        #close claw
        self.close_claw(force)
        time.sleep(1)

        return True
    
    def drop_sequence(self, location_rail_mm = None, location_rail_dir = None):
        #drops object, if user asks, moves to a location first

        if location_rail_mm and location_rail_dir:
            self.move_rail_mm(location_rail_mm, location_rail_dir)
            time.sleep(2.5)

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
controller = SerialController

def test_serial():
    print("Serial Controller Test\n")
    c = SerialController(command=True)

    print("1. Stow")
    c.stow()

    print("\n2. Rail home:")
    c.rail_home()

    print("\n3.Move rail 500mm left: ")
    c.move_rail_mm(500, "left")

    print("\n4. Set tendons: ")
    c.set_all_tendons([45, 90, 45])

    print("\n5. Close claw (gentle): ")
    c.close_claw(0.3)

    print("\n6. Full grab sequence: ")
    c.grab_sequence(
        rail_mm = 300,
        rail_direction = "left",
        tendon_angle = [60, 90, 60],
        force = 0.3

    )
          
    print("\n7. Drop sequence: ")
    c.drop_sequence(
        location_rail_mm = 400,
        location_rail_dir = "right"
    )

    print("\n8. Emergency stop:")
    c.estop()

    print("\n9. Close")
    c.close()
    
    print("\nAll tests passed")


if __name__ == "__main__":
    test_serial()
    


