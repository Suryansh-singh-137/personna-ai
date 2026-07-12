import chromadb
import  uuid
import json
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
def reflection_and_clean(llm):
    collection = init_memory()

    all_data = collection.get()
    all_memories = all_data["documents"]
    ids = all_data["ids"]
    
    if not all_memories:
        return "No memories to reflect on."
    
    fact_text  = ""
    for fact  in  all_memories:
        fact_text += "-"+fact+"\n"
    prompt = f"""You are a memory cleanup assistant.
    Here are all the facts stored about a user:

    {fact_text}

    Your job:
    1. Remove exact duplicates
    2. Merge facts that say the same thing differently  
    3. Resolve contradictions (keep the more specific/recent sounding one)
    4. Return a clean deduplicated list

    Return ONLY a JSON array of strings, nothing else. Example:
    ["user's name is Suryansh", "user loves cricket", "user studies CS"]"""   
    reponse = llm.invoke([HumanMessage(content=prompt)])
    try :
        cleaned_facts  =  json.loads(reponse.content)
    except json.JSONDecodeError:
        print("Error decoding JSON from LLM response. Response was:")
        print(reponse.content)
        return []
    collection.delete(ids=ids) # Clear existing memories
    for fact in cleaned_facts:
        collection.add(
            documents=[fact],
            metadatas=[{"source": "reflection"}],
            ids=[uuid.uuid4().hex]
        )    
 
if __name__ == "__main__":
    results = retrieve_memory("what do you know about the user")
    for r in results:
        print(r)   


def consolidate_and_update(messages: list, llm):
    conversation_text = ""
    for  msg in  messages:
        role = "User" if isinstance(msg, HumanMessage) else "Suzy"
        conversation_text += f"{role}: {msg.content}\n"
    try:
        with open("user_proflie_with_previous_sessions.txt", "r") as f:
            existing_profile  =  f.read()
    except FileNotFoundError:
        existing_profile = ""
    prompt = f"""You are a memory consolidation assistant.you have two jobs:
1. Read the following conversation between Suzy and the user, and summarize it into a few key facts about the user.
2. Compare these new facts with the existing profile of the user, and update the profile with any new information. If there are contradictions, keep the most recent information.
existing profile:
{existing_profile}
conversation:
{conversation_text}
return  only  valid JSON of the updated profile, nothing else. Example:
{{
  "new_facts": ["fact 1", "fact 2"],
  "updated_profile": "A coherent 4-6 sentence paragraph about the user merging old and new information about the whole converation"
}}"""
    reponse  =  llm.invoke([HumanMessage(content=prompt)])
    try:
        result = json.loads(reponse.content)
        for fact in result.get("new_facts", []):
            store_memory(fact)
        with open("user_proflie_with_previous_sessions.json", "w") as f:    
             f.write(result["updated_profile"])
    except json.JSONDecodeError:
        print("Error decoding JSON from LLM response. Response was:")
        print(reponse.content)         