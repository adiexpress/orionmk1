import numpy as np
import time
from openwakeword.model import Model
from microphone import get_mic_input, read_chunk, sample_rate 

owwcall = "alexa" #going to test it with jarvis first since ill have to train it on orion and itll take time

confidence_threshold = 0.2

cooldown = 2.0

print("Loading model...")

owwmodel = Model(wakeword_models = [owwcall], inference_framework="onnx") #using onnx since it runs on cpu and not gpu

print(f"Model loaded. Waiting for start call '{owwcall}'")

def beep(): #plays a quick beep to show that the model heard the name call
    import pyaudio

    beep_duration = 0.15
    beep_HZ = 900

    audio = pyaudio.PyAudio()
    stream = audio.open(format = pyaudio.paFloat32, channels = 1, rate = sample_rate, output = True)

    #sine wave for the beep essentially
    t = np.linspace(0, beep_duration, int(sample_rate*beep_duration))
    beep = (np.sin(2 * np.pi * beep_HZ * t) * 0.25).astype(np.float32)

    fade_samples = int(len(beep) * 0.2)
    beep[-fade_samples:] *= np.linspace(1, 0, fade_samples)

    stream.write(beep.tobytes())
    stream.stop_stream()
    stream.close()
    audio.terminate()


def listen_for_call(stream): #this is the main lsiten function that will call the model when someone says hey_jarvis
    
    last_trigger_time = 0

    while True:

        audio_chunk = read_chunk(stream)

        prediction = owwmodel.predict(audio_chunk)
        
        print(prediction)

        confscore = prediction.get('alexa', 0.0)

        if confscore > 0.05:
            print(f"Wake score: {confscore:.3f}", end="\r")

        now = time.time()
        if confscore >= confidence_threshold and (now-last_trigger_time) > cooldown:
            last_trigger_time = now
            print(f"\n Call detected. (Score: {confscore:.3f})")
            beep()
            return


#testing time :)

def test_model():

    stream, audio_interface = get_mic_input()

    try:
        for i in range(3):
            print(f"\nTest {i+1}/3 ")
            listen_for_call(stream)
            print(f"Trigger {i+1} confirmed")
            time.sleep(1)

        print("\nAll triggers confirmed")
    
    except KeyboardInterrupt: #if user presses ctrl+c it quits
        print("\n\nStopped")
    

    finally:
        stream.stop_stream()
        stream.close()
        audio_interface.terminate()


if __name__ == "__main__":
    test_model()








