#detects platform automatically
#central config for ORION

import platform

#platform detection (PI or macOS)
is_pi = platform.machine() in ("aarch64" , "armv7l")
is_mac = platform.system() == "Darwin"

#camera
use_picamera = is_pi

#ai models used
whisper_model = "tiny.en" if is_pi else "base"
ollama_model = "qwen2.5:3b-instruct"
ollama_url = "http://localhost:11434/api/generate"

#parser options
parser_options = {
            "temperature": 0.2, #changes temp to make it less sporadic (test 0.2 or 0.3)
            "top_p": 0.5,
            "num_predict": 100,
            "stop": ["\n\n", "---", "Voice command"]
}

#audio
SAMPLE_RATE = 16000
CHUNK_SIZE = 1280
CHANNELS = 1
SILENCE_THRESHOLD = 0.03
SILENCE_DURATION = 1.5
MAX_RECORD_DURATION = 10.0

#wake word stuff
wake_word = "hey_orion" if is_pi else "hey_jarvis"
wake_word_confidence = 0.5
wake_word_cooldown = 2.0

#usb serial port stuff
serial_port = "/dev/ttyACM0" if is_pi else None
serial_baud = 115200
serial_command = not is_pi #if on mac, print command, if on pi, send command

#hardware geometry
base_height = 76.2 #3inches in mm
pole_height = 304.8 #12 inches in mm (where camera will hang)
camera_height = pole_height + base_height #roughly 15 inches above the desk


#camera detection
detection_confidence = 0.5
priority_objects = {"person", "cell phone", "cup", "keyboard", "mouse", "book", "laptop"} #making a list of priority objects that it detects so it doesnt waste time on other stuff

name_mapping = {"person" : "person",
    "cell phone": "phone", #name mapping 
                "cup": "cup",
                "keyboard": "keyboard",
                "mouse": "mouse",
                "book": "book",
                "laptop": "laptop",
                }

#jsons
locations_file = "locations.json"

#multiprocessing
start_method = "fork" if is_pi else "spawn"