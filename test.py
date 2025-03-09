import pyttsx3

# Initialize pyttsx3 engine
engine = pyttsx3.init()

# Get available voices
voices = engine.getProperty('voices')

# Print available voices (optional, to check what voices are available)
for voice in voices:
    print(f"Voice ID: {voice.id} - Name: {voice.name} - Lang: {voice.languages}")

# Set the voice to Microsoft David (assuming the second voice is Microsoft David, but you may need to adjust the index)
david_voice_id = None
for voice in voices:
    if "David" in voice.name and "English" in voice.languages[0]:
        david_voice_id = voice.id
        break

# If Microsoft David is found, set it as the active voice
if david_voice_id:
    engine.setProperty('voice', david_voice_id)
else:
    print("Microsoft David voice not found. Using default voice.")

# Set speech rate (speed of speech)
engine.setProperty('rate', 150)  # Lower values = slower speech

# Set volume (0.0 to 1.0)
engine.setProperty('volume', 1.0)  # Max volume

# Speak the text
engine.say("Hello Val-tehree, how are you doing today")

# Wait until speaking is finished
engine.runAndWait()
