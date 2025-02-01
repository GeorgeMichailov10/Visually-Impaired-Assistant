# Running loop design

# Create LLM instance + task queue
# Create a single utility instance
# Start main interaction thread
# Start collision detection thread

from LLM import LLM
from utils import Utils

if __name__ == "__main__":
    llm = LLM()
    utils = Utils(llm.get_queue())
    utils.speak(utils.add_llm_task("send_message", "Hello, how are you?"))

