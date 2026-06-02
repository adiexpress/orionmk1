# # combination of wakeword.py, transcirption.py and all of the other util files

from wakeword import listen_for_audio, beep
from transcription import transcribe
from microphone import get_mic_input, record_audio

record_duration = 5.0

def voice_command():

    stream, audio_interface = get_mic_input()

    try:
        while True:
            listen_for_audio()
            beep()

            print("What is your command: ")

            audio = record_audio(stream, record_duration)

            command = transcribe(audio)

            if command:
                print(f"Command: '{command}'")
                return command
            else:
                print("No command received")
    finally:
        stream.stop_stream()
        stream.close()
        audio_interface.terminate()



def loop_run():
    stream, audio_interface = get_mic_input()

    print("Say wake word and then command. Ctrl+C to stop. \n")

    try:
        while True:
            listen_for_audio()
            beep()

            print("Say your command: ")

            audio = record_audio(stream, record_duration)

            command = transcribe(audio)

            if command:
                print(command)
            else:
                print("Nothing stated")
    except KeyboardInterrupt:
        print("\nstopped")
    finally:
        stream.stop_stream()
        stream.close()
        audio_interface.terminate()

if __name__ == "__main__":
    loop_run()

    
