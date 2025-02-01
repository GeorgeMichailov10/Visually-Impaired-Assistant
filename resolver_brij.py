from utils import capture_screen, send_frame, speak

def text_recognition(goal: str):
    """Captures a frame, sends it to Qwen 3B for text recognition with the user's goal, and speaks the result."""
    frame = capture_screen()  # Capture the screen
    if frame is None:
        speak("Error capturing screen.")  # Notify the user
        return

    # Construct the prompt dynamically by including the user's goal
    prompt = f"The user wants: '{goal}'. You are helping a visually impaired user to help read text from the captured image or frame. Please break it down into paragraphs and read it for them."
    
    # Send frame and prompt to Qwen 3B
    extracted_text = send_frame(prompt, frame)

    if extracted_text.strip():  # If text is detected
        speak(f"The text reads: {extracted_text}")  # Speak the extracted text
    else:
        speak("No readable text detected.")