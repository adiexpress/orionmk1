# #text to speech 
# #orion voice output system

# import pyttsx3

# engine = pyttsx3.init()

# #rate 
# engine.setProperty("rate", 160)

# #volume
# engine.setProperty("volume", 0.9)

# #voice property (how orion sounds)

# voices = engine.getProperty("voices")
# engine.setProperty("voice", voices[0].id)

# def speak(text):
#     #speaks a line of text
#     print(f"[ORION]: {text}")
#     engine.say(text)
#     engine.runAndWait()

# def test():
#     speak("shut up monkey")
#     speak("good evening master bruce")
#     speak("moving object")
#     speak("should I get the suit ready, mister stark?")



# if __name__ == "__main__":
#     test()
# text to speech 
# orion voice output system with Kokoro

import sounddevice as sd
from kokoro import KPipeline

# 1. Initialize Kokoro Pipeline ('a' for American English)
pipeline = KPipeline(lang_code='b')

# 2. Voice configuration (Kokoro does not use index numbers)
# Available male voices: 'am_adam', 'am_fenrir', 'am_michael', 'am_onyx'
# Available female voices: 'af_heart', 'af_bella', 'af_nicole', 'af_sarah'
ORION_VOICE = 'bm_daniel' 

def speak(text):
    # Speaks a line of text and prints with prefix
    print(f"[ORION]: {text}")
    
    # Generate audio chunks from the text
    generator = pipeline(text, voice=ORION_VOICE)
    
    for _, _, audio in generator:
        # Kokoro models output audio natively at 24000Hz (24kHz)
        sd.play(audio, samplerate=24000)
        sd.wait() # Wait for the current line to finish playing

def test():
    speak("good evening master bruce")
    # speak("moving object")
    # speak("should I get the suit ready, mister stark?")

if __name__ == "__main__":
    test()
