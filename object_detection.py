import cv2
import speech_recognition as sr
import threading
import time
import pyttsx3
from queue import Queue
from ultralytics import YOLO

# Queue for managing speech requests
speech_queue = Queue()
exit_flag = False  # Exit flag for stopping all threads

def speak_worker():
    """Thread worker function to process speech requests sequentially."""
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)

    while not exit_flag:
        try:
            text = speech_queue.get(timeout=1)  # Wait for text
            if text:
                print(f"[INFO] Speaking: {text}")
                engine.say(text)
                engine.runAndWait()
        except:
            continue  # Avoid breaking due to empty queue

def speak(text):
    """Adds text to the speech queue for processing."""
    speech_queue.put(text)

def detect_objects():
    global exit_flag
    cap = cv2.VideoCapture(0)
    model = YOLO("yolov8n.pt")  # Load YOLOv8 model
    last_spoken_time = time.time()
    spoken_objects = set()
    
    while cap.isOpened() and not exit_flag:
        if not detection_active:
            time.sleep(1)
            continue
        
        ret, frame = cap.read()
        if not ret:
            break
        
        results = model(frame)
        detected_objects = set()
        
        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = box.conf[0].item()
                cls = int(box.cls[0].item())
                label = f"{model.names[cls]} {conf:.2f}"
                detected_objects.add(model.names[cls])
                
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        if detected_objects and (time.time() - last_spoken_time > 3 or detected_objects != spoken_objects):
            speak("Detected " + ", ".join(detected_objects))
            last_spoken_time = time.time()
            spoken_objects = detected_objects.copy()
        
        cv2.imshow("YOLOv8 Object Detection", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

def voice_control():
    global detection_active, exit_flag
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening for commands: 'start detection', 'stop detection', or 'exit'")

        while not exit_flag:
            try:
                audio = recognizer.listen(source)
                command = recognizer.recognize_google(audio).lower()
                print(f"You said: {command}")
                
                if "start detection" in command:
                    detection_active = True
                    speak("Starting object detection")  # Announce the command
                    print("Object detection started")
                
                elif "stop detection" in command:
                    detection_active = False
                    speak("Stopping object detection")  # Announce the command
                    print("Object detection stopped")
                
                elif "exit" in command:
                    exit_flag = True
                    speak("Exiting program")  # Announce the command
                    print("Exiting program")
                    break
            
            except sr.UnknownValueError:
                print("[ERROR] Could not understand the command")
            except sr.RequestError:
                print("[ERROR] Error connecting to speech recognition service")

# Global variables
detection_active = False

# Run threads
t1 = threading.Thread(target=detect_objects)
t2 = threading.Thread(target=voice_control)
t3 = threading.Thread(target=speak_worker, daemon=True)  # Background speech thread

t1.start()
t2.start()
t3.start()

t1.join()
t2.join()
exit_flag = True  # Ensure speech thread stops
print("Program exited successfully")


#AIzaSyAM6HmXX_9_rZZ-DmVQ9hpt5T1C3Kb4c8Y