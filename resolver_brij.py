from utils import capture_screen, send_frame, send_frames, divide_screen, speak

def text_recognition(goal: str):
    """Captures a frame, sends it to Qwen 3B for text recognition with the user's goal, and speaks the result."""
    frame = capture_screen()  # Capture the screen

    # Construct the prompt dynamically by including the user's goal
    prompt = f"""You are helping a visually impaired user to help read text from the captured image or frame. The user wants: '{goal}'. """
    
    # Send frame and prompt to Qwen 3B
    extracted_text = send_frame(prompt, frame)

    if extracted_text.strip():  # If text is detected
        speak(f"{extracted_text}")  # Speak the extracted text

def object_recognition(goal: str):
    """Captures frames, divides the screen into quadrants and detects object(s) based on user goal."""

    # Capture initial frame
    frame = capture_screen()
    
    # Split frame into quadrants to reduce search space
    quadrants = divide_screen()

    # Dynamic prompt including user's goal
    prompt = f"""You are helping a visually impaired user to help identify an object. 
    The original frame is broken down into quadrants to reduce the search space. Look through the list of those frame partitions
    and identify the object(s) as per the user goal, point out any other objects near by for context. The user wants: '{goal}'."""

    # Send quadrant partitions to Qwen 3B for processing
    recognized_objects = send_frames(prompt, list(quadrants.values()))

    # Speak the detect objects
    if recognized_objects:
        speak("{recognized_objects}")
