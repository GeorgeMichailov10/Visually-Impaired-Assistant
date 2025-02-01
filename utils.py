import vosk
import pyaudio
import json
import pyttsx3
import numpy as np
import mss
import openai
import base64
import cv2 
from queue import Queue
class Utils:
    def __init__(self, task_queue: Queue):
        # Input Audio attributes
        self.keyword = "hey assistant"
        self.model = vosk.Model("vosk-model-small-en-us-0.15")
        self.recognizer = vosk.KaldiRecognizer(self.model, 16000)
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8192)

        # Output Audio attributes
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)
        self.engine.setProperty('volume', 0.9)
        voices = self.engine.getProperty('voices')
        self.engine.setProperty('voice', voices[1].id)

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
                    print("User's goal detected!")
                    return 1  # Example return value

    #----Output Audio methods-----------------------------------------------

    def speak(self, text: str):
        self.engine.say(text)
        self.engine.runAndWait()

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

    # def send_message(prompt: str) -> str:
        # Send the prompt to the LLM
        # Return the LLM response

    # def send_frame(prompt: str, frame: np.ndarray) -> str:
        # Send the frame and prompt to the LLM
        # Return the LLM response

    # def send_frames(prompt: str, frames: list[np.ndarray]) -> str:
        # Send the frames and prompt to the LLM
        # Return the LLM response

