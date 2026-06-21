#firmware Orion
#runs on raspberry pi rp2040
#sends json commands from pi 5 at 115200 baud
#rp2040 controls all servos via PCA9685
#reads fsr sensors through ADC pins

 # Full command set:

    # TENDON SERVOS (3x MG996R):
    # {"cmd": "tendon", "cable": 0, "angle": 90} --------> moves one tendon servo

    # LAZY SUSAN (1x MG996R):
    # {"cmd": "rotate", "angle": 90}. ------> rotates lazy susan

    # CLAW (4x MG90S):
    # {"cmd": "claw", "state": "open"} --------> opens all claw fingers
    # {"cmd": "claw", "state": "close", "force" : 0.5} ----------> close fingers with fsr sensors

    # SENSORS (4x FSR402)
    # {"cmd" : "fsr", "finger": 0} ==> returns {"fsr": 0, "value": 412} -----> reads 1 fsr sensor

    # EMERGENCY STOP:
    # {"cmd": "estop"} -----> stops all movement immediately

    # STOW (hardcoded safe position):
    # {"cmd": "stow"} ----------> go to safe stow position for the arm

    #PING
    # {"cmd": "ping"} ----------> returns {ORION ready, status: ok}

#PCA Channel MAP
#ch0 = MG996R tendon cable servo 0
#ch1 = MG996R tendon cable servo 1
#ch2 = MG996R tendon cable servo 2
#ch3 = MG996R lazy susan servo
#ch4 = MG90S claw finger servo 0
#ch5 = MG90S claw finger servo 1
#ch6 = MG90S claw finger servo 2

#RP2040 GPIO MAP
#GP4/GP5 - I2C0 SDA/SCL -> PCA9695
#gp26 = ADC0 -> FSR finger sensor 0
#gp27 = ADC1 -> FSR finger 1
#gp28 = ADC2 -> FSR finger 2
#usb = serial to pi 5

import sys
from Code.machine import Pin, I2C, ADC
import time
import json
import select


#PCA9685 I2C
PCA9685_ADDR = 0x40
I2C_SDA_PIN = 4 #gp4
I2C_SCL_PIN = 5 #gp5
I2C_FREQ = 400_000

#PCA9685 registers
PCA9685_MODE1 = 0x00
PCA9685_MODE2 = 0x01
PCA9685_LED0_ON_L = 0x06
PCA9685_PRESCALE = 0xFE

#Servo PWM
SERVO_MIN_US = 600 #0.6ms conservative minimum, safe for both mg90s and mg996r
SERVO_MAX_US = 2400 #2.4ms conservative max
#servo 90 deg = 1500 microseconds 
SERVO_FREQ_HZ = 50 
COUNTS_PER_US = 4096 / 20_000 #0.2048 counts per microsecond at 50hz

#ADC
FSR_ADC_PINS = [26, 27, 28] #gp26 = finger0, gp27 = finger1, gp28=finger2
ADC_MAX = 65535

#FSR
#forces 0-1.0 maps to adc values
FSR_MIN_THRESHOLD = 5000 #5000 = very light touch (0.25V)
FSR_MAX_THRESHOLD = 45000 #45000 = firm hard grip (2.27V)

#stow position
STOW_TENDON_ANGLES = [119, 52, 52]
STOW_CLAW_ANGLE = 180 # fully open
STOW_SUSAN_ANGLE = 90 #neutral

#claw closing parameters
CLAW_STEP_DEG = 2 #more precise the smaller it is
CLAW_STEP_DELAY_MS = 20
CLAW_TIMEOUT_S = 3.0 #hard timeout for if an fsr sensor doesnt trigger (in seconds)


#PCA9685 DRIVER

