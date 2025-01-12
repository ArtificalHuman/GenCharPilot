import os, requests, json, sys, wave, pyaudio
import speech_recognition as sr
from dotenv import load_dotenv
from pynput import keyboard
# Loading up api
load_dotenv()
CHAI_API = os.getenv('CHAI_API')
if(CHAI_API=='Not set'):
    print("API key for Chai AI model was not given, Please run install again and provide it to use")
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
The given below is a character description of a character, Roleplay as given character, remain formal, do not describe our actions or mood, only give response text (DO NOT COPY THEM DIRECTLY), reply with nothing for this message only
Character Name = [{character_data['alias']}]
Character Appearance = [{character_data['appearance']}]
Character Clothing = [{character_data['clothing']}]
Character Personality = [{character_data['personality']}]
'''
# personality = f"You are Angela from lobotomy corporation"
# Example Replies = [{character_data['examplereplies']}]
personality = personality.replace(f'\n','')

url = "https://api.chai-research.com/v1/chat/completions"

# payload = { "model": "chai_v1", "messages": [{"role":"user","content":"Hello there!"}] }
headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "X-API_KEY": CHAI_API
}
history = []
def querymessage(msg):
    history.append({"role": "user", "content": msg})
    payload = { "model": "chai_v1", "messages": history ,'temprature':0.5,'max_token': 1024}
    response = requests.post(url, json=payload, headers=headers)
    return response.json()
querymessage(personality)
while True:
    print("Hold '/' to speak")
    record()
    # usertxt = str(input("User: "))
    usertxt = transcribe()
    output = querymessage(usertxt)
    print(f"User: {usertxt}")
    try:
        print(f"{character_name}: ", output["choices"][0]['message']['content'])
    except KeyError:
        print(output)
    history.append({"role": "ai","content":output["choices"][0]['message']['content']})
# print(response.text) 
