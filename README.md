Hello All who come to this project

This is the beginnings of Project O.R.I.O.N, which stands for Object Retrieval and Intelligent Operating Network

<img width="1244" height="830" alt="Group 1-3" src="https://github.com/user-attachments/assets/39eb01a0-8b20-4a39-95c1-0288d550b705" />

ORION is a ceiling-mounted robot arm system designed to assist at a workstation. Inspired by Doctor Octopus from Spider-Man, it features a flexible tendon-driven tentacle spine arm with a 3-jaw gripper, 3 wide-angle AI cameras linked together, local voice recognition, and object detection — all running fully offline on a Raspberry Pi 5 with a Raspberry Pi AI HAT+ (Hailo-8 NPU, 26 TOPS).

 The hub is a wide shallow tray (Pi and HAT side by side) keeping hub height under 1.7 inches, leaving 5.8 inches of clearance above the monitors. It detaches via a quick-release plate and runs standalone on a camera tripod from an Anker power bank.

The spine is cable-tendon driven — 3 Dyneema UHMWPE cables (65-80lb, ~0.4mm) run through PTFE-lined channels in 9 triangular PETG segments, pulled by 3 MG996R base servos for full 3D motion. Each segment is an equilateral triangle (70mm sides, 35mm body) with M4 RC rod-end ball joints alternating 90 degrees per segment. Total reach: ~19.5 inches

The sensors that are used in this project are the FSR402 pressure sensors on the tips of the fingers of the claw

This project is driven on a few AI Models: Whisper, by OpenAI for the language transcription when a user asks a question, YOLOV8 by Ultralytics for the object tracking and detection, OpenWakeWord which is the key tool behind the "Hey ORION" activation call, and LLaVA Phi 3 for the live object description in the webcam whenever a user uses the "describe" action

Orion runs on Qwen 2.5 3B parameters version by Alibaba and essentially it is the framework for all the reasoning and computing done by the model. 

The camera system runs on 3 USB 2.0 Cameras (1080P 130 degree rotation) to help with object tracking/detection and also obstacle avoidance.
After initial calibration where the cameras are trained on distict marked locations so that they can make their distance measurements, the tri-camera system uses triangulation to gather measurements from each of the 3 FOV ranges that it has. Using this, the ORION arm has almost 360 degree FOV. 

We created this project to help future engineers, like my teammate and I, strive in the workplace when no one else is there to help. Personally, I have been there many times. When it feels like the project that I am building needs 3 hands. Now, ORION is that 3rd hand.<br>
ORION acts like a personal desktop assistant that can physically help you with tasks like holding up objects, putting unnecessary tools
away, or even holding up a flashlight for those dark corners you can never see into. ORION is more than just an average robotic arm, however. It can even act as a friend. With its built-in AI voice-chat feature, you can have conversations about whatever weird things you like and it can answer the most redundant of questions.

## DISCLAIMER
Due to hardware deficiency, the custom "Hey ORION" wake word has not been trained yet. The system currently uses "Hey Jarvis" (a pre-trained OpenWakeWord model). Once hardware arrives, a custom model will be trained using OpenWakeWord's training pipeline and swapped in with a single config change.
<br>
## How the pipeline works:

1. Orion starts up and greets the user
2. Orion asks the user for the wake word (in this case it will be "Hey Jarvis")
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

## AI Pipelines


| Layer | Model | Hardware it Runs On |
|---|---|---|
| Wake word | OpenWakeWord (hey_jarvis) | Pi 5 CPU |
| Transcription | Whisper tiny.en | Pi 5 CPU |
| Command parsing | Qwen2.5-coder 3B | Pi 5 CPU via Ollama |
| Object detection | YOLOv8n | Hailo-8 NPU (26 TOPS) |
| Visual Q&A | LLaVA-phi3 | Pi 5 CPU via Ollama |

---

### Requirements
if you haven't already: download Python (coding language used for this project<br>
<br>
(download using the link below and following the steps)<br>
'https://www.python.org/downloads/'<br>

