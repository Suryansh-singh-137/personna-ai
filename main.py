def main():
    print("Hello from personna-ai!")

from dotenv import load_dotenv
from langgraph.graph import StateGraph,START,END, add_messages
from typing import TypedDict, Annotated
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage,HumanMessage
class  ChatState(TypedDict):
       messages: Annotated[list, add_messages]
import json
with open("persona.json", "r") as f:
    persona = json.load(f)


load_dotenv()

def chat_node(state:ChatState):
       messages = [SystemMessage(content=system_prompt)] + state['messages']
       response =  llm.invoke(messages)
       return  {"messages":[response]}

system_prompt = f"""Your name is {persona['name']}.
Your personality: {persona['personality']}.
You are talking to {persona['user_facts']['name']}, 
a {persona['user_facts']['age']} year old {persona['user_facts']['gender']}.
Stay in character always."""


llm =  ChatGroq( model="qwen/qwen3-32b")       
graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)
graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)
personaa = graph.compile()
if __name__ == "__main__":
       state = {"messages": []}
       while  True:
              user_input  =  input("You: ")
              if user_input.lower() in ["exit", "quit"]:
                        break
              state['messages'].append(HumanMessage(content=user_input))
              response =  personaa.invoke(state)
              print(f"{persona['name']}: {response['messages'][-1].content}")
              
