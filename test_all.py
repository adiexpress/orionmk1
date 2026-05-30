import sys
import numpy as np

# 1. Mac-specific TensorFlow Lite patch
try:
    import tflite_runtime
    print("✅ Found native tflite_runtime.")
except ImportError:
    try:
        import tensorflow.lite as tflite
        sys.modules['tflite_runtime'] = tflite
        print("✅ Apple Silicon Patch: Redirected tflite_runtime to full TensorFlow.")
    except ImportError:
        print("❌ ERROR: Neither 'tflite-runtime' nor 'tensorflow' is installed.")
        print("Please run: pip install tensorflow")
        sys.exit(1)

# 2. Import audio and wake word libraries
try:
    import sounddevice as sd
    import openwakeword
    from openwakeword.model import Model
except ImportError as e:
    print(f"❌ ERROR: Missing required libraries. {e}")
    print("Please run: pip install sounddevice openwakeword numpy")
    sys.exit(1)

# 3. Initialize the wake word engine
print("\n🔄 Loading pre-trained openWakeWord models (this may take a few seconds)...")
try:
    # This automatically loads default models like "alexa", "hey_mycroft", etc.
    oww_model = Model()
    print(f"✅ Models loaded successfully: {list(oww_model.models.keys())}")
except Exception as e:
    print(f"❌ Failed to initialize openWakeWord: {e}")
    sys.exit(1)

# 4. Audio Configuration (openWakeWord requires exactly 16000Hz, Mono, 16-bit)
RATE = 16000
CHANNELS = 1
CHUNK = 1280  # openWakeWord processes audio in chunks of 1280 samples

print("\n🎤 Testing audio input devices...")
print(f"Default Input Device: {sd.query_devices(kind='input')['name']}")
print("Starting stream... Speak into your microphone!")
print("-" * 60)

def audio_callback(indata, frames, time, status):
    if status:
        print(f"⚠️ Audio Status Warning: {status}", flush=True)
    
    # Flatten the 2D array to 1D for openWakeWord
    audio_frame = indata[:, 0]
    
    # Visual audio level indicator (prints dots if mic hears sound)
    volume_norm = np.linalg.norm(audio_frame) / np.sqrt(len(audio_frame))
    if volume_norm > 100:  # Adjust this threshold if it's too sensitive/blind
        print(".", end="", flush=True)
        
    # Feed audio chunk into openWakeWord
    prediction = oww_model.predict(audio_frame)
    
    # Check if any wake word confidence is higher than 0.5
    for model_name, confidence in prediction.items():
        if confidence > 0.5:
            print(f"\n\n✨ WAKE WORD DETECTED: {model_name.upper()} (Confidence: {confidence:.2f}) ✨\n")

# 5. Start listening
try:
    with sd.InputStream(samplerate=RATE, channels=CHANNELS, dtype='int16', 
                        callback=audio_callback, blocksize=CHUNK):
        print("Listening... (Press Ctrl+C to stop)")
        while True:
            sd.sleep(1000)
except KeyboardInterrupt:
    print("\n🛑 Test stopped by user.")
except Exception as e:
    print(f"\n❌ Audio Stream Error: {e}")
    print("Hint: Check your macOS System Settings > Privacy & Security > Microphone to ensure VS Code is allowed.")
