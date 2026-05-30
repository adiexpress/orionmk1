import sys
import numpy as np
import time

try:
    import tflite_runtime
except ImportError:
    try:
        import tensorflow.lite as tflite
        sys.modules['tflite_runtime'] = tflite
    except ImportError:
        print("ERROR: run: pip install tensorflow")
        sys.exit(1)

import sounddevice as sd
from openwakeword.model import Model
from microphone import sample_rate

chunk = 1280
confscore = 0.5
cooldown = 2.0
owwcall = "hey_jarvis" #going to test it with jarvis first since ill have to train it on orion and itll take time

print("Loading wake word model")

owwmodel = Model() # loaded all models for now, but will specify when out of testing phase

detected = False
last_trigger_time = 0

def audio_callback(indata, frames, time_info, status):
    global detected, last_trigger_time

    if status:
        print(status)

    audio_frame = indata[:, 0] # flattens audio to 16 bit 

    prediction = owwmodel.predict(audio_frame)

    for model_name, confidence in prediction.items():
        if confidence > 0.1:
            print(f"Score[{owwcall}]: {confidence:.3f}", end="\r")
        
        now = time.time()

        if confidence >= confscore and (now - last_trigger_time) > cooldown:
            last_trigger_time = now
            detected = True
            print(f"\nCall Detected: {owwcall} (Score: {confidence:.3f})")


def listen_for_audio(stream=None): #this is the main lsiten function that will call the model when someone says hey_jarvis
    global detected
    detected = False

    with sd.InputStream(samplerate = sample_rate, channels = 1, dtype = 'int16', callback=audio_callback, blocksize = chunk):
        print("Listening for call")
        while not detected:
            sd.sleep(100)

def beep():
    import pyaudio
    duration = 0.15
    hz = 900
    audio=pyaudio.PyAudio()
    
    stream = audio.open(format = pyaudio.paFloat32, channels=1, rate=sample_rate, output = True)
    
    t = np.linspace(0, duration, int(sample_rate * duration))
    b = (np.sin(2 * np.pi * hz * t) * 0.25).astype (np.float32) # sine wave for audio files, stole from previous code

    fade = int(len(b) * 0.2)

    b[-fade:] *= np.linspace(1,0,fade)

    stream.write(b.tobytes())

    stream.stop_stream()

    stream.close()

    audio.terminate()


def test_model():
    try:
        for i in range(3):
            print(f"\nTest{i+1}/3")
            listen_for_audio()
            print(f"Trigger{i+1} confirmed")
            beep()
            time.sleep(1)
        print("\nall triggers confirmed")
    
    except KeyboardInterrupt:
        print("\nStopped")

if __name__ == "__main__":
    test_model()







