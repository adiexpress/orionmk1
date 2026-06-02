import pyaudio as pya
import numpy as np

sample_rate = 16000
chunk_size = 1280

channels = 1
format = pya.paInt16 #16 bit audio samps

def get_mic_input(): #gets microphone input
    audio = pya.PyAudio()

    print("mic inputs: ") # prints avaliable microphone input options so user makes sure they choose the correct one
    for i in range(audio.get_device_count()):
        device = audio.get_device_info_by_index(i)
        if device["maxInputChannels"] > 0:
            print(f"[{i}] {device['name']}")
    

    stream = audio.open(format=format, channels = channels, rate = sample_rate, input = True, frames_per_buffer = chunk_size)

    print(f"\n Mic opened at {sample_rate}HZ, {chunk_size} frames")
    
    return stream, audio

def read_chunk(stream):
    raw = stream.read(chunk_size, exception_on_overflow=False)#exception on overflow basically keeps the audio from crashing 

    audio_np = np.frombuffer(raw, dtype=np.int16).copy()

    return audio_np

def record_audio(stream, duration, silence_duration):
    
    needed_chunks = int((sample_rate * duration) / chunk_size)
    silence_chunks = int((sample_rate * silence_duration) / chunk_size)
    chunks = []
    silent_count = 0

    print("Recording until you stop talking")

    for x in range(needed_chunks):
        chunk = read_chunk(stream)
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

