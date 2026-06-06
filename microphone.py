import numpy as np #numpy must be first
import sounddevice as sd

sample_rate = 16000
chunk_size = 1280
channels = 1

def get_mic_input():
    print("Mic inputs: ")
    print(f"Using mic input: {sd.query_devices(kind='input')['name']}")
    print(f"Mic ready at {sample_rate} HZ")

def read_chunk(stream = None):

    audio = sd.rec(chunk_size, samplerate=sample_rate, channels=channels, dtype = 'float32', blocking=True)

    return audio.flatten()

def record_audio(stream = None, duration = 10.0, silence_duration = 1.0):
    needed_chunks = int((sample_rate * duration) / chunk_size)
    silence_chunks = int((sample_rate * silence_duration) / chunk_size)
    
    chunks = []
    silent_count = 0

    print("Recording until you stop talking")

    for x in range(needed_chunks):
        chunk = read_chunk()
        chunks.append(chunk)

        volume = np.max(np.abs(chunk))

        if volume < 0.05: #silent threshold, change depending on mic sensitivity
            silent_count += 1
        else:
            silent_count = 0 #resets silent count
    
        if silent_count >= silence_chunks and len(chunks) > silence_chunks:
            print("User silence detected, stopped recording")
            break 

    print("Recording finished")
    return np.concatenate(chunks)









