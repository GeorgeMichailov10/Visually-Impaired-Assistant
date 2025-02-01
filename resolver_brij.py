from utils import Utils

def text_recognition(u: Utils, goal: str):
    """Captures a frame, sends it to Qwen 3B for text recognition with the user's goal, and speaks the result."""
    frame = u.capture_screen()  # Capture the screen

    # Construct the prompt dynamically by including the user's goal
    prompt = f"""You are helping a visually impaired user to help read text from the captured image or frame. The user wants: '{goal}'. """
    
    # Send frame and prompt to Qwen 3B
    extracted_text = u.add_llm_task("text_recognition", prompt, frame)

    if extracted_text.strip():  # If text is detected
        u.speak(f"{extracted_text}")  # Speak the extracted text

def object_recognition(u: Utils, goal: str):
    """Captures frames, divides the screen into quadrants and detects object(s) based on user goal."""

    # Capture initial frame
    frame = u.capture_screen()
    
    # Split frame into quadrants to reduce search space
    quadrants = u.divide_screen()

    # Dynamic prompt including user's goal
    prompt = f"""You are helping a visually impaired user to help identify an object. 
    The original frame is broken down into quadrants to reduce the search space. Look through the list of those frame partitions
    and identify the object(s) as per the user goal, point out any other objects near by for context. The user wants: '{goal}'."""

    # Send quadrant partitions to Qwen 3B for processing
    recognized_objects = u.add_llm_task("object_recognition", prompt, *quadrants.values())

    # Speak the detect objects
    if recognized_objects:
        u.speak("{recognized_objects}")
