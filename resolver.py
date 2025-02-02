from utils import Utils
import time
import numpy as np

def text_recognition(u: Utils, goal: str):
    print("Text recognition")
    frame = u.capture_screen()
    prompt = f"The user wants: '{goal}'. "
    extracted_text = u.send_frame(prompt, frame)
    print(extracted_text)
    u.speak(f"{extracted_text}")

def object_recognition(u: Utils, goal: str):
    frame = u.capture_screen()
    prompt = f"You are assisting a completely blind user from their point of view. Identify the key object(s) in the frame through scene description. Be descriptive, but concise. The user wants: '{goal}'"
    recognized_objects = u.send_frame(prompt, frame)
    u.speak(recognized_objects)

def object_location(u:Utils, goal:str):
    found = False
    while not found:
        frames = []
        u.speak("Please look around slowly and I will try to find what you are looking for.")
        start = time.time()
        while time.time() - start < 3:
            frames.append(u.capture_screen())
            time.sleep(0.7)
        print(len(frames))
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
    u.speak(response)
    u.speak("Now would you like me to guide you to it?")
    user_res = u.basic_listening()
    prompt = f"In one word 'yes' or 'no' is this a confirmatory statement? User response: '{user_res}'"
    retry_response = u.send_message(prompt)
    print(retry_response)
    if "yes" not in retry_response.lower():
        u.speak("Happy to help!")
        return
    else:
        u.speak("Ok, I now will guide you to it.")
        room_navigation(u, goal, response, frame)
   
def room_navigation(u:Utils, goal:str, goal_location:str, original_frame:np.ndarray):
    u.speak(f"I am coming up with a plan to get you to the goal location.")
    adjust_frame = u.capture_screen()
    adjust_prompt = f"You are assisting a completely blind user in navigating to {goal_location}. Based on this description of the room and the first image, have them turn their position to the left or right using degrees if the way they are currently facing  is the second image. In simple terms, your goal is to make the new point of view go from the second image to the first image."
    adjust_response = u.send_frame(adjust_prompt, adjust_frame)
    u.speak(adjust_response)
    

    prompt = f"You are assisting a completely blind user. Due to their visual impairment, this process will be iterative. Giving colors and descriptions of small objects that are unrelated will not help. Please plan in baby steps to help the user accomplish their navigation through the room.The user wants to go to the following location: '{goal}'. The goal location is: '{goal_location}'. Please give a quick description of the room with 2 short sentences describing if it is easy or difficult to navigate through and of any potential obstacles they may encounter. Also and create a plan of action for traversing to the goal location and remember you have already located so step one should be something like 'turn right slightly' or 'take two steps forward'. The first image is of the image where you have already located the object and the second imageis where the user is currently facing."
    curr_frame = u.capture_screen()
    plan = u.send_frames(prompt, [original_frame, curr_frame], max_tokens=250, model="gpt-4o")
    u.speak(plan)

    done = False

    while not done:
        frame = u.capture_screen()
        prompt = (f"The user wants to go to the following location: '{goal}'. The goal location is: '{goal_location}'."
                 f"Please give the next set of instructions for the next few steps to continue traversing to the goal location. These should come in the format of turning, stepping, and then turning again in that order (turning if necessary, you may skip turning). Each iteration has a range of two steps of movement."
                 f"If there are any hazards or collisions in the next few steps, please alert the user with a warning such as 'be careful of a cable on the floor' or 'carefull of the person in front of you'. Be extra cautious with items on the ground or in the way."
                 f"This is the plan you created at the beginning: '{plan}'. The second image is the original location of the user and the first image is what you see now."
                 )
        next_step = u.send_frames(prompt, [frame, original_frame])
        u.speak(next_step)
        done_prompt = f"In one word yes or no has the user within arms reach of the goal location?"
        frame = u.capture_screen()
        done_response = u.send_frame(done_prompt, frame)
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