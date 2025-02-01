import cv2
import torch
from transformers import Qwen2_5_VLForConditionalGeneration, AutoProcessor
from qwen_vl_utils import process_vision_info
from PIL import Image
import numpy as np


model = Qwen2_5_VLForConditionalGeneration.from_pretrained("Qwen/Qwen2.5-VL-3B-Instruct", torch_dtype=torch.float16, device_map="auto")
processor = AutoProcessor.from_pretrained("Qwen/Qwen2.5-VL-3B-Instruct")

def send_message(prompt: str) -> str:
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
            ],
        }
    ]
    return interact(messages)

def send_frame(prompt: str, frame: np.ndarray) -> str:
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
    return interact(messages, has_vision=True)

def send_frames(prompt: str, frames: list[np.ndarray]) -> str:
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
    
    return interact(messages, has_vision=True)

def interact(messages: list[dict], has_vision: bool = False) -> str:
    text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

    if has_vision:
        image_inputs, video_inputs = process_vision_info(messages)
        inputs = processor(
            text=[text], images=image_inputs, videos=video_inputs, padding=True, return_tensors="pt"
        )
    else:
        inputs = processor(text=[text], padding=True, return_tensors="pt")

    inputs = inputs.to("cuda")

    with torch.no_grad():
        generated_ids = model.generate(**inputs, max_new_tokens=256)

    generated_ids_trimmed = [
        out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
    ]

    output_text = processor.batch_decode(
        generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
    )

    return output_text[0]


