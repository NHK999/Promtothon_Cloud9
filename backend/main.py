from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import json
import os

app = FastAPI()

# Allow your local HTML file to talk to this server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    week: int
    language: str

# PHASE 3: MEDICAL SAFETY LAYER
RED_FLAGS = ["bleeding", "severe pain", "fainted", "miscarriage", "emergency", "blood"]

def check_safety(message: str, language: str) -> str:
    msg_lower = message.lower()
    if any(flag in msg_lower for flag in RED_FLAGS):
        if language.lower() == "telugu":
            return "⚠️ వైద్యపరమైన హెచ్చరిక: దయచేసి వెంటనే డాక్టర్‌ను లేదా ఆసుపత్రిని సంప్రదించండి."
        elif language.lower() == "hindi":
            return "⚠️ चिकित्सा चेतावनी: कृपया तुरंत डॉक्टर या अस्पताल से संपर्क करें।"
        return "⚠️ MEDICAL ALERT: Please contact a doctor or visit a hospital IMMEDIATELY."
    return None

def get_trimester_knowledge(week: int) -> str:
    if week <= 13:
        file = "trimester_1.json"
    elif week <= 26:
        file = "trimester_2.json"
    else:
        file = "trimester_3.json"

    # Resolve from this file so it works whether you run from project root or backend/
    knowledge_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "knowledge"))
    path = os.path.join(knowledge_dir, file)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return "Basic pregnancy knowledge."

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    # 1. Check Safety
    safety_warning = check_safety(request.message, request.language)
    if safety_warning:
        return {"reply": safety_warning}

    # 2. Load Knowledge (Offline RAG alternative)
    knowledge = get_trimester_knowledge(request.week)

    # 3. Create Prompt
    system_prompt = f"""You are MatruMitra, a helpful pregnancy assistant.
    The user is in Week {request.week} of pregnancy.
    Reply strictly in {request.language}.
    Use this medical knowledge to answer: {knowledge}
    Do not prescribe medicine."""

    # 4. Call Local Ollama API (100% Offline)
    try:
        ollama_res = requests.post("http://localhost:11434/api/generate", json={
            "model": "qwen2.5:1.5b",
            "prompt": f"System: {system_prompt}\nUser: {request.message}\nAnswer:",
            "stream": False
        })
        return {"reply": ollama_res.json()["response"]}
    except Exception as e:
        return {"reply": "Error connecting to local AI."}

if __name__ == "__main__":
    import uvicorn
    # Pass the app object so this works as `python backend/main.py`
    # (string "backend.main:app" fails because the script is not a package).
    uvicorn.run(app, host="127.0.0.1", port=8000)
