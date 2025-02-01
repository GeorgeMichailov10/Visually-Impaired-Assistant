from langchain.memory import ConversationBufferMemory


def room_navigation(goal: str):
    memory = ConversationBufferMemory(return_messages=True)
    sys_prompt = f"""
    You are a helpful assistant that can navigate a room.
    You are given a goal and a description of the room.
    You need to navigate to the goal.
    """
    
    

