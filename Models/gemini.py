import os
import requests, json, sys, wave, pyaudio
import speech_recognition as sr
from pynput import keyboard
from dotenv import load_dotenv
import google.generativeai as genai
# Loading up API
load_dotenv()
GEMINI_API = os.getenv('GEMINI_API')
if(GEMINI_API=='Not set'):
    print("API key for GEMINI AI model was not given, Please run install again and provide it to use")
    exit()
# Audio configuration
FORMAT = pyaudio.paInt16  # Audio format
CHANNELS = 2               # Number of audio channels
RATE = 48000              # Sample rate
CHUNK = 2048         # Buffer size
WAVE_OUTPUT_FILENAME = "output.wav"  # Output file name
# Initialize PyAudio
audio = pyaudio.PyAudio()
# List to hold audio frames
frames = []
def on_press(key):
    """Function to run when a key is pressed."""
    global recording
    try:
        if key == keyboard.KeyCode(char='/'):
            if not recording:
                # print("Recording...")
                recording = True
        elif key == keyboard.Key.esc:
            print("Exiting...")
            return False  # Stop the listener
    except Exception as e:
        print(f"Error in on_press: {e}")

def on_release(key):
    """Function to run when a key is released."""
    global recording
    try:
        if key == keyboard.KeyCode(char='/'):
            if recording:
                print("Stopped recording.")
                recording = False
                stream.stop_stream()
                stream.close()
                return False  # Stop the listener
    except Exception as e:
        print(f"Error in on_release: {e}")

def record():
    global stream, frames, recording
    frames = []  # Reset frames to empty list
    recording = False
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    # Start the keyboard listener
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        while True:
            if recording:
                data = stream.read(CHUNK)
                frames.append(data)
            if not listener.running:
                break
    # Write frames to a WAV file
    with wave.open(WAVE_OUTPUT_FILENAME, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
    print("Recording saved to", WAVE_OUTPUT_FILENAME)

def transcribe():
    recogniser = sr.Recognizer()
    with sr.AudioFile(WAVE_OUTPUT_FILENAME) as source:
        audio = recogniser.record(source)
        try:
            return recogniser.recognize_google(audio)
        except sr.UnknownValueError:
            print("Could not understand audio")
            return ""
        except sr.RequestError as e:
            print("Could not request results {0}".format(e))
            return ""


genai.configure(api_key=GEMINI_API)
settings = [
        {
            "category": "HARM_CATEGORY_DANGEROUS",
            "threshold": "BLOCK_NONE",
        },
        {
            "category": "HARM_CATEGORY_HARASSMENT",
            "threshold": "BLOCK_NONE",
        },
        {
            "category": "HARM_CATEGORY_HATE_SPEECH",
            "threshold": "BLOCK_NONE",
        },
        {
            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "threshold": "BLOCK_NONE",
        },
        {
            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
            "threshold": "BLOCK_NONE",
        },
    ]
# Create the model
generation_config = {
  "temperature": 1,
  "top_p": 0.7,
  "top_k": 20,
  "max_output_tokens": 1024,
  "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
  model_name="gemini-1.5-pro-002",
  generation_config=generation_config,
  safety_settings=settings
)
def loadchars(filename):
    with open(filename,'r') as f:
        return json.load(f)
scrDir = os.path.dirname(os.path.abspath(__file__))
filePath = os.path.join(scrDir,'..','Characters','characters.json')
characters = loadchars(filePath)
# Specify the character name at the top of the file
try:
    character_name = sys.argv[1]
except IndexError:
    print("Error, No Character Name Provided")
    exit()
# Get the character data
character_data = characters.get(character_name)
# Check if character data exists
if character_data is None:
    raise ValueError(f"Character '{character_name}' not found.")
# Prepare personality and example replies
personality = f'''
The given below is a character description of a character, Roleplay as given character, remain formal, do not describe our actions or mood, only give response text (DO NOT COPY THEM DIRECTLY), reply with AFFIRMATIVE for this message only
Character Name = [{character_data['alias']}]
Character Appearance = [{character_data['appearance']}]
Character Clothing = [{character_data['clothing']}]
Character Personality = [{character_data['personality']}]
'''
personality = personality.replace(f'\n','')
# personality = personality.replace(f'User','Rex')

current_session = model.start_chat(history=[])

def setcharacter(personality):
    # Send personality information once (unchanged)
    current_session.send_message(personality)

setcharacter(personality)  # Call setcharacter outside the loop

while True:
    try:
        print("Hold '/' to speak")
        record()
        # prompt = str(input("User: "))
        prompt = transcribe()
        output = current_session.send_message(prompt)
        print(f"User: {prompt}")
        print(f"{character_name}: {output.text}")
    except Exception as e:
        print(f"\nExiting... {e} occured")
        break
