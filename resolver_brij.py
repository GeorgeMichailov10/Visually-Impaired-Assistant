from utils import capture_screen, send_frame, send_frames, divide_screen, speak

def text_recognition(goal: str):
    """Captures a frame, sends it to Qwen 3B for text recognition with the user's goal, and speaks the result."""
    frame = capture_screen()  # Capture the screen
    if frame is None:
        speak("Error capturing screen.")  # Notify the user
        return

    # Construct the prompt dynamically by including the user's goal
    prompt = f"The user wants: '{goal}'. You are helping a visually impaired user to help read text from the captured image or frame. 
    Please break it down into paragraphs and read it for them."
    
    # Send frame and prompt to Qwen 3B
    extracted_text = send_frame(prompt, frame)

    if extracted_text.strip():  # If text is detected
        speak(f"The text reads: {extracted_text}")  # Speak the extracted text
    else:
        speak("Text could not be detected, please try again.")

def object_recognition(goal: str):
    """Captures frames, divides the screen into quadrants and detects object(s) based on user goal."""

    # Capture initial frame
    frame = capture_screen()
    if frame is None:
        speak("Error locating object, please capture a better angle.")
        return
    
    # Split frame into quadrants to reduce search space
    quadrants = divide_screen()

    # Dynamic prompt including user's goal
    prompt = f"The user wants: '{goal}'. You are helping a visually impaired user to help identify an object. 
    The original frame is broken down into quadrants to reduce the search space. Look through the list of those frame partitions
    and identify the object(s) as per the user goal, point out any other objects for help locating the target."

    # Send quadrant partitions to Qwen 3B for processing
    recognized_objects = send_frames(prompt, list(quadrants.values()))

    # Speak the detect objects
    if recognized_objects:
        speak("The identified objects are: {recognized_objects}")
    else:
        speak("The object was not identified in the footage captured")
