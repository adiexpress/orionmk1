Hello All who come to this project

This is the beginnings of Project O.R.I.O.N, which stands for Object Retrieval and Intelligent Operating Network

ORION is a ceiling-mounted robot arm system designed to assist at a workstation. Inspired by Doctor Octopus from Spider-Man, it features a flexible tendon-driven tentacle spine arm with a 3-jaw gripper, 3 wide-angle AI cameras linked together, local voice recognition, and object detection — all running fully offline on a Raspberry Pi 5 with a Raspberry Pi AI HAT+ (Hailo-8 NPU, 26 TOPS).

 The hub is a wide shallow tray (Pi and HAT side by side) keeping hub height under 1.7 inches, leaving 5.8 inches of clearance above the monitors. It detaches via a quick-release plate and runs standalone on a camera tripod from an Anker power bank.

The spine is cable-tendon driven — 3 Dyneema UHMWPE cables (65-80lb, ~0.4mm) run through PTFE-lined channels in 9 triangular PETG segments, pulled by 3 MG996R base servos for full 3D motion. Each segment is an equilateral triangle (70mm sides, 35mm body) with M4 RC rod-end ball joints alternating 90 degrees per segment. Total reach: ~19.5 inches

The sensors that are used in this project are the FSR402 pressure sensors on the tips of the fingers of the claw


This project is driven on a few AI Models: Whisper, by OpenAI for the language transcription when a user asks a question, YOLOV8 by Ultralytics for the object tracking and detection, OpenWakeWord which is the key tool behind the "Hey ORION" activation call, and LLaVA Phi 3 for the live object description in the webcam whenever a user uses the "describe" action

Orion runs on Qwen 2.5 3B parameters version by Alibaba and essentially it is the framework for all the reasoning and computing done by the model. 

The camera system runs on 2 USB 2.0 Cameras (U20-Cam 720P's) and 1 CSI Camera Module (IMX219) to help with object tracking/detection and also obstacle avoidance.
After initial calibration where the cameras are trained on distict marked locations so that they can make their distance measurements, the tri-camera system uses triangulation to gather measurements from each of the 3 FOV ranges that it has. Using this, the ORION arm has almost 360 degree FOV. 

##How the pipeline works:

1. Orion starts up and greets the user
2. Orion asks the user for the wake word (in this case it will be "Hey Orion")
3. The user either speaks the wake word or waits until they require the assistance of Orion
4. After receiving the wake word, Orion then asks the user for a command from which they have a few preset options to choose from:
   - grab: grabs an object that must be specified by the user
   - move to: moves an object that must be specified by the user to a location
   - drop: drops the object the arm is holding in the position it is currently at
   - stow: puts the arm away into "sleep mode"
   - describe: describes the object that is in the webcam's POV
   - clarify: Orion uses this command when further clarification is necessary regarding the request
     (Ex. User says "bring me that thingy over there", Orion says "What "thingy" are you referring to?)
   - chat: A chat feature used when the user just wants a buddy to talk to or to ask general questions
   - where is: gives the location/coordinates of an object that must be specified by the user
5. User requests which ever command they require in their work and Orion parses it and fulfills the command

## Setup

### Requirements
if you haven't already: download Python (coding language used for this project
(download using the link below and following the steps)
'https://www.python.org/downloads/'

install all python libraries and utils needed to run ORION
(run this command in the Terminal CLI)
'pip install -r requirements.txt'

### Pull AI Models
first, install the ollama desktop app
(download using the link below and following the steps)
'https://ollama.com/download'

after downloading:
pull both AI models from ollama
(run these commands in the Terminal CLI)
'ollama pull qwen2.5:3b-instruct'
'ollama pull llava-phi3'

### Calibrate Cameras
calibrate each of the 3 camera angles (base, overhead, claw) used for this project
(run these commands in the Terminal CLI)
'python calibration.py overhead'
'python calibration.py base'
'python calibration.py claw'

### Flash Pico Firmware
move the firmware from the code compiler to the actual hardware
Option 1: copy firmware.py to RP2040 using Thonny IDE ('https://thonny.org')
Option 2: use mpremote  (run this in CLI: 'mpremote connect /dev/ttyACM0 cp firmware.py :main.py')

### Add named locations (Optional)
run locations.py and input the name of the location + its coordinates to save it to ORION's memory
(run this command in the Terminal CLI)
'python locations.py'

### Run ORION
run orion_brain.py and let the magic begin
(run this command in Terminal CLI)
'python orion_brain.py
*NOTE: this file carries alot of weight, running it may be slow, so please have some patience.*