install all python libraries and utils needed to run ORION<br>
<br>
(run this command in the Terminal CLI)<br>
'pip install -r requirements.txt'<br>

### Pull AI Models
first, install the ollama desktop app<br>
<br>
(download using the link below and following the steps)<br>
'https://ollama.com/download'<br>

after downloading:<br>
pull both AI models from ollama<br>
<br>
(run these commands in the Terminal CLI)<br>
'ollama pull qwen2.5:3b-instruct'<br>
'ollama pull llava-phi3'<br>

### Calibrate Cameras
calibrate each of the 3 camera angles (base, overhead, claw) used for this project<br>
<br>
point each camera at a flat surface with 4 known real world coordinates<br>
<br>
(run these commands in the Terminal CLI)<br>
'python calibration.py overhead'<br>
'python calibration.py base'<br>
'python calibration.py claw'<br>
<br>
then, click the 4 points in this order: top-left, top-right, bottom-left, bottom-right and press 'S' to save them<br>

### Flash Pico Firmware
1. hold BOOTSEL button on Pico while plugging into USB - mounts as a RPI-RP2 drive<br>
2. download MicroPython.uf2 from 'https://micropython.org/download/RPI_PICO/'<br>
3. drag .uf2 onto the RPI-RP2 drive -> Pico will reboot with MicroPython<br>
4. download Thonny IDE from 'https://thonny.org'<br>
5. open Thonny -> Tools -> Options -> Interpreter -> MicroPython (Raspberry Pi Pico)<br>
6. open firmware.py -> File -> Save As -> Raspberry Pi Pico -> save as 'main.py'<br>
<br>
Pico runs firmware automatically on every boot up now<br>
No compliation needed since MicroPython is interpreted<br>
No external dependencies: all libraries used are MicroPython built-ins<br>

### Add named locations (Optional)
run locations.py and input the name of the location + its coordinates to save it to ORION's memory<br>
<br>
(run this command in the Terminal CLI)<br>
'python locations.py'

### Run ORION
run orion_brain.py and let the magic begin<br>
<br>
(run this command in Terminal CLI)<br>
'python orion_brain.py<br>
<br>
*NOTE: this file carries alot of weight, running it may be slow, so please have some patience.*

## How to use ORION

**Basic Workflow**

## USE THESE ONLY AFTER RUNNING ALL SETUP STEPS ABOVE

1. Say **'Hey Jarvis'** - ORION wakes up and beeps
2. Say your command - if you stop talking, the 'silence detection feature' will cut you off, so make sure you have an exact command
3. ORION will then transcribe, parse, detect, and act out your command if its necessary

**Avaliable Commands:**
"grab the ____" --> ORION will find your object via camera, extend its arm and pick it up<br>
<br>
"put it in the bin" ---> ORION will move its held object into the saved position named "bin" by the user<br>
<br>
"drop it" ---> ORION will drop whatever it is holding in its current location<br>
<br>
"stow the arm" ---> ORION will fold its arm to a predetermined safe resting position<br>
<br>
"what do you see" ---> Describes its surroundings using the claw camera with LLaVA vision AI<br>
<br>
"where is my ____?" ---> returns coordinates of the named object<br>
<br>
"how do magnets work?" ---> this is just a random question, you can ask ORION things like this, and it will respond like a normal AI agent<br>
<br>
**ORION understands natural language** - for the commands above, you can phrase them in almost any way you like<br>
<br>
For commands/questions ORION does not understand, it will use the CLARIFY command, where ORION will ask the user to clarify where the misconception was made<br>
<br>
## Hardware Setup

For the shafts, please cut them according to the necessary length as you cut, as plastic expansion might change how long your shaft cuts should be.

### When 3D printing:
For ease of printing, all objects are formated as follows: "Object name xNumber of times needed." For example: "Camera Mount x2" means you must print the camera mount twice.
All objects are in PLA filament, with the exception of the parts "Claw TPU Finger," which are in TPU, and "Claw PETG Tip," which are in PETG. 
Print settings are recommended to be 15-20% infill with supports enabled and gyroid infill.

