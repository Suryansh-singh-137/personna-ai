def main():
    print("Hello from personna-ai!")

from langgraph.graph import StateGraph,START,END, add_messages
from typing import TypedDict, Annotated
from langchain_groq import ChatGroq

class  ChatState(TypedDict):
       messages: Annotated[list[], add_messages]
def chat_node(state:ChatState):
       messages = state['messages']
       response =  llm.invoke(messages)
       return  {"messages":[response]}



llm =  ChatGroq( model="qwen/qwen3-32b")       
graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)
graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)
personaa = graph.compile()
if __name__ == "__main__":
    main()
