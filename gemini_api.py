import google.generativeai as genai
from dotenv import load_dotenv
import os
import subprocess

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

def process_command(command):
    command = command.lower()

    if "start navigation" in command:
        subprocess.Popen(["python", "navigation.py"])
        return "Navigation started."

    elif "stop navigation" in command:
        # Add logic to stop navigation (if required)
        return "Navigation stopped."

    elif "start object detection" in command:
        subprocess.Popen(["python", "object_detection.py"])
        return "Object detection started."

    elif "stop object detection" in command:
        # Add logic to stop object detection (if required)
        return "Object detection stopped."

    else:
        return "Sorry, I didn't understand that command."

