Hello All who come to this project

This is the beginnings of Project O.R.I.O.N, which stands for Object Retrieval and Intelligent Operating Network

ORION is a ceiling-mounted robot arm system designed to assist at a workstation. Inspired by Doctor Octopus from Spider-Man, it features a flexible tendon-driven tentacle spine arm with a 3-jaw gripper, a wide-angle AI camera, local voice recognition, and object detection — all running fully offline on a Raspberry Pi 5 with a Raspberry Pi AI HAT+ (Hailo-8 NPU, 26 TOPS).

The arm mounts under kitchen cabinets above a multi-monitor desk on a 78-inch MGN12H linear rail. The rail sits centered in the 10-inch deep cabinet cavity. The hub is a wide shallow tray (Pi and HAT side by side) keeping hub height under 1.7 inches, leaving 5.8 inches of clearance above the monitors. It detaches via a quick-release plate and runs standalone on a camera tripod from an Anker power bank.

The spine is cable-tendon driven — 3 Dyneema UHMWPE cables (65-80lb, ~0.4mm) run through PTFE-lined channels in 9 triangular PETG segments, pulled by 3 MG996R base servos for full 3D motion. Each segment is an equilateral triangle (70mm sides, 35mm body) with M4 RC rod-end ball joints alternating 90 degrees per segment. Total reach: ~19.5 inches

This project is driven on a few AI Models: Whisper, by OpenAI for the language transcription when a user asks a question, YOLOV8 by Ultralytics for the object tracking and detection, and OpenWakeWord which is the key tool behind the "Hey ORION" activation call. 