class PCA9685:
    #drives all 7 servos via I2C at 0x40
    #prescale = 121 -> 50.03 HZ (0.03HZ error which is negligable for servos)

    def __init__(self, i2c, addr=PCA9685_ADDR):
        self.i2c = i2c
        self.addr = addr
        self._init()
    
    def _write(self, address, val):
        self.i2c.writeto_mem(self.addr, address, bytes([val])) #could be bytearray change if using hashmap

    def _read(self, reg):
        return self.i2c.readfrom_mem(self.addr, reg, 1)[0]
    
    def _init(self):
        self._write(PCA9685_MODE1, 0x00)
        time.sleep_ms(10)

        #prescale -> round(25,000,000 / (4096 * frequnecy)) - 1
        #prescale at 50HZ round(25,000,000 / 204800 ) - 1 = 121
        prescale = round(25_000_000 / (4096 * SERVO_FREQ_HZ)) - 1
        prescale = max(3, min(255, prescale))

        mode1 = self._read(PCA9685_MODE1)
        self._write(PCA9685_MODE1, (mode1 & 0x7F) | 0x10) #sleep to change prescale
        self._write(PCA9685_PRESCALE, prescale) # change prescale
        self._write(PCA9685_MODE1, mode1)   #wake up
        time.sleep_ms(5)
        self._write(PCA9685_MODE1, mode1 | 0xA1) #autoincrement
        self._write(PCA9685_MODE2, 0x04) #totem pole output
        print(f"[PCA9685] Init OK - prescale = {prescale} (~{SERVO_FREQ_HZ}Hz)")

    def set_pwm(self, channel, on, off):
        #write raw on/off counts to one channel. on/off are 0-4095
        reg = PCA9685_LED0_ON_L + 4 * channel
        self.i2c.writeto_mem(
            self.addr, reg, bytes([on & 0xFF, on >> 8, off & 0xFF, off >> 8])
        )

    def set_servo_angle(self, channel, angle_deg):
        #set servo angle from 0-180
        #0 = 600, 90 = 1500, 180 = 2400
        angle_deg = max(0, min(180, int(angle_deg)))
        pulse_us = SERVO_MIN_US + (angle_deg / 180) * (SERVO_MAX_US - SERVO_MIN_US)
        off = int(pulse_us * COUNTS_PER_US)
        self.set_pwm(channel, 0, off)

    def all_off(self):
        #kill all pwm on each of the 16 channels (used for estop)
        for channels in range(16):
            self.set_pwm(channels, 0, 0) #servos will go limp

    #FSR sensors
class FSRSensors:
    #no touch = v-out becomes close to 0 volts
    #hard press = v out is close to v in
    #more force applied = higher ADC value
    #voltage divider - 3.3V -> FSR -> ADC pin -> 10k resistor -> GND

    def __init__(self):
        self.adcs = [ADC(Pin(pin)) for pin in FSR_ADC_PINS] #inits pins as ADC
        print(f"[FSR] Init Good - GP{FSR_ADC_PINS[0]}/GP{FSR_ADC_PINS[1]}/GP{FSR_ADC_PINS[2]}")

    def read(self, finger):
        #for each finger, read the raw ADC value (return 0-65535)
        if not 0 <= finger < len(self.adcs):
            return 0
        return self.adcs[finger].read_u16()
    
    def force_exceeded(self, finger, threshold):
        #return true if fsr reading is beyond threshold
        adc_threshold = int(FSR_MIN_THRESHOLD + threshold * (FSR_MAX_THRESHOLD - FSR_MIN_THRESHOLD))
        return self.read(finger) >= adc_threshold
    
 #servo controller
