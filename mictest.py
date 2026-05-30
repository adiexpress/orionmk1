# mictest.py
import pyaudio
import numpy as np

audio = pyaudio.PyAudio()
stream = audio.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=1280)

print("Listening")

for _ in range(100):
    data = stream.read(1280, exception_on_overflow=False)
    samples = np.frombuffer(data, dtype=np.int16)
    volume = np.abs(samples).mean()
    print(f"Volume: {volume:.1f}", end="\r")

stream.stop_stream()
stream.close()
audio.terminate()
print("\nDone.")