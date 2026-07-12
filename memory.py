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
        role = "User" if isinstance(msg, HumanMessage) else "sidhzi"
        conversation_text += f"{role}: {msg.content}\n"
    
    prompt = f"""Summarize this conversation in 3-4 sentences. 
Focus on: what topics were discussed, what the user's mood seemed like, 
any important things they shared. Write it as a memory from sidhzi's perspective.

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
    3. Resolve contradictions, keep most specific/recent

    Respond in exactly this format:

    <facts>
    cleaned fact 1
    cleaned fact 2
    cleaned fact 3
    </facts>""" 
    reponse = llm.invoke([HumanMessage(content=prompt)])
    try :
        raw = reponse.content
        cleaned_facts_block = raw.split("<facts>")[1].split("</facts>")[0].strip()
        cleaned_facts = [f.strip() for f in cleaned_facts_block.split("\n") if f.strip()]
   
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



def consolidate_and_update(messages: list, llm):
    conversation_text = ""
    for  msg in  messages:
        role = "User" if isinstance(msg, HumanMessage) else "sidhzi"
        conversation_text += f"{role}: {msg.content}\n"
    try:
        with open("user_proflie_with_previous_sessions.txt", "r") as f:
            existing_profile  =  f.read()
    except FileNotFoundError:
        existing_profile = ""
    prompt = f"""You are a memory consolidation assistant. You have two jobs:
    1. Read the conversation and extract new facts about the user
    2. Update the existing profile with new information

    Existing profile:
    {existing_profile}

    Conversation:
    {conversation_text}

    Respond in exactly this format, nothing else:

    <facts>
    fact 1
    fact 2
    fact 3
    </facts>

    <profile>
    A coherent 4-6 sentence paragraph about the user merging old and new information.
    </profile>"""
    reponse  =  llm.invoke([HumanMessage(content=prompt)])
    try:
        raw = reponse.content
        # parse facts
        facts_block = raw.split("<facts>")[1].split("</facts>")[0].strip()
        new_facts = [f.strip() for f in facts_block.split("\n") if f.strip()]

        # parse profile
        profile = raw.split("<profile>")[1].split("</profile>")[0].strip()

        for fact in new_facts:
            store_memory(fact)
        with open("user_proflie_with_previous_sessions.txt", "w") as f:    
              f.write(profile)
    except json.JSONDecodeError:
        print("Error decoding JSON from LLM response. Response was:")
        print(reponse.content)         