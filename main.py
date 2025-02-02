# Running loop design

# Create LLM instance + task queue
# Create a single utility instance
# Start main interaction thread
# Start collision detection thread

from utils import Utils
import threading
from resolver import text_recognition, object_recognition, object_location


def main_loop(stop_event: threading.Event):
    utils = Utils()
    while not stop_event.is_set():
        utils.passive_listening()
        task_number, goal = utils.active_listening()
        print(f"Task number: {task_number}")
        if task_number == 1:
            text_recognition(utils, goal)
        elif task_number == 2:
            object_recognition(utils, goal)
        elif task_number == 3:
            object_location(utils, goal)
        elif task_number == 9:
            utils.speak("Your request is not related to the tasks I can help with.")

if __name__ == "__main__":
    stop_event = threading.Event()
    # threading.Thread(target=collision_detection_thread, args=(llm.get_queue(), stop_event)).start()
    main_loop(stop_event)
    
    



