import wave
import math
import struct

def create_beep(filename="alert.mp3", duration=1.0, freq=440.0, sample_rate=44100):
    # Note: Writing a true MP3 requires LAME or similar libraries which is complex in pure python.
    # We will write a WAV file but name it as user requested or just stick to WAV.
    # To keep it simple and compatible with playsound, let's write a standard WAV file 
    # but give it the extension the config expects, or update config to use .wav.
    # For robust MP3 support, one usually needs 'ffmpeg' installed. 
    # We will change the config to use .wav to be safe and simple.
    
    print("Generating a test sound file (beep)...")
    
    n_samples = int(sample_rate * duration)
    
    try:
        with wave.open(filename, 'w') as obj:
            obj.setnchannels(1) # Mono
            obj.setsampwidth(2) # 2 bytes (16 bit) per sample
            obj.setframerate(sample_rate)
            
            for i in range(n_samples):
                value = int(32767.0 * math.sin(2.0 * math.pi * freq * i / sample_rate))
                data = struct.pack('<h', value)
                obj.writeframesraw(data)
                
        print(f"Successfully created {filename}")
        
    except Exception as e:
        print(f"Error creating sound file: {e}")

if __name__ == "__main__":
    create_beep("alert.wav")
