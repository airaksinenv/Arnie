import speech_recognition as sr
import ollama
from TTS.api import TTS
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Load Coqui TTS model
tts = TTS("tts_models/en/ljspeech/tacotron2-DDC")

# Initialize speech recognizer
recognizer = sr.Recognizer()

# Spotify authentication setup
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id="your_client_id",
                                               client_secret="your_client_secret",
                                               redirect_uri="http://localhost:8888/callback",
                                               scope="user-library-read user-read-playback-state user-modify-playback-state"))

# OpenWeatherMap API setup
weather_api_key = "your_openweathermap_api_key"
weather_url = "http://api.openweathermap.org/data/2.5/weather"

def speak_arnold(text):
    print("Arnold says:", text)
    
    # Generate speech and save as file
    tts.tts_to_file(text=text, file_path="arnold.wav")
    
    # Load audio file as a numpy array
    sample_rate, audio_data = wav.read("arnold.wav")
    
    # Modify pitch to make it sound deeper (Arnold effect)
    audio_data = np.interp(np.arange(0, len(audio_data), 1.2), np.arange(0, len(audio_data)), audio_data)
    
    # Play the modified audio
    sd.play(audio_data.astype(np.int16), samplerate=sample_rate)
    sd.wait()

def listen():
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

        try:
            command = recognizer.recognize_google(audio, language="en-US")
            print("You said:", command)
            return command.lower()
        except sr.UnknownValueError:
            print("Sorry, I didn't understand.")
            return None
        except sr.RequestError:
            print("Error with Google Speech Recognition.")
            return None

# Get weather info
def get_weather(city):
    params = {
        'q': city,
        'appid': weather_api_key,
        'units': 'metric'  # For Celsius temperatures
    }
    response = requests.get(weather_url, params=params)
    data = response.json()

    if data["cod"] != 200:
        return "Sorry, I couldn't fetch the weather data."
    
    temp = data['main']['temp']
    weather_description = data['weather'][0]['description']
    return f"The current temperature in {city} is {temp}°C with {weather_description}."

# Control Spotify
def play_spotify(track_name):
    results = sp.search(q=track_name, limit=1, type='track')
    if results['tracks']['items']:
        track_url = results['tracks']['items'][0]['external_urls']['spotify']
        sp.start_playback(uris=[track_url])
        return f"Playing {track_name} on Spotify!"
    else:
        return "Sorry, I couldn't find that track on Spotify."

# 🔥 Voice assistant with Llama 3
while True:
    user_input = listen()
    
    if user_input:
        if "stop" in user_input:
            print("Shutting down...")
            break

        # Handle weather requests
        if "weather" in user_input:
            # Extract city from user input, e.g., "weather in London"
            city = user_input.split("in")[-1].strip()
            weather_info = get_weather(city)
            speak_arnold(weather_info)
            continue

        # Handle Spotify requests
        if "play" in user_input:
            # Extract track name from user input, e.g., "play Bohemian Rhapsody"
            track_name = user_input.replace("play", "").strip()
            spotify_response = play_spotify(track_name)
            speak_arnold(spotify_response)
            continue

        # Send question to Ollama (Llama 3 model)
        response = ollama.chat(model="llama3", messages=[{"role": "user", "content": user_input}])
        reply_text = response['message']['content']

        # Speak response in Arnold's voice
        speak_arnold(reply_text)
