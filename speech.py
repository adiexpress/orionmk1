
import numpy as np #numpy must be first
import sounddevice as sd
from kokoro import KPipeline
import threading
import queue
import time
import soundfile as sf
import os
import subprocess

os.environ["HF_HUB_OFFLINE"] = "1"

# 1. Initialize Kokoro Pipeline
pipeline = KPipeline(lang_code='b')
ORION_VOICE = 'bm_george' 

# 2. Main Thread Queue for Mac-safe playback
mac_audio_queue = queue.Queue()

playback_lock = threading.Lock()

def _play_audio_file(file_path):
    """Runs inside a thread to play the audio file using Mac's native system."""
    with playback_lock:
        try:
            # afplay is macOS's built-in, thread-safe command line audio player
            subprocess.run(["afplay", file_path], check=True)
        except Exception as e:
            print(f"[PLAYBACK ERROR] {e}")
        finally:
            # Clean up the file after it finishes playing
            if os.path.exists(file_path):
                os.remove(file_path)

def _generation_worker(text):
    """Generates audio in the background."""
    try:
        generator = pipeline(text, voice=ORION_VOICE)
        for _, _, audio in generator:
            if audio is not None and len(audio) > 0:
                mac_audio_queue.put(audio)
    except Exception as e:
        print(f"Kokoro generation error: {e}")

def speak(text):
    """
    Generates and plays audio completely safely on macOS.
    Does not crash Python because playback is handled by the OS.
    """
    print(f"[ORION]: {text}")
    
    try:
        generator = pipeline(text, voice=ORION_VOICE)
        for i, (_, _, audio) in enumerate(generator):
            if audio is not None and len(audio) > 0:
                # Create a unique temporary file path for this chunk
                file_path = f"orion_temp_{threading.get_ident()}_{i}.wav"
                
                # Save the numpy array as a standard WAV file (Kokoro is 24000Hz)
                sf.write(file_path, audio, 24000)
                
                # Hand it over to a safe background thread to play via afplay
                threading.Thread(target=_play_audio_file, args=(file_path,), daemon=True).start()
                
    except Exception as e:
        print(f"[KOKORO ERROR] {e}")


def process_audio():
    """Checks the queue and plays any waiting audio on the main thread."""
    try:
        # Check if audio is ready without locking up the program
        audio_to_play = mac_audio_queue.get_nowait()
        sd.play(audio_to_play, samplerate=16000)
        sd.wait() 
        mac_audio_queue.task_done()
    except queue.Empty:
        pass


def test():
    # 1. Trigger the speech (Non-blocking!)
    speak("good evening sir") #nice it works
    print("Systems operational.")
    
    process_audio()

if __name__ == "__main__":
    test()