class ServoController:
    #servo control
    #tracks current position of all 7 servos
    #manages claw FSr feedback loop

    def __init__(self, pca, fsr):
        self.pca = pca
        self.fsr = fsr
        self.estop_flag = False #stow safety check

        #current position
        self.tendon_angles = [90, 90, 90]
        self.susan_angle = 90
        self.claw_angles = [180, 180, 180]

        self.stow()
        print(f"[SERVO] Stow complete")

        #tendons
    def set_tendon(self, cable, angle):
        #sets servo for 1 tendon
        if self.estop_flag:
            return
        angle = max(0, min(180, int(angle)))
        self.pca.set_servo_angle(cable, angle)
        self.tendon_angles[cable] = angle

    def set_all_tendons(self, angles):
        #sets servo for all tendons (same for all)
        for i, angle in enumerate(angles):
            self.set_tendon(i, angle)
    
    #lazy susan
    def rotate_susan(self, angle):
        #rotates servo for lazy susan
        if self.estop_flag:
            return
        angle = max(0, min(180, int(angle)))
        self.pca.set_servo_angle(3, angle)
        self.susan_angle = angle

    #claw
    def open_claw(self):
        #opens all 3 fingers fully
        if self.estop_flag:
            return
        for finger in range(3):
            self.pca.set_servo_angle(4 + finger, 180)
            self.claw_angles[finger] = 180
        print("[CLAW] Opened")

    def close_claw(self, force=0.5):
        #close all 3 fingers with per-finger fsr feedback
        #each finger stops independently when its own FSR threshold is hit
        #Hard timeout after claw timeout regardless

        #timing: 90 steps * 20ms = 1.8s max (which is within 3.0s timeout)

        if self.estop_flag:
            return
        
        force = max(0.0, min(1.0, float(force)))
        finger_complete = [False, False, False]
        current_angles = [180, 180, 180]
        start_time = time.time()
        print(f"[CLAW] Closing.. Force = {force}")

        while not all(finger_complete):
            if time.time() - start_time > CLAW_TIMEOUT_S:
                print("[CLAW] Timeout")
                break
        
            if self.estop_flag:
                break

            for finger in range(3):
                if finger_complete[finger]:
                    continue

                if self.fsr.force_exceeded(finger, force):
                    finger_complete[finger] = True
                    print(f"[CLAW] Finger {finger} FSR threshold reached")
                    continue

                new_angle = current_angles[finger] - CLAW_STEP_DEG
                if new_angle < 0:
                    finger_complete[finger] = True
                    continue

                self.pca.set_servo_angle(4 + finger, new_angle)
                current_angles[finger] = new_angle
                self.claw_angles[finger] = new_angle

            time.sleep_ms(CLAW_STEP_DELAY_MS)
        
        print(f"[CLAW] Final: {current_angles}")

    #stow
    def stow(self):
        #move to safe stow position
        #Order: open claw, center susan, fold tendons
        #has priority over estop, but clears estop flag first
        #total time is 1.1s (fits within Pi 2second connect delay)

        self.estop_flag = False #stow always works, even after estop

        print("[SERVO] Stowing..")

        #open claw (never stow while gripping an object)
        for finger in range(3):
            self.pca.set_servo_angle(4 + finger, STOW_CLAW_ANGLE)
        self.claw_angles = [STOW_CLAW_ANGLE] * 3
        time.sleep_ms(500)

        #center susan
        self.pca.set_servo_angle(3, STOW_SUSAN_ANGLE)
        self.susan_angle = STOW_SUSAN_ANGLE
        time.sleep_ms(300)

        #fold tendons (sleep is in loop to stagger for smoother movement)
        for i, angle in enumerate(STOW_TENDON_ANGLES):
            self.pca.set_servo_angle(i, angle)
            self.tendon_angles[i] = angle
            time.sleep_ms(100)

        print(f"[SERVO] Stowed - tendons = {STOW_TENDON_ANGLES} susan = {STOW_SUSAN_ANGLE}")

    #estop
    def emergency_stop(self):
        #cut all PWM channels so servos go limp
        #!!!(send stow command to recover)

        self.estop_flag = True
        self.pca.all_off()
        print("[SERVO] ESTOP - all channels off")

    #command handler
