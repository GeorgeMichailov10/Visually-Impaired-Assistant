import vosk
import pyaudio
import json
import pyttsx3
import numpy as np
import mss
from io import BytesIO
import threading
import time
import requests
import base64
from PIL import Image
import cv2
import os
from dotenv import load_dotenv

load_dotenv()

priority_speaker = None
speaker_lock = threading.Lock()
global_output_engine = pyttsx3.init()
interruption_event = threading.Event()

class Utils:
    def __init__(self, is_priority_speaker: bool = False):
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
        self.engine.setProperty('voice', voices[0].id)
        self.is_priority_speaker = is_priority_speaker


        # Screen attributes
        self.sct = mss.mss()

        # LLM attributes
        self.model = "qwen-vl-max"
        self.api_key = os.getenv("ALIBABA_API_KEY")
        self.base_url = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1/chat/completions"
        self.default_max_tokens = 100

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
                if text:
                    print("User's goal detected. Querying LLM")
                    prompt = (
                        f"This is what the user wants to do: {text}. It is your job to determine which of the following tasks isn most relevant and thus you need to perform: 1: Text Recognition on screen, sign, or book, 2: Describe a scene out in the real world, 3: Object Location such as where a specific object is relative to the user, 4: Helping navigate through a room, 8: None of the above or is inappeopriate, or 9: Done for now. Do NOT make assumptions, only return a function number if this task is direct such as they ask you to read a page, not taking multiple steps to come to a conclusion."
                        "Please return only the number associated with the task you need to perform and explain why you chose that number."
                    )
                    response = self.send_message(prompt)
                    print(f"LLM Response: {response}")


                    for char in response:
                        if char in "123489":
                            print(f"Returning task number: {char}")
                            return int(char), text

    def basic_listening(self):
        try:
            while True:
                data = self.stream.read(4096, exception_on_overflow=False)
                if self.recognizer.AcceptWaveform(data):
                    result = self.recognizer.Result()
                    result_dict = json.loads(result)
                    text = result_dict.get('text', '')
                    if text:
                        return text
        except Exception as e:
            print(f"Error during basic listening: {e}")
            return ""

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
        height, width = 1600, 2560
        screenshot = self.sct.grab(self.sct.monitors[1])
        screenshot = np.array(screenshot)
        #screenshot = screenshot[125:height-75, 920:1640]
        return screenshot

    def divide_screen(self, screen: np.ndarray):
        height, width, _ = screen.shape
        mid_x, mid_y = width // 2, height // 2


        top_left = screen[:mid_y, :mid_x]
        top_right = screen[:mid_y, mid_x:]
        bottom_left = screen[mid_y:, :mid_x]
        bottom_right = screen[mid_y:, mid_x:]

        return [top_left, top_right, bottom_left, bottom_right]

    #----LLM methods-----------------------------------------------------

    def send_message(self, prompt: str, max_tokens=None) -> str:
        messages = [
            {"role": "system", "content": "You are a helpful assistant for a completely blind person and are seeing the world through their point of view."},
            {"role": "user", "content": prompt}
        ]
        return self.interact(messages, max_tokens)

    def send_frame(self, prompt: str, frame: np.ndarray, max_tokens=None) -> str:
        print("Sending frame to LLM")
        image_base64 = self.image_to_base64(frame)

        messages = [
            {"role": "system", "content": "You are a helpful assistant for a completely blind person and are seeing the world through their point of view."},
            {
                "role": "user",
                "content": [

                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{image_base64}"}
                    },
                    {"type": "text", "text": prompt},
                ],
            }
        ]
        return self.interact(messages, max_tokens)

    def send_frames(self, prompt: str, frames: list[np.ndarray], max_tokens=None) -> str:
        images_base64 = [
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/png;base64,{self.image_to_base64(frame)}"}
            }
            for frame in frames
        ]

        messages = [
            {"role": "system", "content": "You are a helpful assistant for a completely blind person and are seeing the world through their point of view."},
            {
                "role": "user",
                "content": images_base64 + [{"type": "text", "text": prompt}],
            }
        ]

        return self.interact(messages, max_tokens)

    def interact(self, messages: list[dict], max_tokens=None) -> str:
        print("Interacting with LLM")
        """Sends a request to the Alibaba Cloud API and retrieves the response."""
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens if max_tokens else self.default_max_tokens
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        response = requests.post(self.base_url, json=payload, headers=headers)

        if response.status_code == 200:
            output_text = response.json().get("choices", [{}])[0].get("message", {}).get("content", "")
            return output_text
        else:
            return f"Error: {response.status_code} - {response.text}"

    @staticmethod
    def image_to_base64(image: np.ndarray) -> str:
        image_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        buffered = BytesIO()
        image_pil.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode("utf-8")

