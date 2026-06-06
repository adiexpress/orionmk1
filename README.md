Hello All who come to this project

This is the beginnings of Project O.R.I.O.N, which stands for Object Retrieval and Intelligent Operating Network

ORION is a ceiling-mounted robot arm system designed to assist at a workstation. Inspired by Doctor Octopus from Spider-Man, it features a flexible tendon-driven tentacle spine arm with a 3-jaw gripper, a wide-angle AI camera, local voice recognition, and object detection — all running fully offline on a Raspberry Pi 5 with a Raspberry Pi AI HAT+ (Hailo-8 NPU, 26 TOPS).

The arm mounts under kitchen cabinets above a multi-monitor desk on a 78-inch MGN12H linear rail. The rail sits centered in the 10-inch deep cabinet cavity. The hub is a wide shallow tray (Pi and HAT side by side) keeping hub height under 1.7 inches, leaving 5.8 inches of clearance above the monitors. It detaches via a quick-release plate and runs standalone on a camera tripod from an Anker power bank.

The spine is cable-tendon driven — 3 Dyneema UHMWPE cables (65-80lb, ~0.4mm) run through PTFE-lined channels in 9 triangular PETG segments, pulled by 3 MG996R base servos for full 3D motion. Each segment is an equilateral triangle (70mm sides, 35mm body) with M4 RC rod-end ball joints alternating 90 degrees per segment. Total reach: ~19.5 inches

This project is driven on a few AI Models: Whisper, by OpenAI for the language transcription when a user asks a question, YOLOV8 by Ultralytics for the object tracking and detection, and OpenWakeWord which is the key tool behind the "Hey ORION" activation call. 

Orion runs on Mistral (7b parameters version) by Mistral AI essentially is the framework for all the reasoning and computing done by the model. 

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