def handle_command(cmd_dict, servos, fsr):
        #Excecutes the parsed cmd dict
        #returns response to pi
        #No None return - all paths return something

        cmd = cmd_dict.get("cmd", "")

        if cmd == "ping":
            return {"status": "ok", "msg": "ORION firmware ready"}

        elif cmd == "tendon":
            cable = cmd_dict.get("cable")
            angle = cmd_dict.get("angle")
            if cable is None or angle is None:
                return {"status" : "error", "msg": "missing angle"}
            if not 0 <= int(angle) <= 180:
                return {"status" : "error", "msg": "angle must be between 0-180"}
            if not cable in (0, 1, 2):
                return {"status" : "error", "msg": "cable must be 0, 1, 2"}
            servos.set_tendon(int(cable), int(angle))
            return {"status": "ok", "angle": angle}
        
        elif cmd == "rotate":
            angle = cmd_dict.get("angle")
            if angle is None:
                return {"status" : "error", "msg": "missing angle"}
            if not 0 <= int(angle) <= 180:
                return {"status": "error", "msg": "angle must be between 0-180"}
            servos.rotate_susan(int(angle))
            return {"status" : "ok", "angle": angle}
        
        elif cmd == "claw":
            state = cmd_dict.get("state")
            if state == "open":
                servos.open_claw()
                return {"status" : "ok", "state" : "open"}
            elif state == "close":
                force = float(cmd_dict.get("force", 0.5))
                force = max(0.0, min(1.0, force))
                return {"status": "ok", "state": "closed", "force" : force}
            else:
                return {"status": "error", "msg": f"unknown claw state: {state}"}
            
        elif cmd == "fsr":
            finger = cmd_dict.get("finger", 0)
            if int(finger) not in (0, 1, 2):
                return {"status": "error", "msg": "finger must be 0, 1, or 2"}
            value = fsr.read(int(finger))
            return {"fsr" : finger, "value": value}
        
        elif cmd == "stow":
            servos.stow()
            return {"status": "ok", "msg": "stowed"}
        
        elif cmd == "estop":
            servos.emergency_stop()
            return {"status": "ok", "msg": "emergency stop activated"}
        
        else:
            return {"status": "error", "msg": f"unknown command: {cmd}"}
            
def send_response(response_dict):
        #send json response to pi over USB serial
        sys.stdout.write(json.dumps(response_dict) + "\n")

    #main
def main():
    print("ORION RP2040 Firmware")

    #init I2C
    i2c = I2C(0, sda = Pin(I2C_SDA_PIN), scl = Pin(I2C_SCL_PIN), freq = I2C_FREQ)

    #verify PCA9685 on bus
    devices = i2c.scan()
    print(f"[I2C] Found: {[hex(d) for d in devices]}")

    if PCA9685_ADDR not in devices:
        print(f"[ERROR] PCA9685 not found at {hex(PCA9685_ADDR)}")
        print("[ERROR] Check: SDA=GP4 SCL=GP5 VCC=3.3V GND=GND")
        while True:
            send_response({
                "status": "error",
                "msg": "PCA9685 not found - I2C wiring"
            })
            time.sleep(2)
    
    #init hardware
    pca = PCA9685(i2c)
    fsr = FSRSensors()
    servos = ServoController(pca, fsr)

    #pi serial_controller handshake ready
    print("[ORION] Ready")
    send_response({"status": "ok", "msg": "ORION firmware ready"})

    #setup serial poll
    poll = select.poll()
    poll.register(sys.stdin, select.POLLIN)
    
    #command loop
    buffer = ""

    while True:
        try:
            events = poll.poll(10)
            if not events:
                continue

            char = sys.stdin.read(1)
            if not char:
                continue

            if char in ("\n", "\r"):
                line = buffer.strip()
                buffer = ""

                if not line:
                    continue

                #parse JSON
                try:
                    cmd_dict = json.loads(line)
                except ValueError as e:
                    send_response({"status": "error", "msg": f"invalid JSON: {e}"})
                    continue

                #execute and respond
                try:
                    response = handle_command(cmd_dict, servos, fsr)
                    send_response(response)
                except Exception as e:
                    print(f"[ERROR] {e}")
                    send_response({"status": "error", "msg": str(e)})

            else:
                buffer += char
                #guard against runaway input
                if len(buffer) > 256:
                    print("[ERROR] Buffer overflow - clearing")
                    buffer = ""
            
        except KeyboardInterrupt:
            print("[ORION] Stopping - stowing arm")
            servos.stow()
            break

        except Exception as e:
            print(f"[LOOP ERROR] {e}")
            time.sleep_ms(100)
            #never crash the loop

if __name__ == "__main__":
    main()







                 



     






    








