import numpy as np #numpy must be first
import sounddevice as sd
import queue
import sys

sample_rate = 16000
chunk_size = 1280
channels = 1

audio_queue = queue.Queue()


def audio_callback(indata, frames, time_info, status):
    if status:
        print(status, file = sys.stderr)
    
    int16_data = (indata.copy() * 32768.0).astype(np.int16)
    audio_queue.put(int16_data.flatten())

audio = sd.InputStream(samplerate = sample_rate, channels = channels, dtype = 'float32', blocksize = chunk_size)
audio.start()

def get_mic_input():
    print("Mic inputs: ")
    print(f"Using mic input: {sd.query_devices(kind='input')['name']}")
    print(f"Mic ready at {sample_rate} HZ")

def read_chunk():

    data, overflow = audio.read(chunk_size)
    
    return data.squeeze()

def record_audio(duration = 10.0, silence_duration = 1.0):
    
    needed_chunks = int((sample_rate * duration) / chunk_size)
    silence_chunks = int((sample_rate * silence_duration) / chunk_size)
    min_chunks = int((sample_rate * 1.5) / chunk_size)
    
    chunks = []
    silent_count = 0

    print("Recording until you stop talking")

    for _ in range(needed_chunks):
        chunk = read_chunk()
        chunks.append(chunk)

        volume = np.max(np.abs(chunk)) 

        if volume < 0.04: #silent threshold, change depending on mic sensitivity
            silent_count += 1
        else:
            silent_count = 0 #resets silent count
    
        if silent_count >= silence_chunks and len(chunks) > min_chunks:
            print("User silence detected, stopped recording")
            break 

    print("Recording finished")
    return np.concatenate(chunks)