### Requirements
* All 3D printed objects 
* Drill
* CA glue and activator
* Screwdriver for m2, m3, and m4 screws
* All parts and materials dictated by the BOM
* Clippers

### Assembly overveiw
We will progress through creating ORION in the following order

1. Electronics Hub
2. Servo Hub
3. Arm
4. Claw
5. Full Assembly

Unless specified, assume the count is one per part when looking at what 3D parts to grab for a section

### Electronics Hub Assembly

Grab the Following 3D parts:
* Electronics Hub Parts 1-4
* Rectangular E-Hub Connector (2)
* Angular E-Hub Connector (2)
* Circular E-Hub Connector
* PCA9685 Mount
* Base Camera Mount
* Camera mount
* Pi Stack Mount
* Pi Stack Spacer (4)
* DC Buck Mount
* Pico Mount Top
* Pico Mount Bottom
* Power Bank Mount
* Power Bank Cover

Put together the Electronics Hub Parts (1-4) Like in the photo below. Keep in mind the holes to help you align each part with each other

<img width="1101" height="970" alt="image" src="https://github.com/user-attachments/assets/0d23a65d-fc03-471c-bac6-46cad14b2e15" />

Take the Circular E-Hub Connector and place it in the circular insert. Drill small holes with a small drill bit in each corner of the circle (One hole per Hub part, the hole should go through the hub part). Then put a small screw through the drilled holes (M4 or M3 both work). That circle should hold the four parts together somewhat.

Next, Take both Rectangular Connectors and use the same method to connect the Hub parts on the insert that looks like this (There should be a total of 2, on opposite sides of one another): 

<img width="1847" height="699" alt="image" src="https://github.com/user-attachments/assets/4421c6cf-08df-4230-b978-e5716d159f95" />

Next, repeat with the Angular Connectors on the inserts that look like this (Again, total of two, on opposite sides of one another):

<img width="1619" height="663" alt="image" src="https://github.com/user-attachments/assets/31d1df41-ecef-4765-9868-8b9315df7feb" />

After that, we will move on to assembling our electronics.

Take your Pi 5, AI PI 5 HAT, Respeaker, 40 pin extended stacking header, Pi stack mount, and the mounting hardware that comes with the AI HAT+ . 

Attach the extended stacking header onto the pins for the Pi 5. Take an M3 screw, and stick it through the bottom of the stack mount and through the pi %, screwing it into the 4 Pi stack Spacers. Here is what it should look like:

<img width="1715" height="811" alt="image" src="https://github.com/user-attachments/assets/697e5d9d-2146-4f82-887a-aea9cbe829df" />

Attach the AI Pi HAT+ and use M3 screws to attach it to the spacers like so:

<img width="1875" height="968" alt="image" src="https://github.com/user-attachments/assets/6aed939c-9b09-403e-bd95-392857b67861" />

Attach the respeaker on top of that to make it look like this:

<img width="1789" height="809" alt="image" src="https://github.com/user-attachments/assets/fef8f4cc-3c6d-4606-a865-5ff25274c2db" />

After that, place the pico inside its case like so:

<img width="1783" height="883" alt="image" src="https://github.com/user-attachments/assets/4a175894-bb97-4f9c-976c-01be30e9d6bc" />

The PCA9685 like so:

<img width="1508" height="961" alt="image" src="https://github.com/user-attachments/assets/b78229f3-3532-49fa-b263-7f1fd58fabdf" />

The Buck convertor like so:

<img width="1412" height="971" alt="image" src="https://github.com/user-attachments/assets/e941f01e-5e4e-440c-a7b6-b42ec0b7d4c9" />

and The Camera like so:

<img width="794" height="650" alt="image" src="https://github.com/user-attachments/assets/1d434c26-fa03-42d8-9fbd-8299a622cd5b" />

After that, please wire all of your electronic components (excluding the speaker, the servos, the other 2 cameras, and the FSR sensors) like so:

<img width="1568" height="873" alt="image" src="https://github.com/user-attachments/assets/de8422b9-2637-463b-a961-41d879c3d164" />

