from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Local AI backend running with memory"}

class ChatRequest(BaseModel):
    message: str

# 🧠 Chat memory (in RAM)
conversation_history = []

@app.post("/chat")
def chat(req: ChatRequest):
    # Add user message to memory
    conversation_history.append(f"User: {req.message}")

    # Combine full conversation
    full_prompt = "\n".join(conversation_history) + "\nAI:"

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "phi",
            "prompt": full_prompt,
            "stream": False
        }
    )

    ai_reply = response.json()["response"]

    # Add AI reply to memory
    conversation_history.append(f"AI: {ai_reply}")

    return {"reply": ai_reply}
