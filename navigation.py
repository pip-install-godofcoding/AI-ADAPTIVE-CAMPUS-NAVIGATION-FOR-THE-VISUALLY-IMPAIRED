import pyttsx3
import requests  # For sending stop requests to the server
import time
import speech_recognition as sr
import sys
import googlemaps
import re

# Initialize Google Maps client with your API Key
API_KEY = " "  # Replace with your API key
gmaps = googlemaps.Client(key=API_KEY)

print(f"Running {__file__} with Python: {sys.executable}")  # Corrected the variable name

SERVER_URL = "http://127.0.0.1:8000"  # FastAPI server address

# Initialize Text-to-Speech Engine
engine = pyttsx3.init()
engine.setProperty('rate', 150)

def speak(text):
    print(f"[SPEAKING]: {text}")
    engine.say(text)
    engine.runAndWait()

def get_speech_input(prompt):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        speak(prompt)
        print(f"[INFO] Listening for: {prompt}")

        try:
            audio = recognizer.listen(source, timeout=8, phrase_time_limit=5)
            text = recognizer.recognize_google(audio).lower()
            print(f"[USER SAID]: {text}")

            if "stop navigation" in text:
                print("[INFO] Stop command detected! Sending request to stop navigation...")
                speak("Stopping navigation.")
                try:
                    requests.get(f"{SERVER_URL}/stop_navigation")  # Notify server
                except requests.RequestException as e:
                    print(f"[ERROR] Failed to send stop command: {e}")
                sys.exit()  # Stop this script immediately

            return text
        except sr.UnknownValueError:
            print("[ERROR] Could not understand speech")
            speak("Sorry, I could not understand. Please try again.")
        except sr.RequestError:
            print("[ERROR] Error connecting to speech recognition service")
            speak("I am having trouble connecting to the speech service.")
        return None

def start_navigation():
    speak("Say 'Start navigation' to begin.")
    while True:
        command = get_speech_input("Say 'Start navigation' to begin.")
        if command and "start navigation" in command:
            speak("Navigation starting.")
            break

    # Ask if the user is inside or outside
    speak("Are you inside the campus or outside?")
    while True:
        mode = get_speech_input("Say 'Inside' for inside campus or 'Outside' for outside campus.")
        if mode:
            if "inside" in mode:
                speak("You are inside the campus. Please say your destination.")
                indoor_navigation()
                break
            elif "outside" in mode:
                speak("You are outside the campus. Please say your destination.")
                outdoor_navigation()
                break
            else:
                speak("I didn't understand that. Please say either 'Inside' or 'Outside'.")

def indoor_navigation():
    # Example for indoor navigation: grid-based with dummy directions
    speak("You are now in indoor navigation mode.")
    speak("Please say your destination within the campus.")
    
    # Hardcoded destinations inside the campus
    destinations = {
        "library": ["Move straight, turn left, your destination is on the right."],
        "cafeteria": ["Move straight, take the second right, your destination is on the left."],
        "administration": ["Go straight, turn right, continue until the end, your destination is ahead."],
        "gym": ["Move straight, turn right, take the first left, your destination is on the right."]
    }

    destination = get_speech_input("Where do you want to go inside?")
    if not destination:
        speak("I couldn't understand your destination. Try again.")
        return

    destination = destination.lower()
    
    # Check if the destination exists in the predefined list
    if destination in destinations:
        speak(f"Starting indoor navigation to {destination}.")
        
        # Provide directions for the destination
        for direction in destinations[destination]:
            print(f"[DIRECTION]: {direction}")
            speak(direction)
            time.sleep(3)  # Simulate some time passing for each direction
        
        # Continuously listen for stop command
        stop_command = get_speech_input("Say 'Stop navigation' to end navigation.")
        if stop_command and "stop navigation" in stop_command:
            print("[INFO] Stopping navigation...")
            speak("Stopping navigation.")
            try:
                requests.get(f"{SERVER_URL}/stop_navigation")
            except requests.RequestException as e:
                print(f"[ERROR] Failed to send stop command: {e}")
            sys.exit()  # Exit navigation.py
    else:
        speak("Sorry, I couldn't find that destination. Please choose from Library, Cafeteria, Administration, or Gym.")
        return

def outdoor_navigation():
    speak("You are now in outdoor navigation mode.")
    destination = get_speech_input("Please say your destination for outdoor navigation.")
    if not destination:
        speak("I couldn't understand your destination. Try again.")
        return

    speak(f"Starting outdoor navigation to {destination}.")
    
    # Geocode the destination using Google Maps API to get the coordinates
    geocode_result = gmaps.geocode(destination)
    
    if geocode_result:
        # Extract latitude and longitude from the geocode result
        lat = geocode_result[0]['geometry']['location']['lat']
        lng = geocode_result[0]['geometry']['location']['lng']
        print(f"[INFO] Destination coordinates: Latitude: {lat}, Longitude: {lng}")
    else:
        speak("Sorry, I couldn't find that location.")
        return

    # Use Google Maps Directions API to get step-by-step directions
    origin = "12.9716,77.5946"  # Replace with user's current location (latitude,longitude)
    
    def get_directions(start, destination):
        """Fetches directions from Google Maps API"""
        try:
            directions = gmaps.directions(start, destination, mode="walking")
            if not directions:
                raise Exception("No directions found.")

            steps = directions[0]["legs"][0]["steps"]
            return [re.sub(r'<.*?>', '', step["html_instructions"]) for step in steps]  # Remove HTML formatting
        except Exception as e:
            print("[ERROR] Unable to fetch directions:", e)
            speak("Unable to fetch directions.")
            return []

    directions = get_directions(origin, f"{lat},{lng}")
    if directions:
        for step in directions:
            speak(step)
            print(f"[DIRECTION]: {step}")
            time.sleep(3)  # Simulate each direction with a short delay
        
        # Continuously listen for stop command
        stop_command = get_speech_input("Say 'Stop navigation' to end navigation.")
        if stop_command and "stop navigation" in stop_command:
            print("[INFO] Stopping navigation...")
            speak("Stopping navigation.")
            try:
                requests.get(f"{SERVER_URL}/stop_navigation")
            except requests.RequestException as e:
                print(f"[ERROR] Failed to send stop command: {e}")
            sys.exit()  # Exit navigation.py
    else:
        speak("Sorry, I couldn't find a route to your destination.")

if __name__ == "__main__":  # Fix: Corrected the __name_ check
    start_navigation()
