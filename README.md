# Persona AI — A Companion That Actually Remembers You

Most AI chatbots forget you the moment you close the tab.

Persona AI doesn't.

Tell her your name today. Come back next week. She'll already know it — along with everything else you've shared: your hobbies, your stress, your wins, your favourite cricket team. Every conversation makes her know you a little better. That's the whole idea.

---

## The Problem This Solves

Every time you open a new ChatGPT session, you start from zero. You re-introduce yourself. You re-explain your context. You repeat yourself — again and again — to something that should, by now, know you.

Persona AI is an attempt to fix that. Not with a massive context window, not with a database dump at the start of every chat — but with a layered memory system that mirrors how humans actually remember things: facts, feelings, and the shape of past conversations.

---

## The Architecture
<img width="4546" height="4392" alt="image" src="https://github.com/user-attachments/assets/37add944-514e-4449-b654-ced15bf82ef4" />



---

## How the Memory Works

There are four layers, each doing a different job:

**Core Memory** — who Suzy is, and the permanent basics about you (name, age). Always present. Never changes mid-conversation.

**Semantic Memory** — individual facts extracted and stored over time. *"Suryansh is learning Docker." "Suryansh loves cricket."* Stored as embeddings in ChromaDB, retrieved by meaning not keyword — so asking "what are my hobbies?" surfaces cricket even if you never used the word "hobbies" when you mentioned it.

**Episodic Memory** — whole conversation summaries stored at the end of each session. Not just facts, but the *feel* of a conversation. *"Suryansh seemed stressed about his job search. We talked through it and he felt a bit better."* This is what makes Suzy feel like she lived through conversations with you, not just collected data from them.

**User Profile** — a consolidation of everything known about you, rewritten into a coherent paragraph after each session and loaded at startup. This means Suzy wakes up already briefed — she doesn't wait for retrieval to kick in.

---

## What Happens Each Session

**When you start:**
```
Load user profile (always)
    +
Semantic search Chroma for relevant facts + past episodes
    +
Last 15 messages from this session (sliding window)
    ↓
Everything injected into Suzy's system prompt
```

**Every turn:**
```
Your message
    ↓
Retrieve relevant memories from Chroma
    ↓
Suzy builds a reply with full context
    ↓
You get a response
```

**When you quit:**
```
Summarize the whole conversation → store as episode
    ↓
Consolidate new facts → update user profile paragraph
    ↓
Clean up Chroma → merge duplicates, resolve contradictions
```

One session end does the work that used to require an LLM call after every single message. Slower in batch, but cheaper and smarter — she sees the full conversation before deciding what's worth keeping.

---

## Tech Stack

| What | Why |
|---|---|
| LangGraph | Conversation graph — nodes, state, edges |
| ChromaDB | Local vector database for semantic + episodic memory |
| LangChain + Groq | LLM integration (llama-3.3-70b-versatile) |
| Python + uv | Clean dependency management |

No cloud databases. No Docker required. Everything runs locally — memory persists in a `./memory_store` folder on disk.

---

## Project Structure

```
persona-ai/
│
├── main.py              # LangGraph graph, chat loop, session lifecycle
├── memory.py            # All memory operations (store, retrieve, consolidate, reflect)
├── persona.json         # Suzy's identity + permanent user facts
├── user_profile.txt     # Auto-updated profile paragraph (generated, don't edit manually)
│
├── memory_store/        # ChromaDB persistent storage (auto-created)
│   ├── user_memories    # Semantic facts collection
│   └── episodic_memories # Conversation summaries collection
│
├── .env                 # GROQ_API_KEY goes here
├── pyproject.toml       # Dependencies
└── .gitignore           # Keeps .env and memory_store out of git
```

---

## Getting Started

**1. Clone and install**
```bash
git clone https://github.com/Suryansh-singh-137/personna-ai
cd persona-ai
uv sync
```

**2. Add your Groq API key**
```
# .env
GROQ_API_KEY=your_key_here
```
Get a free key at [console.groq.com](https://console.groq.com)

**3. Edit the persona** (optional)

Open `persona.json` and change Suzy's name, personality, and your basic info:
```json
{
  "name": "suzy",
  "personality": "loving and caring from the core of her heart",
  "user_facts": {
    "name": "Suryansh",
    "age": 20,
    "gender": "male"
  }
}
```

**4. Run**
```bash
uv run main.py
```

Type `quit` or `exit` to end a session. Memory saves automatically on exit.

---

## Memory Commands (coming soon)

| Command | What it does |
|---|---|
| `quit` / `exit` | Save session and exit cleanly |
| `!memory` | Show all stored facts about you |
| `!profile` | Show current user profile |
| `!clear` | Reset all memories (fresh start) |

---



## What Makes This Different from a Basic Chatbot

| Feature | Basic ChatGPT session | Persona AI |
|---|---|---|
| Remembers your name | ❌ next session | ✅ always |
| Knows your hobbies | ❌ | ✅ extracted + stored |
| References past conversations | ❌ | ✅ episodic memory |
| Gets to know you over time | ❌ | ✅ profile evolves |
| Runs locally | depends | ✅ fully local |
| Cost per message | 1 LLM call | 1 LLM call |

---

## Inspired By

The memory architecture in this project was directly inspired by [Letta's research on memory models and agents that learn](https://www.letta.com/blog/towards-agents-that-learn). The distinction they draw — RAG retrieves, memory *learns* — is the core idea behind how this project is structured.

---

## What's Next

- [ ] Web UI (FastAPI + simple React frontend)
- [ ] Voice input/output (Whisper + TTS)
- [ ] Mood tracking over time
- [ ] Memory browser (view/edit stored facts)
- [ ] Multi-persona support

---
