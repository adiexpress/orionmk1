import sys
import time

try:
    import tensorflow.lite as tflite
    sys.modules['tflite_runtime'] = tflite
except ImportError:
    print("ERROR: run: pip install tensorflow")
    pass

import numpy as np
import sounddevice as sd
from openwakeword.model import Model
from microphone import sample_rate, chunk_size
import queue
import threading

chunk = chunk_size

confscore = 0.5

cooldown = 2.0

owwcall = "hey_jarvis" #going to test it with jarvis first since ill have to train it on orion and itll take time

print("Loading wake word model")

owwmodel = Model() # loaded all models for now, but will specify when out of testing phase

detected = False

last_trigger_time = 0

audio_queue = queue.Queue(maxsize=100)


def processing():

    #the ml work that was previously connected to the audio_callback but needed to be moved

    global detected, last_trigger_time

    while True:
        
        try:
            chunk = audio_queue.get(timeout=1.0)
            prediction = owwmodel.predict(chunk)
            confidence = prediction.get(owwcall, 0.0)

            if confidence > 0.2:
                print(f"Score[{owwcall}]: {confidence:.3f}", end= "\r")
            
            now = time.time()

            if confidence >= confscore and (now - last_trigger_time) > cooldown:
                last_trigger_time = now
                detected = True
                print(f"\nCall Detected: {owwcall} (Score: {confidence:.2f})")
            
            audio_queue.task_done()

        except queue.Empty:
            continue
        except Exception as e:
            print(f"[PROCESSING ERROR]: {e}")



def listen_for_audio(record_seconds = 5.0): #this is the main listen function that will call the model when someone says hey_jarvis
    global detected
    
    detected = False

    owwmodel.reset() #resets internal state so test runs dont bleed into each other sort of

    while not audio_queue.empty():
        try:
            audio_queue.get_nowait()
        except queue.Empty:
            break

    processing_thread = threading.Thread(target=processing, daemon=True)
    processing_thread.start()
    
    time.sleep(1)

    record_chunks = int((sample_rate * record_seconds) / chunk)

    print("Listening for call")

    stream = sd.InputStream(samplerate=sample_rate, channels = 1, dtype = 'float32', blocksize = chunk_size)
    stream.start()

    try:    
        while not detected:
            raw, _ = stream.read(chunk_size)
            chunk_int = (raw[:,0] * 32768).astype(np.int16)

            try:
                audio_queue.put_nowait(chunk_int)
            except queue.Full:
                pass
    
        beep()
        print("What is your command: ")

        record_chunks = int((sample_rate * record_seconds) / chunk_size)
        recorded = []

        for _ in range(record_chunks):
            raw, _ = stream.read(chunk_size)
            recorded.append(raw[:,0].astype(np.float32))
    finally:
        stream.stop()
        stream.close()

    if recorded:
        return np.concatenate(recorded)
    return None


def beep():
    duration = 0.15
    hz = 900
   
    
    t = np.linspace(0, duration, int(sample_rate * duration))
    b = (np.sin(2 * np.pi * hz * t) * 0.3).astype(np.float32) # sine wave for audio files, stole from previous code

    sd.play(b, samplerate=sample_rate)
    sd.wait()




def test_model():
    try:
        for i in range(3):
            print(f"\nTest{i+1}/3")
            audio = listen_for_audio()
            if audio is not None:
                print(f"Trigger{i+1} confirmed")
                beep()
            time.sleep(2)
        print("\nall triggers confirmed")
    
    except KeyboardInterrupt:
        print("\nStopped")

if __name__ == "__main__":
    test_model()







