import chromadb
import  uuid

def  init_memory():
  client = chromadb.PersistentClient(path="./memory_store")
  collection = client.get_or_create_collection(name="user_memories")
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


