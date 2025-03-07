import pvporcupine
import pyaudio
import struct
import requests
import os
import speech_recognition as sr
from dotenv import load_dotenv
import sys
import streamlit as st

# Load environment variables for Picovoice
load_dotenv()
PICOVOICE_ACCESS_KEY = os.getenv("PICOVOICE_ACCESS_KEY")

# Streamlit App Configuration
st.set_page_config(page_title="Jarvis AI Assistant", layout="wide")

# Custom HTML & CSS for Styling
st.markdown("""
    <style>
    body {
        background: linear-gradient(135deg, #2C3E50, #34495E);
        color: white;
        font-family: 'Roboto', sans-serif;
    }

    .title {
        text-align: center;
        font-size: 60px;
        font-weight: bold;
        color: #00ffcc;
        margin-top: 40px;
        text-shadow: 4px 4px 10px rgba(0, 255, 204, 0.7);
    }

    .subtitle {
        text-align: center;
        font-size: 22px;
        color: #ffffff;
        margin-bottom: 40px;
        font-style: italic;
    }

    .detected {
        font-size: 26px;
        color: #ffcc00;
        text-align: center;
        font-weight: bold;
        margin-top: 10px;
        animation: bounce 1s infinite;
    }

    .response-box {
        background: rgba(0, 255, 204, 0.1);
        padding: 20px;
        margin: 20px auto;
        border-radius: 15px;
        width: 80%;
        text-align: center;
        box-shadow: 0 6px 12px rgba(0, 255, 204, 0.2);
    }

    .history-box {
        background: rgba(255, 255, 255, 0.1);
        padding: 15px;
        margin-top: 30px;
        border-radius: 15px;
        box-shadow: 0px 0px 12px rgba(0, 255, 204, 0.4);
    }

    .btn {
        display: inline-block;
        background-color: #00ffcc;
        color: white;
        padding: 15px 30px;
        border-radius: 12px;
        font-size: 18px;
        cursor: pointer;
        transition: 0.3s ease-in-out;
        margin-top: 20px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 255, 204, 0.4);
    }

    .btn:hover {
        background-color: #00e6b8;
        transform: translateY(-4px);
    }

    .btn:active {
        transform: translateY(2px);
    }

    @keyframes bounce {
        0%, 100% {
            transform: translateY(0);
        }
        50% {
            transform: translateY(-10px);
        }
    }

    /* Card styling for response */
    .response-card {
        background-color: #1c2833;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 10px rgba(0, 255, 204, 0.3);
        color: #fff;
    }

    .history-item {
        font-size: 18px;
        color: #00ffcc;
        margin-bottom: 10px;
        padding: 5px;
        border-radius: 10px;
        background: rgba(0, 255, 204, 0.1);
    }
    </style>
""", unsafe_allow_html=True)

# Title and Subtitle
st.markdown('<p class="title">Jarvis AI Assistant</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Listening for the wake word <strong>"Jarvis"</strong>...</p>', unsafe_allow_html=True)

# Placeholder for responses
response_placeholder = st.empty()

# Command History Placeholder
history_placeholder = st.empty()

# Speech-to-Text History list to keep track of the spoken commands
command_history = []

def update_command_history(command):
    """Update command history in the sidebar"""
    command_history.append(command)
    history_placeholder.empty()
    with history_placeholder:
        st.markdown('<div class="history-box"><h3>Command History</h3>', unsafe_allow_html=True)
        for i, cmd in enumerate(command_history[-5:]):  # Limit to last 5 commands
            st.markdown(f'<div class="history-item">{cmd}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

def start_wake_word_detection():
    """Detects wake word and processes commands."""
    porcupine = pvporcupine.create(
        access_key=PICOVOICE_ACCESS_KEY,
        keywords=["jarvis"]
    )

    pa = pyaudio.PyAudio()
    audio_stream = pa.open(
        rate=porcupine.sample_rate,
        channels=1,
        format=pyaudio.paInt16,
        input=True,
        frames_per_buffer=porcupine.frame_length
    )

    recognizer = sr.Recognizer()

    print("Listening for wake word...")

    while True:
        pcm = audio_stream.read(porcupine.frame_length, exception_on_overflow=False)
        pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)

        if porcupine.process(pcm) >= 0:
            print("Wake word detected! Listening for command...")
            response_placeholder.markdown('<p class="detected">Wake word detected! Listening for command...</p>', unsafe_allow_html=True)

            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source)
                try:
                    print("Listening for command...")
                    response_placeholder.markdown('<p class="detected">Listening for command...</p>', unsafe_allow_html=True)
                    audio = recognizer.listen(source, timeout=5)
                    command = recognizer.recognize_google(audio).lower()
                    print(f"You said: {command}")

                    # Add command to history
                    update_command_history(command)

                    # Send command to the backend (Gemini API)
                    response = requests.post("http://127.0.0.1:8000/ask_gemini", json={"prompt": command})

                    # Display response
                    response_text = response.json().get("response", "No response from backend")
                    print(response_text)

                    # Show response in a cool-looking card
                    response_placeholder.markdown(f'<div class="response-card"><p>{response_text}</p></div>', unsafe_allow_html=True)
                    st.success(f"Backend Response: {response_text}")

                except sr.UnknownValueError:
                    print("[ERROR] Could not understand the command")
                    response_placeholder.markdown('<p class="detected">[ERROR] Could not understand the command</p>', unsafe_allow_html=True)
                except sr.RequestError:
                    print("[ERROR] Error connecting to speech recognition service")
                    response_placeholder.markdown('<p class="detected">[ERROR] Error connecting to speech service</p>', unsafe_allow_html=True)

# Run the wake word detectionstre
if __name__ == "__main__":
    start_wake_word_detection()