Please use jumber cables, USBA, USBC, And USB Pigtails as necessary. If you need more assistance, please take a look at an unofficial version below:

<img width="1484" height="964" alt="image" src="https://github.com/user-attachments/assets/2a9fa2cf-79d0-468a-bbde-acbfa0167896" />

Attach that entire system like so, making sure to use either M3 or M4 screws and their assorted heatset insert:

<img width="1536" height="1147" alt="image" src="https://github.com/user-attachments/assets/7cff9cc3-a344-41ad-96c4-af69b93ced07" />

Please attach the Power Bank Mount like so:

<img width="1367" height="523" alt="image" src="https://github.com/user-attachments/assets/8e8de0ab-9bd0-4a12-8fb1-81c0534dc5f0" />

And once you place the power bank inside place the cover like so, making sure to use heatset inserts:

<img width="1425" height="509" alt="image" src="https://github.com/user-attachments/assets/7dc9244e-046a-402f-bccf-ea95b38395e2" />

you can add the speaker into the slot using CA glue and the camera right above that in the premade holes:

<img width="1209" height="1010" alt="image" src="https://github.com/user-attachments/assets/aff8ecc2-64f3-4f32-a5b5-993b0f0a6fd4" />

Finally, use zipties and the cable tie holders to organize your wires. Please use CA glue and activator to attach the cable tie holders.

### Servo Hub Assembly:

Once you are confident your electircal wiring is correct, gather the following:

* Electronic Hub Top A-D
* E-Hub Rectangular Connector (2)
* Gear to Servo Mount
* Rotator A (3)
* Servo winch (3)
* Servo Hub Sides A-C
* Servo Hub Side Connector (6)
* Servo Hub Top
* Winch Pulley (6)
* Small Gear
* Susan Gear
* Overhead Camera Mount

Assemble the Electornic Hub Tops (A-D) and Overhead Camera Mount like so (with heatset inserts): 

<img width="1101" height="892" alt="image" src="https://github.com/user-attachments/assets/b822a3ef-52b6-4c19-819a-56fd1cb0be94" />

Use E-Hub E-Hub Rectangular Connectors in the same method as before, like so:

<img width="1219" height="859" alt="image" src="https://github.com/user-attachments/assets/56af0f21-6bdf-46e6-8293-a593b7033f90" />

Attach all of that onto the Electronics Hub (With heatset inserts):

<img width="1041" height="981" alt="image" src="https://github.com/user-attachments/assets/1532f7dd-bfcc-432c-b9be-1385f4051ab8" />

Attach the packaged long servo horns and the 3D pritned Rotator A's to an MG90S servo, and clip off the excess from the servo horn till you have 3 MG90S servos that look like this:

<img width="925" height="628" alt="image" src="https://github.com/user-attachments/assets/bfab4030-ce38-4460-817e-49a112641c7b" />

Then, take an MG996R servo at attach it here, using headset inserts:

<img width="1356" height="475" alt="image" src="https://github.com/user-attachments/assets/cb4bec73-d0a2-4f16-9de1-ee4911281dde" />

Then attach the small gear to that servo using the Gear to Servo mount.

Using spacers and screws, attach the outer ring of the lazy susan to the assembly like so:

<img width="1189" height="1133" alt="image" src="https://github.com/user-attachments/assets/22c6a20f-bab0-4ec7-b665-b44402dd1540" />

Attach the Susan gear atop that:

<img width="1330" height="1049" alt="image" src="https://github.com/user-attachments/assets/9b3d3d64-5439-4d6d-84bb-3bd9b06a186a" />

Attach Servo Hub sides A-C using the 6 servo side connectors like before, 3 MG996R servos, 3 winch pulleys, and three Servo Winches to construct this (use heatset inserts and attach the servos before attaching the siding):

<img width="1700" height="957" alt="image" src="https://github.com/user-attachments/assets/c6f0a71f-a87a-4001-a4e2-1dd415d762a8" />

Attach the bottom:

<img width="1496" height="993" alt="image" src="https://github.com/user-attachments/assets/f9414a4e-65c3-4c1d-8fa6-7554768be8a2" />

