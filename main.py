# Running loop design

# Create LLM instance + task queue
# Create a single utility instance
# Start main interaction thread
# Start collision detection thread

from LLM import LLM

if __name__ == "__main__":
    llm = LLM()
    queue = llm.get_queue()
