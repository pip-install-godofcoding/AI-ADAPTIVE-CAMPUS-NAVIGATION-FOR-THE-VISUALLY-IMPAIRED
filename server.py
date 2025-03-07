import sys
import subprocess
import signal
import uvicorn
from fastapi import FastAPI
import requests  # Import for making API requests
from gemini_api import process_command

app = FastAPI()

# Get the correct Python executable inside the virtual environment
python_executable = sys.executable

# Global variables to track processes
navigation_process = None
object_detection_process = None

@app.get("/")
def home():
    return {"message": "Server is running"}

@app.get("/start_navigation")
def start_navigation():
    global navigation_process
    if navigation_process is None or navigation_process.poll() is not None:
        navigation_process = subprocess.Popen([python_executable, "navigation.py"])
        return {"message": "Navigation started"}
    return {"message": "Navigation is already running"}

@app.get("/stop_navigation")
def stop_navigation():
    global navigation_process
    if navigation_process and navigation_process.poll() is None:
        try:
            navigation_process.terminate()  # Try graceful stop
            navigation_process.wait()  # Ensure it exits
            navigation_process = None
            return {"response": "Navigation stopped."}
        except Exception as e:
            return {"response": f"Error stopping navigation: {str(e)}"}
    return {"response": "No navigation process is running."}

@app.get("/start_object_detection")
def start_object_detection():
    global object_detection_process
    if object_detection_process is None or object_detection_process.poll() is not None:
        object_detection_process = subprocess.Popen([python_executable, "object_detection.py"])
        return {"message": "Object detection started"}
    return {"message": "Object detection is already running"}

@app.get("/stop_object_detection")
def stop_object_detection():
    global object_detection_process
    if object_detection_process and object_detection_process.poll() is None:
        try:
            object_detection_process.terminate()  # Try graceful stop
            object_detection_process.wait()  # Ensure it exits
            object_detection_process = None
            return {"response": "Object detection stopped."}
        except Exception as e:
            return {"response": f"Error stopping object detection: {str(e)}"}
    return {"response": "No object detection process is running."}

@app.post("/ask_gemini")
async def ask_gemini(request: dict):
    command = request.get("prompt", "").lower()  # Convert to lowercase for easier matching
    
    # Handle "stop navigation" and "stop object detection" commands
    if "stop navigation" in command:
        print("[INFO] Gemini AI detected 'stop navigation'. Stopping navigation...")
        requests.get("http://127.0.0.1:8000/stop_navigation")
        return {"response": "Navigation stopped."}
    
    if "stop object detection" in command:
        print("[INFO] Gemini AI detected 'stop object detection'. Stopping object detection...")
        requests.get("http://127.0.0.1:8000/stop_object_detection")
        return {"response": "Object detection stopped."}

    # Process other commands normally
    response = process_command(command)
    return {"response": response}

if __name__ == "__main__":
    print(f"Using Python Executable: {python_executable}")  # Debugging
    uvicorn.run(app, host="0.0.0.0", port=8000)