screw that into the susan gear

<img width="1422" height="1086" alt="image" src="https://github.com/user-attachments/assets/459fff5b-34bb-4f54-a111-3982d07d8e47" />

Attach the servo hub Top to make it look like so:

<img width="1269" height="1143" alt="image" src="https://github.com/user-attachments/assets/d1d30040-e141-4201-87ae-7090a8121e71" />

Finally, attach the MG90S servos from before like so:

<img width="1429" height="938" alt="image" src="https://github.com/user-attachments/assets/66147b23-3249-49a2-8e68-35fd56a0c66c" />

### Arm Assembly

Grab the following 3D printed parts:

* Middle Segment (6)
* Outer Pin Stopper (14)
* Pin to Rod end Spacer (14)
* Rod End Spacer (7)
* Servo Hub Cap

To stat off, take a rod end, a 3mm shaft, and two pin to rod end spacers and assemble them like so:

<img width="733" height="685" alt="image" src="https://github.com/user-attachments/assets/f9dbaca9-99b3-436c-8106-5546d20e3330" />

Take the Outer Pin Stopper and put it on the outsides to stop the pin from sliding out (screw or CA glue)

Attach the servo Hub Cap to have this:

<img width="1601" height="1167" alt="image" src="https://github.com/user-attachments/assets/57a99395-0e1d-4664-85a9-d30ff0934989" />

Momentarialy put that to the side and grab your Middle segments. Take your Rod End spacer and attach it here:

<img width="1324" height="977" alt="image" src="https://github.com/user-attachments/assets/3eeaddb2-a879-4a8e-ae16-27cc1d4e97ac" />

put a rod end beneath it and screw the rod end spacer into that, with the bottom of the middle segment in between. Repeat for every middle segment.
Now take the pins, the outer pin stoppers, and the Pin to Rod end Spacers to take the rod end from the bottom of one middle segment at attach it to the top of another. However, you will notice there are two sets of holes, so make sure to alternate which set you put the pin through.

You will have a set of connected segments looking like this:

<img width="352" height="1058" alt="image" src="https://github.com/user-attachments/assets/f1fcab20-6cf7-4b9e-9f27-0a5cb86bdaab" />

Take two sets of Dyneema tubing and thread it through two sets of PTFE tubing. Repeat 3 times and put one set through each of the three outer holes of every mid segment.

### Claw Assembly

You will need your remaining 3D printed parts

Take your 5mm shafts and slide it through the holes of the Main Fairlead body. screw in the Fairlead Pin holders like so:

<img width="1287" height="898" alt="image" src="https://github.com/user-attachments/assets/2e691760-14be-4888-b9e5-1dd21deebc12" />

Repeat until you have 9 of these.

Add one Camera here:

<img width="1595" height="1040" alt="image" src="https://github.com/user-attachments/assets/504a1115-1dd6-402d-9610-5757ecabeb00" />

and the Claw Camera Holder on top of it:

<img width="1210" height="1003" alt="image" src="https://github.com/user-attachments/assets/7b7426ac-005a-485f-9df3-f7a2a78e5c53" />

Attach the 3 spring holders like so:

<img width="1262" height="1064" alt="image" src="https://github.com/user-attachments/assets/94344b7b-7cc0-444c-81c4-df40a99d195e" />

slide a 5mm shaft through each of these holes:

<img width="1336" height="534" alt="image" src="https://github.com/user-attachments/assets/4b8d0a22-6ea8-4c4a-9ff1-4d451a6e7adb" />

Attach 3 fairleads like so:

<img width="1180" height="1134" alt="image" src="https://github.com/user-attachments/assets/0b6e7371-75dc-40af-972f-31dec3fa21a0" />

Assemble the Claw by inserting 4 (two on each side) TPU connector pins into the Claw TPU finger, using CA glue to attach them to the Claw Finger A part and the Claw PETG part, like so:

<img width="969" height="983" alt="image" src="https://github.com/user-attachments/assets/0af6c289-7bed-4d9a-94cd-bbf8845ddf20" />

Repeat 3 times

