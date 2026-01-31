from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import requests

app = FastAPI(title="Thinka AI Backend")

# -----------------------------
# Enable CORS (frontend access)
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Health check
# -----------------------------
@app.get("/")
def root():
    return {"message": "Thinka AI backend running with memory"}

# -----------------------------
# Request model
# -----------------------------
class ChatRequest(BaseModel):
    message: str
    image: Optional[str] = None  # base64 or placeholder

# -----------------------------
# In-memory chat history
# -----------------------------
conversation_history = []

# -----------------------------
# Chat endpoint
# -----------------------------
@app.post("/chat")
def chat(req: ChatRequest):
    # Save user text
    conversation_history.append(f"User: {req.message}")

    # If image exists (UI feature)
    if req.image:
        conversation_history.append("[User sent an image]")

    # Build prompt with memory
    full_prompt = "\n".join(conversation_history) + "\nAI:"

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "phi",
                "prompt": full_prompt,
                "stream": False
            },
            timeout=60
        )

        ai_reply = response.json().get(
            "response",
            "Sorry, I couldn't generate a response."
        )

    except Exception as e:
        ai_reply = "⚠️ AI service is unavailable right now."

    # Save AI reply
    conversation_history.append(f"AI: {ai_reply}")

    return {"reply": ai_reply}
