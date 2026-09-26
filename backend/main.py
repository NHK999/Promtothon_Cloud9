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

# PHASE 3: COMPREHENSIVE OBSTETRIC EMERGENCY SAFETY LAYER
RED_FLAGS = [
    # Hemorrhage & Bleeding
    "bleeding", "heavy bleeding", "blood", "spotting with pain", "blood clot", "hemorrhage",
    "రక్తం", "రక్తస్రావం", "raktham", "rakthasravam", "khoon", "खून", "रक्तस्राव",
    
    # Severe Abdominal & Pelvic Pain
    "severe pain", "sharp pain", "severe cramp", "stomach pain", "abdominal pain", "pelvic pain",
    "unbearable pain", "నొప్పి", "తీవ్రమైన నొప్పి", "noppi", "dard", "दर्द", "पेट दर्द", "तेज दर्द",
    
    # Respiratory & Cardiovascular
    "difficulty breathing", "shortness of breath", "chest pain", "breathless", "cannot breathe",
    "ఊపిరి", "ఊపిరి ఆడకపోవడం", "saans", "साँस", "सीने में दर्द",
    
    # Neurological & Consciousness
    "seizure", "convulsion", "fit", "fainted", "fainting", "passed out", "unconscious", "loss of consciousness", "collapsed",
    "స్పృహ", "స్పృహ తప్పడం", "spruha", "behoshi", "behos", "बेहोश", "दौरा", "fits",
    
    # Preeclampsia / Vision / Severe Headache
    "vision change", "blurred vision", "flashing light", "severe headache", "extreme headache", "high bp", "swollen face",
    "కళ్ళు తిరగడం", "తలనొప్పి", "dhundhla", "धुंधला", "सिरदर्द",
    
    # Amniotic Fluid / Water Break
    "leaking fluid", "water broke", "water break", "amniotic fluid", "water leakage", "leaking water",
    "ఉమ్మనీరు", "ummaneeru", "pani", "पानी छूटना",
    
    # Fetal Movement Reduction
    "baby not moving", "no movement", "less movement", "reduced movement", "no kicks", "stopped moving",
    "కదలికలు లేవు", "kadalikalu", "bacha hil", "बच्चा हिल नहीं रहा", "हलचल बंद",
    
    # General Emergencies
    "miscarriage", "emergency", "urgent hospital", "danger", "ఆపద", "అత్యవసరం", "आपातकाल", "खतरा"
]

def check_safety(message: str, language: str) -> dict:
    msg_lower = message.lower()
    for flag in RED_FLAGS:
        if flag.lower() in msg_lower:
            lang = language.lower()
            if lang == "telugu":
                warning = "⚠️ అత్యవసర హెచ్చరిక: ఇది గర్భధారణ అత్యవసర పరిస్థితి కావచ్చు. దయచేసి ఆలస్యం చేయకుండా వెంటనే సమీపంలోని ఆసుపత్రికి వెళ్ళండి లేదా 108 అంబులెన్స్‌ను సంప్రదించండి."
            elif lang == "hindi":
                warning = "⚠️ आपातकालीन चेतावनी: यह गर्भावस्था की गंभीर स्थिति हो सकती है। कृपया तुरंत नजदीकी अस्पताल जाएँ या 108 एम्बुलेंस से संपर्क करें।"
            else:
                warning = "⚠️ MEDICAL EMERGENCY ALERT: This may be a pregnancy emergency. Please seek medical help immediately or dial 108 / call an ambulance without delay."
            
            return {
                "is_emergency": True,
                "warning": warning,
                "detected_symptom": flag
            }
    return None

def get_trimester_knowledge(week: int) -> str:
    if week <= 13:
        file = "trimester_1.json"
    elif week <= 26:
        file = "trimester_2.json"
    else:
        file = "trimester_3.json"

    knowledge_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "knowledge"))
    path = os.path.join(knowledge_dir, file)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return "Basic pregnancy knowledge."

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    # 1. Check Safety (Obstetric Emergency Escalation)
    safety_result = check_safety(request.message, request.language)
    if safety_result:
        return {
            "reply": safety_result["warning"],
            "safety_alert": True,
            "emergency_mode": True,
            "symptom": safety_result["detected_symptom"]
        }

    # 2. Load Knowledge (Offline RAG alternative)
    knowledge = get_trimester_knowledge(request.week)

    # 3. Create Prompt
    system_prompt = f"""You are Janani, a caring and expert pregnancy assistant.
The user is in Week {request.week} of pregnancy.
Reply clearly and concisely (2 to 3 sentences) strictly in {request.language}.
Medical Context: {knowledge}
Do not prescribe medicine. If unsure, advise consulting a doctor."""

    # 4. Call Local Ollama API (100% Offline, Optimized for Fast CPU Inference)
    try:
        ollama_res = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "qwen2.5:1.5b",
                "prompt": f"System: {system_prompt}\nUser: {request.message}\nAnswer:",
                "stream": False,
                "keep_alive": "60m",
                "options": {
                    "num_predict": 100,
                    "temperature": 0.35,
                    "num_ctx": 1024,
                    "num_thread": 4,
                },
            },
            timeout=60,
        )
        if ollama_res.status_code == 200:
            return {"reply": ollama_res.json()["response"]}
        return {"reply": "Sorry, local AI encountered an issue generating a response."}
    except requests.exceptions.Timeout:
        return {"reply": "Local AI is processing your request. Please ask a more concise question or try again."}
    except Exception as e:
        return {"reply": "Error connecting to local AI. Please ensure Ollama is running."}

if __name__ == "__main__":
    import uvicorn
    # Pass the app object so this works as `python backend/main.py`
    # (string "backend.main:app" fails because the script is not a package).
    uvicorn.run(app, host="127.0.0.1", port=8000)
