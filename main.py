# Running loop design

# Create LLM instance + task queue
# Create a single utility instance
# Start main interaction thread
# Start collision detection thread

from LLM import LLM
from utils import Utils
from queue import Queue
import threading
import time
from resolver import text_recognition, object_recognition, object_location


def main_thread(task_queue: Queue, stop_event: threading.Event):
    utils = Utils(task_queue)
    while not stop_event.is_set():
        utils.passive_listening()

        task_number, goal = utils.active_listening()
        if task_number == 1:
            text_recognition(utils, goal)
        elif task_number == 2:
            object_recognition(utils, goal)
        elif task_number == 3:
            object_location(utils, goal)

def collision_detection_thread(task_queue: Queue, stop_event: threading.Event):
    utils = Utils(task_queue)
    while not stop_event.is_set():
        time.sleep(1)

if __name__ == "__main__":
    llm = LLM()
    stop_event = threading.Event()
    # threading.Thread(target=collision_detection_thread, args=(llm.get_queue(), stop_event)).start()
    threading.Thread(target=main_thread, args=(llm.get_queue(), stop_event)).start()

    while not stop_event.is_set():
        llm.check_task_queue()
        time.sleep(0.1)
    
    



