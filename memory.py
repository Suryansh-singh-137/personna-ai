import chromadb
import  uuid
from datetime import datetime
from langchain_core.messages import SystemMessage,HumanMessage
def  init_memory():
  client = chromadb.PersistentClient(path="./memory_store")
  collection = client.get_or_create_collection(name="user_memories")
  return  collection 
def init_episodic_memory():
    client = chromadb.PersistentClient(path="./memory_store")
    collection = client.get_or_create_collection(name="episodic_memories")
    return  collection    
def  store_memory(facts:str):
    collection = init_memory()
    collection.add(
        documents=[facts],
        metadatas=[{"source": "user"}],
        ids = [uuid.uuid4().hex]
    )     


def  retrieve_memory(query:str):
   collection  =  init_memory()
   results = collection.query(
      query_texts=[query],
      n_results=3
   )    
   return  results["documents"][0]
def store_episode(summary: str):
   collection = init_episodic_memory()
   collection.add(
         documents=[summary],
         metadatas=[{"timestamp": datetime.now().isoformat(), "source": "episode"}],
         ids=[uuid.uuid4().hex]
   )
def   retrieve_episodes(query: str):
   collection  =  init_episodic_memory()
   results = collection.query(
         query_texts=[query],
         n_results=2
   )
   return results["documents"][0]

def summarize_conversation(messages: list, llm) -> str:
    conversation_text = ""
    for msg in messages:
        role = "User" if isinstance(msg, HumanMessage) else "Suzy"
        conversation_text += f"{role}: {msg.content}\n"
    
    prompt = f"""Summarize this conversation in 3-4 sentences. 
Focus on: what topics were discussed, what the user's mood seemed like, 
any important things they shared. Write it as a memory from Suzy's perspective.

Conversation:
{conversation_text}

Summary:"""
    
    response = llm.invoke([HumanMessage(content=prompt)])
    return response.content