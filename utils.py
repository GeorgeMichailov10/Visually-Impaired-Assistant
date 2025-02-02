import vosk
import pyaudio
import json
import pyttsx3
import numpy as np
import mss
from queue import Queue
import threading
import time
import re

priority_speaker = None
speaker_lock = threading.Lock()
global_output_engine = pyttsx3.init()
interruption_event = threading.Event()

class Utils:
    def __init__(self, task_queue: Queue, is_priority_speaker: bool = False):
        # Input Audio attributes
        self.keyword = "hey assistant"
        self.model = vosk.Model("vosk-model-small-en-us-0.15")
        self.recognizer = vosk.KaldiRecognizer(self.model, 16000)
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8192)

        # Output Audio attributes
        self.engine = global_output_engine
        self.engine.setProperty('rate', 150)
        self.engine.setProperty('volume', 0.9)
        voices = self.engine.getProperty('voices')
        self.engine.setProperty('voice', voices[1].id)
        self.is_priority_speaker = is_priority_speaker


        # Screen attributes
        self.sct = mss.mss()

        # LLM attributes
        self.task_queue = task_queue

    #----Input Audio methods-----------------------------------------------

    def passive_listening(self):
        print("Listening for activation phrase...")
        while True:
            data = self.stream.read(4096, exception_on_overflow=False)
            if self.recognizer.AcceptWaveform(data):
                result = self.recognizer.Result()
                result_dict = json.loads(result)
                text = result_dict.get('text', '')
                print(f"Recognized: {text}")
                if "activation phrase" in text.lower():
                    print("Activation phrase detected!")
                    break

    def active_listening(self):
        """Listens for the user's goal, queries the LLM to classify it, and returns the corresponding function number."""
        print("Listening for user's goal...")
        while True:
            data = self.stream.read(4096, exception_on_overflow=False)
            if self.recognizer.AcceptWaveform(data):
                result = self.recognizer.Result()
                result_dict = json.loads(result)
                text = result_dict.get('text', '')
                print(f"Recognized: {text}")
                # Placeholder for LLM processing
                if text:
                    print("User's goal detected. Querying LLM")
                    # LLM Prompt classification
                    prompt = (
                        f"You are assisting a visually impaired person with the following tasks: 1: Text Recognition, 2: Object Recognition, 3: Object Location."
                        "This is the user's goal: {text}. Return the number corresponding to the task you need to perform and return -1 if the goal is not related to the tasks."
                    )
                    response = self.add_llm_task("goal_classification", prompt)
                    return response

                
    #----Output Audio methods-----------------------------------------------

    def speak(self, text: str):
        global priority_speaker
        # Phase 1: Acquire the lock to set priority and interrupt if needed.
        with speaker_lock:
            if self.is_priority_speaker:
                priority_speaker = "collision"
                print("[Collision Detector] Interrupting default speech!")
                self.engine.stop()  # Interrupt any ongoing speech.
            else:
                # If a collision speech is in progress, wait.
                while priority_speaker == "collision":
                    time.sleep(0.05)
                priority_speaker = "default"
                print("[Default] Speaking...")

        self.engine.stop()
        time.sleep(0.1)
        self.engine.say(text)

        try:
            self.engine.runAndWait()
        except Exception as e:
            print("Engine exception:", e)

        # Phase 3: Clear our priority flag.
        with speaker_lock:
            if priority_speaker == ("collision" if self.is_priority_speaker else "default"):
                priority_speaker = None

    #----Screen methods-----------------------------------------------------

    def capture_screen(self):
        screenshot = self.sct.grab(self.sct.monitors[1])
        return np.array(screenshot)

    def divide_screen(self, screen: np.ndarray):
        height, width, _ = screen.shape
        mid_x, mid_y = width // 2, height // 2

        top_left = screen[:mid_y, :mid_x]
        top_right = screen[:mid_y, mid_x:]
        bottom_left = screen[mid_y:, :mid_x]
        bottom_right = screen[mid_y:, mid_x:]

        return [top_left, top_right, bottom_left, bottom_right]

    #----LLM methods-----------------------------------------------------

    def add_llm_task(self, task_type, *args):
        response_holder = {}
        event = threading.Event()
        self.task_queue.put((task_type, response_holder, event, *args))
        event.wait()
        return response_holder["response"]

