from utils import Utils
import time

def text_recognition(u: Utils, goal: str):
    print("Text recognition")
    frame = u.capture_screen()
    prompt = f"The user wants: '{goal}'. "
    extracted_text = u.send_frame(prompt, frame)
    print(extracted_text)
    u.speak(f"{extracted_text}")

def object_recognition(u: Utils, goal: str):
    frame = u.capture_screen()
    prompt = f"Identify the key object(s) in the frame through scene description. Be descriptive, but concise. The user wants: '{goal}'"
    recognized_objects = u.send_frame(prompt, frame)
    u.speak(recognized_objects)

def object_location(u:Utils, goal:str):
    found = False
    while not found:
        frames = []
        u.speak("Please look around slowly and I will try to find what you are looking for.")
        start = time.time()
        while time.time() - start < 5:
            frames.append(u.capture_screen())
            time.sleep(0.5)
        prompt = f"You are  looking for the following object: '{goal}'. Return the image number where you see it (the most clearly). Return a 1 if you see it in the first image, 2 if you see it in the second image, and so on. Return a 0 if you do not see it in any of the images. Return a vague description of where you found it."
        response = u.send_frames(prompt, frames)
        image_number = ""
        for char in response:
            if char in "1234567890":
                image_number += char
        image_number = int(image_number)
        if image_number == 0:
            u.speak("I did not find it the object you are looking for. Would you like me to try again?")
            user_res = u.basic_listening()
            prompt = f"In one word yes or no does the user want to try again? User response: '{user_res}'"
            retry_response = u.send_message(prompt)
            if "yes" not in retry_response.lower():
                u.speak('I apologize for not being able to find it. Please try again later.')
                return
        else:
            break

    u.speak(f"I believe I have found what you are looking for!")
    frame = frames[image_number - 1]
    prompt = f"In the previous image, you found the following object: '{goal}'. This was the description: '{response}'. Please give a deeper description of where you found it."
    response = u.send_frame(prompt, frame)
    u.speak(response)
    u.speak("Now would you like me to guide you to it?")
    user_res = u.basic_listening()
    prompt = f"In one word yes or no does the user want to try again? User response: '{user_res}'"
    retry_response = u.send_message(prompt)
    if "yes" not in retry_response.lower():
        u.speak("Happy to help!")
        return
    else:
        u.speak("Ok, I will guide you to it.")
        room_navigation(u, goal, response)



def room_navigation(u:Utils, goal:str, goal_location:str = None):
    # If goal location is not provided, find it
    if goal_location is None:
        goal_location = goal
    prompt = f"The user wants to go to the following location: '{goal}'. The goal location is: '{goal_location}'. Please give a quick description of the room and create a plan of action for traversing to the goal location."
    frame = u.capture_screen()
    plan = u.send_frame(prompt, frame)
    u.speak(plan)
    buffer = []
    done = False
    while not done:
        frame = u.capture_screen()
        prompt = (f"The user wants to go to the following location: '{goal}'. The goal location is: '{goal_location}'."
                 f"This is the plan you created at the beginning: '{plan}'."
                 f"These are the previous instructions you have given the user: '{''.join(buffer[::-1])}'."
                 f"Please give the next set of instructions for the next few steps to continue traversing to the goal location."
                 )
        next_step = u.send_frame(prompt, frame)
        buffer.append(next_step)
        u.speak(next_step)
        done_prompt = f"In one word yes or no has the user arrived at the goal location based on the last instruction: '{next_step}'?"
        done_response = u.send_message(done_prompt)
        if "yes" in done_response.lower():
            u.speak("Happy to help!")
            return

def collision_detection(u:Utils):
    counter = 10
    while counter > 0:
        frame = u.capture_screen()
        prompt = f"You are looking from the point of view of the user. If the user continues to move forward, will there be a collision or a hazard of any kind? We only care about directly in front of the user. Answer either 'no' or give a very concise description of the potential collision or hazard and how to avoid it." 
        collision_response = u.send_frame(prompt, frame)
        if "no" not in collision_response.lower()[:min(len(collision_response), 5)]:
            print(f"Collision detected: {collision_response}")
        counter -= 1
        time.sleep(0.5)



    

