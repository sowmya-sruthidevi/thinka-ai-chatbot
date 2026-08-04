from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import requests

app = FastAPI(title="Thinka AI Backend")

# ---------------------------------------
# CORS
# ---------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # Replace with your Vercel URL later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------
# Ollama Configuration
# ---------------------------------------
OLLAMA_URL = "http://104.211.99.16:11434/api/generate"
MODEL_NAME = "phi3:mini"

# ---------------------------------------
# Health Check
# ---------------------------------------
@app.get("/")
def root():
    return {
        "status": "running",
        "model": MODEL_NAME,
        "message": "Thinka AI Backend is running successfully."
    }

# ---------------------------------------
# Request Model
# ---------------------------------------
class ChatRequest(BaseModel):
    message: str
    image: Optional[str] = None

# ---------------------------------------
# Chat Endpoint
# ---------------------------------------
@app.post("/chat")
def chat(req: ChatRequest):

    system_prompt = """
You are Thinka AI, a friendly AI assistant.

Instructions:
- Answer ONLY the user's current question.
- Do NOT invent previous conversations.
- Keep answers short unless the user asks for details.
- If asked for a definition:
  • Give a simple definition.
  • Give two examples.
- If asked programming questions:
  • Explain clearly.
  • Give code when appropriate.
- If the user simply says "hi", greet them naturally.
"""

    prompt = f"""{system_prompt}

User: {req.message}

Assistant:
"""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.4,
                    "num_predict": 300,
                    "num_ctx": 2048
                }
            },
            timeout=180
        )

        response.raise_for_status()

        result = response.json()

        ai_reply = result.get("response", "").strip()

        if not ai_reply:
            ai_reply = "Sorry, I couldn't generate a response."

        return {
            "reply": ai_reply
        }

    except requests.exceptions.Timeout:
        return {
            "reply": "⚠️ AI request timed out. Please try again."
        }

    except requests.exceptions.ConnectionError:
        return {
            "reply": "⚠️ Unable to connect to the AI server."
        }

    except Exception as e:
        return {
            "reply": f"⚠️ Backend Error: {str(e)}"
        }