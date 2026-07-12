def main():
    print("Hello from personna-ai!")

from dotenv import load_dotenv
from langgraph.graph import StateGraph,START,END, add_messages
from typing import TypedDict, Annotated
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage,HumanMessage as HM
from  memory  import retrieve_memory,store_memory, retrieve_episodes,store_episode,summarize_conversation,reflection_and_clean

class  ChatState(TypedDict):
       messages: Annotated[list, add_messages]
       retrieved_memories: list[str]
import json
with open("persona.json", "r") as f:
    persona = json.load(f)


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

def extract_facts_node(state: ChatState):
    # get last user message and AI reply
    messages = state["messages"]
    last_human = messages[-2].content  # second to last = user
    last_ai = messages[-1].content     # last = AI reply
    
    extraction_prompt = f"""You are a memory extraction assistant.
Look at this conversation exchange and extract ONE important fact about the user if present.
Return ONLY valid JSON, nothing else.

User said: "{last_human}"
AI replied: "{last_ai}"

If there is a clear fact about the user (preference, hobby, life detail, goal), return:
{{"worth_saving": true, "fact": "user <fact here>"}}

If nothing important, return:
{{"worth_saving": false, "fact": ""}}"""

    response = llm.invoke([HM(content=extraction_prompt)])
    
    import json
    try:
        result = json.loads(response.content)
        if result["worth_saving"] and result["fact"]:
            store_memory(result["fact"])
            print(f"\n[Memory stored: {result['fact']}]")
    except:
        pass  # if LLM returns bad JSON, just skip
    
    return {}

system_prompt = f"""Your name is {persona['name']}.
Your personality: {persona['personality']}.
You are talking to {persona['user_facts']['name']}, 
a {persona['user_facts']['age']} year old {persona['user_facts']['gender']}.
Stay in character always."""


llm = ChatGroq(model="llama-3.3-70b-versatile")   
graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)
graph.add_node("retrieve_memory", retrieve_memory__node)
graph.add_node("extract_facts", extract_facts_node)
graph.add_edge(START, "retrieve_memory")
graph.add_edge("retrieve_memory", "chat_node")
graph.add_edge("chat_node", "extract_facts")
graph.add_edge("extract_facts", END)
personaa = graph.compile()
if __name__ == "__main__":
    state = {"messages": [], "retrieved_memories": []}

    while True:
        user_input = input("You: ")

        if user_input.lower() in ["exit", "quit"]:
            if state["messages"]:
                summary = summarize_conversation(state["messages"], llm)
                store_episode(summary)
                print(f"\n[Episode stored: {summary}]")
            print("Exiting chat. Goodbye! WITH MEMORY cleanup")
            reflection_and_clean(llm)
            break

        state["messages"].append(HM(content=user_input))
        state = personaa.invoke(state)

        print(f"{persona['name']}: {state['messages'][-1].content}")