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


def main_thread(task_queue: Queue):
    utils = Utils(task_queue)
    while True:
        utils.passive_listening()
        task_number = utils.active_listening()
        if task_number == 1:




def collision_detection_thread(task_queue: Queue):
    utils = Utils(task_queue)




if __name__ == "__main__":
    llm = LLM()
    threading.Thread(target=main_thread, args=(llm.get_queue(),)).start()
    threading.Thread(target=collision_detection_thread, args=(llm.get_queue(),)).start()

    while True:
        time.sleep(10)
    

