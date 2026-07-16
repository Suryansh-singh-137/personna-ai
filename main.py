def main():
    print("Hello from personna-ai!")
import time
from dotenv import load_dotenv
from voice import speak
from langgraph.graph import StateGraph,START,END, add_messages
from typing import TypedDict, Annotated
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage,HumanMessage as HM
from  memory  import retrieve_memory,store_memory, retrieve_episodes,store_episode,summarize_conversation,reflection_and_clean, consolidate_and_update

class  ChatState(TypedDict):
       messages: Annotated[list, add_messages]
       retrieved_memories: list[str]
import json
with open("persona.json", "r") as f:
    persona = json.load(f)
try:
    with open("user_proflie_with_previous_sessions.txt", "r") as f:
        user_profile = f.read()
except FileNotFoundError:
    user_profile = "No information about user yet."

load_dotenv()

def chat_node(state:ChatState):

       memories  = state['retrieved_memories']
       recent_messages = state["messages"][-15:]
       memory_text = "\n".join(f"- {m}" for m in memories) if memories else "None yet"
       full_system_prompt = f"""{system_prompt}
       What you remember about {persona['user_facts']['name']}:
       {memory_text}"""
       messages = [SystemMessage(content=full_system_prompt)] + recent_messages
       response = llm.invoke(messages)
       return  {"messages":[response]}

def  retrieve_memory__node(state:ChatState):
       last_message = state['messages'][-1].content
       facts = retrieve_memory(last_message)
       episodes  = retrieve_episodes(last_message)
       return  {
              "retrieved_memories": facts + episodes
       }

system_prompt = f"""Your name is {persona['name']}.
Your personality: {persona['personality']}.

What you know about {persona['user_facts']['name']}:
{user_profile}

Stay in character always."""


llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    streaming=True
)
graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)
graph.add_node("retrieve_memory", retrieve_memory__node)
graph.add_edge(START, "retrieve_memory")
graph.add_edge("retrieve_memory", "chat_node")
graph.add_edge("chat_node", END)
personaa = graph.compile()
if __name__ == "__main__":
    state = {"messages": [], "retrieved_memories": []}

    while True:
        user_input = input("You: ")

        if user_input.lower() in ["exit", "quit"]:
            ...
            break

        state["messages"].append(HM(content=user_input))

        final_state = None

        print(f"{persona['name']}: ", end="", flush=True)

        for chunk in personaa.stream(
            state,
            stream_mode=["messages", "values"],
            version="v2",
        ):
            if chunk["type"] == "messages":
                msg, metadata = chunk["data"]

                if msg.content:
                    for ch in msg.content:
                        print(ch, end="", flush=True)
                        time.sleep(0.02)

            elif chunk["type"] == "values":
                final_state = chunk["data"]

        print()

        if final_state is not None:
            state = final_state
            full_response = state["messages"][-1].content
            speak(full_response)