# # combination of wakeword.py, transcirption.py and all of the other util files

from wakeword import listen_for_audio, beep
from transcription import transcribe
import time
import sounddevice as sd

record_duration = 5.0

silence = 1

def voice_command():

    try:
        while True:
            audio = listen_for_audio(record_seconds = 5.0)
            beep()
            
            if audio is None:
                continue
            
            time.sleep(0.3)

            print("What is your command: ")

            command = transcribe(audio)

            if command:
                print(f"Command: '{command}'")
                return command
            else:
                print("No command received")
    
    except KeyboardInterrupt:
        print("\nStopped")



def loop_run():

    print("Say wake word and then command. Ctrl+C to stop. \n")

    try:
        while True:
            audio = listen_for_audio(record_duration = 5.0)
            beep()

            time.sleep(0.3)

            if audio is None:
                continue

            print("Say your command: ")

            command = transcribe(audio)

            if command:
                print(command)
            else:
                print("Nothing stated")
    except KeyboardInterrupt:
        print("\nstopped")


if __name__ == "__main__":
    loop_run()

    
