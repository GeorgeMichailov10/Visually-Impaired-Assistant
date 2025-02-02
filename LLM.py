import cv2
import torch
from transformers import Qwen2_5_VLForConditionalGeneration, AutoProcessor, BitsAndBytesConfig
from qwen_vl_utils import process_vision_info
from PIL import Image
import numpy as np
from queue import Queue
import time
import threading

import os

class LLM:
    def __init__(self):
        self.quantization_config = BitsAndBytesConfig(load_in_8bit=True)
        self.model = Qwen2_5_VLForConditionalGeneration.from_pretrained("Qwen/Qwen2.5-VL-3B-Instruct", quantization_config=self.quantization_config, device_map="auto")
        self.processor = AutoProcessor.from_pretrained("Qwen/Qwen2.5-VL-3B-Instruct")


        self.task_queue = Queue()
        
    def check_task_queue(self):
        task = self.task_queue.get()
        task_type, response_holder, event, *args = task
        if task_type == "send_message":
            response_holder["response"] = self.send_message(args[0])
            event.set()
        elif task_type == "send_frame":
            response_holder["response"] = self.send_frame(args[0], args[1])
            event.set()
        elif task_type == "send_frames":
            response_holder["response"] = self.send_frames(args[0], args[1])
            event.set()
        elif task_type == "send_video":
            response_holder["response"] = self.send_video(args[0], args[1])
            event.set()

    def get_queue(self):
        return self.task_queue

    def send_message(self, prompt: str) -> str:

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                ],
            }
        ]
        return self.interact(messages)

    def send_frame(self, prompt: str, frame: np.ndarray) -> str:
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image_pil = Image.fromarray(image_rgb)
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image", "image": image_pil}, 
                    {"type": "text", "text": prompt},
                ],
            }
        ]
        return self.interact(messages, has_vision=True)

    def send_frames(self, prompt: str, frames: list[np.ndarray]) -> str:
        images_pil = [
            Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)) for frame in frames
        ]


        messages = [
            {
                "role": "user",
                "content": [{"type": "image", "image": img} for img in images_pil] +
                        [{"type": "text", "text": prompt}]
            }
        ]
        
        return self.interact(messages, has_vision=True)

    def send_video(self, prompt:str, video_path:str, frame_interval:int = 5) -> str:
        cap = cv2.VideoCapture(video_path)
        frames = []
        frame_count = 0
        while cap.isOpened():

            ret, frame = cap.read()
            if not ret:
                break
            frames.append(frame)
            if frame_count % frame_interval == 0:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frames.append(Image.fromarray(frame_rgb))
            frame_count += 1
        cap.release()
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "video", "video": frames},
                    {"type": "text", "text": prompt},
                ],
            }
        ]
        try:
            os.remove(video_path)
        except:
            pass
        return self.interact(messages, has_vision=True)
                
    def interact(self, messages: list[dict], has_vision: bool = False) -> str:
        text = self.processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)


        if has_vision:
            image_inputs, video_inputs = process_vision_info(messages)
            inputs = self.processor(
                text=[text], images=image_inputs, videos=video_inputs, padding=True, return_tensors="pt"
            )
        else:
            inputs = self.processor(text=[text], padding=True, return_tensors="pt")


        inputs = inputs.to("cuda")

        with torch.no_grad():
            generated_ids = self.model.generate(**inputs, max_new_tokens=256)


        generated_ids_trimmed = [
            out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
        ]

        output_text = self.processor.batch_decode(
            generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
        )


        return output_text[0]
