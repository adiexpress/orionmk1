from faster_whisper import WhisperModel
import numpy as np

whisper_size = "base" #using actual hardware ill use tiny, but using base for testing currently

language = "en" #english only model (may support other languages at anothet time)

print(f"Loading Model: {whisper_size}")

whisper_model = WhisperModel(whisper_size, device = "cpu", compute_type = "int8") #use cuda for device type if nvidia gpu 

print("Whisper Model Loaded")



def transcribe(audio_array):
    segments, info = whisper_model.transcribe(audio_array, language = language, beam_size = 3, vad_filter = True, vad_parameters = {"min_silence_duration_ms" : 300,} )

    full_text = "".join(segment.text for segment in segments)
    full_text = full_text.strip().lower()

    return full_text

#testing

def test_transcription():
    
    from microphone import get_mic_input, record_audio

    stream, audio_interface = get_mic_input()

    try:
        print("\nTranscription test started")

        for i in range(3):
            input(f"\nTest{i+1}/3. Press Enter to speak")
            audio = record_audio(stream,duration=5)

            result = transcribe(audio)

            if result:
                print(f"Transcribed audio: '{result}'")
            else:
                print("Nothing transcribed")
    finally:
        stream.stop_stream()
        stream.close()
        audio_interface.terminate()



if __name__ == "__main__":
    test_transcription()