Undo the 5mm shaft from before and slide the claw fingers through like so:

<img width="1429" height="975" alt="image" src="https://github.com/user-attachments/assets/98a847fe-c9e9-477c-b796-c0a22351c840" />

and cover each side with the Claw pin stoppers, using CA glue or screws to attach:

<img width="813" height="582" alt="image" src="https://github.com/user-attachments/assets/e42eecf1-ab2f-4d97-b693-2d77364e3fc4" />

Attach 3 fairleads on the bottom like this:
<img width="1700" height="1051" alt="image" src="https://github.com/user-attachments/assets/3cd6c8ba-2ca8-4442-a727-2ecb3c9c5598" />

On each claw, drill a wider hole through the small pre-printed one and pass the FSR sensor wiring through that. Then attach the fsr sensors and the FSR wire holder (with screws) like so:

<img width="826" height="968" alt="image" src="https://github.com/user-attachments/assets/87a5fb53-20cb-449f-9046-ea83cb24ba07" />

Attach claw base A with heatset inserts and screws like so:

<img width="1456" height="813" alt="image" src="https://github.com/user-attachments/assets/43f9d4fb-bbc3-43f5-a46f-996dad774155" />

Attach remaining fairleads like so:

<img width="1593" height="942" alt="image" src="https://github.com/user-attachments/assets/d5d2c233-9c45-4334-8e11-e17b7ad68d91" />

Then Attach claw base B like so, making sure to put a Rod End Spacer through its center and attach a rod end before screwing it into the claw system with heatset inserts.

<img width="854" height="1016" alt="image" src="https://github.com/user-attachments/assets/ce237db5-87cc-4074-b1c3-2b4fe1189ede" />

Take one set of the ptfe tubing and attach it to the claw finger where the hole is made, and take the other set and tie a knot to once they both go through all the middle segments. At the bottom, connect the tubing from the fingers and connect it to the winch on the MG90S servo and take the other three and connect it to the MG996R servo winches (through the center hole of the servo hub) This is the tensioning that will control the arm.

Once you attach that to the rest of the parts (from the last segment of the arm, using the same technique with the spacers to attach the rod end bearing as before), you can run the wires from the FSR sensors down into the E-Hub and make sure your wiring matches this diagram, using cable tie mounts as needed.
<img width="1567" height="880" alt="image" src="https://github.com/user-attachments/assets/7d83656e-8657-4869-96ca-78d6bcf3d311" />

or the unofficial one if that is what you prefer, as it is simpler.

<img width="1634" height="1117" alt="image" src="https://github.com/user-attachments/assets/5fab2617-4836-4d3a-bb01-e7156eb2f9ea" />

Finally, you will have a finished ORION:

<img width="787" height="1002" alt="image" src="https://github.com/user-attachments/assets/95ccf0ee-234b-4085-adc0-694523dc218a" />


## BOM:


* FSR Sensor
* Steel Extension
* Plastic Rod-Ends
* MG90S
* Fishing Line (65 LBS @ 300 YDS
* USB Cameras
* Buck/Voltage Resistor
* 65W Power Bank
* PWM Servo Driver
* Raspberry Pi Pico (RP2040 Microcontroller)
* Female-Female Jumper Wires
* 1-3 Connector
* 1-2 Connector
* External Speaker
* Raspberry Pi Pico Headers
* Raspberry Pi 5 Headers
* Lazy Susan
* AI HAT+ with Hailo-8 NPU
* External Mic for Pi
* Raspberry Pi 5
* M2, M3, M4 Screws
* M2, M3, M4 Screw Heat-set inserts
* Screw spacers
* Cable-tie mounts
* PTFE Tubing
* 10K Ohm Resistors
* USB-A to USB-A Cable
* USB-C to USB-C Cable
* USB-A Male to 2-Pin Pigtail exposed cable
* CA glue and activator
* 5mm Shafts
* 3mm Shafts
* PLA Filament
* TPU Filament
* PETG Filament

[BoM - Sheet1.csv](https://github.com/user-attachments/files/29170802/BoM.-.Sheet1.csv)


