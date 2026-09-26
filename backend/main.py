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


# PHASE 3: COMPREHENSIVE OBSTETRIC EMERGENCY SAFETY LAYER (ALL 8 REGIONAL LANGUAGES)
RED_FLAGS = [
    # Hemorrhage & Bleeding
    "bleeding", "heavy bleeding", "blood", "spotting with pain", "blood clot", "hemorrhage",
    "రక్తం", "రక్తస్రావం", "raktham", "rakthasravam", "khoon", "खून", "रक्तस्राव",
    "இரத்தப்போக்கு", "ரத்தம்", "ರಕ್ತಸ್ರಾವ", "രക്തസ്രാവം", "রক্তপাত", "রক্তস্রাব",
    
    # Severe Abdominal & Pelvic Pain
    "severe pain", "sharp pain", "severe cramp", "stomach pain", "abdominal pain", "pelvic pain",
    "unbearable pain", "నొప్పి", "తీవ్రమైన నొప్పి", "noppi", "dard", "दर्द", "पेट दर्द", "तेज दर्द",
    "கடுமையான வலி", "வயிறு வலி", "ತೀವ್ರ ಹೊಟ್ಟೆ ನೋವು", "കഠിനമായ വയറുവേദന", "तीव्र पोटदुखी", "তীব্র পেটে ব্যথা",
    
    # Respiratory & Cardiovascular
    "difficulty breathing", "shortness of breath", "chest pain", "breathless", "cannot breathe",
    "ఊపిరి", "ఊపిరి ఆడకపోవడం", "saans", "साँस", "सीने में दर्द",
    "மூச்சுத்திணறல்", "ಉಸಿರಾಟದ ತೊಂದರೆ", "ശ്വാസമെടുക്കാൻ ബുദ്ധിമുട്ട്", "श्वास घेण्यास त्रास", "শ্বাসকষ্ট",
    
    # Neurological & Consciousness
    "seizure", "convulsion", "fit", "fainted", "fainting", "passed out", "unconscious", "loss of consciousness", "collapsed",
    "స్పృహ", "స్పృహ తప్పడం", "spruha", "behoshi", "behos", "बेहोश", "दौरा", "fits",
    "மயக்கம்", "ಪ್ರಜ್ಞೆ ತಪ್ಪುವುದು", "ബോധക്ഷയം", "भवळणे", "অজ্ঞান",
    
    # Preeclampsia / Vision / Severe Headache
    "vision change", "blurred vision", "flashing light", "severe headache", "extreme headache", "high bp", "swollen face",
    "కళ్ళు తిరగడం", "తలనొప్పి", "dhundhla", "धुंधला", "सिरदर्द",
    "பார்வை மங்குதல்", "தలనొప్పి", "ತಲೆನೋವು", "തലവേദന", "डोकेदुखी", "তীব্র মাথাব্যথা",
    
    # Amniotic Fluid / Water Break
    "leaking fluid", "water broke", "water break", "amniotic fluid", "water leakage", "leaking water",
    "ఉమ్మనీరు", "ummaneeru", "pani", "पानी छूटना",
    "பனிக்குடம் உடைதல்", "ನೀರು ಸೋರುವುದು", "പനിമീൻ പൊട്ടൽ", "पाणी गळणे", "জল ভাঙা",
    
    # Fetal Movement Reduction
    "baby not moving", "no movement", "less movement", "reduced movement", "no kicks", "stopped moving",
    "కదలికలు లేవు", "kadalikalu", "bacha hil", "बच्चा हिल नहीं रहा", "हलचल बंद",
    "குழந்தை அசைவு இல்லை", "ಮಗುವಿನ ಚಲನೆ ಇಲ್ಲ", "കുഞ്ഞിൻ്റെ അനക്കമില്ല", "हालचाल कमी", "বাচ্চার নড়াচড়া বন্ধ",
    
    # General Emergencies
    "miscarriage", "emergency", "urgent hospital", "danger", "ఆపద", "అత్యవసరం", "आपातकाल", "खतरा",
    "அவசரம்", "ತುರ್ತು", "അടിയന്തരം", "आणीबाणी", "জরুরী"
]

def check_safety(message: str, language: str) -> dict:
    msg_lower = message.lower()
    for flag in RED_FLAGS:
        if flag.lower() in msg_lower:
            lang = language.lower()
            if "telugu" in lang:
                warning = "⚠️ అత్యవసర హెచ్చరిక: ఇది గర్భధారణ అత్యవసర పరిస్థితి కావచ్చు. దయచేసి ఆలస్యం చేయకుండా వెంటనే సమీపంలోని ఆసుపత్రికి వెళ్ళండి లేదా 108 అంబులెన్స్‌ను సంప్రదించండి."
            elif "hindi" in lang:
                warning = "⚠️ आपातकालीन चेतावनी: यह गर्भावस्था की गंभीर स्थिति हो सकती है। कृपया तुरंत नजदीकी अस्पताल जाएँ या 108 एम्बुलेंस से संपर्क करें।"
            elif "tamil" in lang:
                warning = "⚠️ அவசர எச்சரிக்கை: இது அவசர கர்ப்பகால நிலையாக இருக்கலாம். தாமதிக்காமல் உடனடியாக அருகிலுள்ள மருத்துவமனைக்கு செல்லவும் அல்லது 108 ஆம்புலன்ஸை அழைக்கவும்."
            elif "kannada" in lang:
                warning = "⚠️ ತುರ್ತು ಎಚ್ಚರಿಕೆ: ಇದು ಗರ್ಭಧಾರಣೆಯ ತುರ್ತು ಪರಿಸ್ಥಿತಿಯಾಗಿರಬಹುದು. ದಯವಿಟ್ಟು ವಿಳಂಬವಿಲ್ಲದೆ ತಕ್ಷಣ ಹತ್ತಿರದ ಆಸ್ಪತ್ರೆಗೆ ಹೋಗಿ ಅಥವಾ 108 ಆಂಬ್ಯುಲೆನ್ಸ್‌ಗೆ ಕರೆ ಮಾಡಿ."
            elif "malayalam" in lang:
                warning = "⚠️ അടിയന്തര മുന്നറിയിപ്പ്: ഇത് ഗർഭകാല അടിയന്തരാവസ്ഥയാകാം. ഒട്ടും വൈകാതെ അടുത്തുള്ള ആശുപത്രിയിൽ എത്തുകയോ 108 ആംബുലൻസ് വിളിക്കുകയോ ചെയ്യുക."
            elif "marathi" in lang:
                warning = "⚠️ तातडीची सूचना: ही गर्भधारणेतील गंभीर आणीबाणी असू शकते. कृपया विलंब न करता त्वरित जवळच्या रुग्णालयात जा किंवा 108 रुग्णवाहिकेला कॉल करा."
            elif "bengali" in lang:
                warning = "⚠️ জরুরী সতর্কতা: এটি একটি গর্ভকালীন জরুরী পরিস্থিতি হতে পারে। অবিলম্বে নিকটস্থ হাসপাতালে যান বা ১০৮ অ্যাম্বুলেন্সে যোগাযোগ করুন।"
            else:
                warning = "⚠️ MEDICAL EMERGENCY ALERT: This may be a pregnancy emergency. Please seek medical help immediately or dial 108 / call an ambulance without delay."
            
            return {
                "is_emergency": True,
                "warning": warning,
                "detected_symptom": flag
            }
    return None

def get_traditional_gender_reply(language: str) -> str:
    lang = language.lower()
    disclaimer = "Fun prediction only — this traditional calendar method is not scientifically proven and cannot determine biological sex. For medically relevant information, consult a qualified healthcare professional."
    
    if "telugu" in lang:
        return (
            "🔮 సాంప్రదాయ లింగ అంచనా:\n"
            "సాంప్రదాయ క్యాలెండర్ విధానం అనేది గర్భధారణ సమయంలో తల్లి వయస్సు మరియు గర్భం దాల్చిన నెలను ఆధారం చేసుకుని రూపొందించబడిన సాంప్రదాయ చార్ట్. చాలామంది దీనిని కేవలం ఉత్సాహం మరియు సరదా కోసం పరిశీలిస్తారు.\n\n"
            "⚠️ వైద్య హెచ్చరిక:\n"
            "వినోదం కోసం సాంప్రదాయ అంచనా మాత్రమే — ఇది శాస్త్రీయంగా నిరూపించబడిన పద్ధతి కాదు మరియు జీవ లింగాన్ని నిర్ధారించలేదు. వైద్యపరమైన సమాచారం కోసం అర్హత కలిగిన వైద్యుడిని సంప్రదించండి.\n\n"
            "మీరు మీ డ్యాష్‌బోర్డ్‌లోని 'సాంప్రదాయ అంచనా' కార్డు ద్వారా స్వయంగా ప్రయత్నించవచ్చు!"
        )
    elif "hindi" in lang:
        return (
            "🔮 पारंपरिक लिंग अनुमान:\n"
            "पारंपरिक कैलेंडर पद्धति गर्भाधान के समय माँ की आयु और गर्भाधान के महीने पर आधारित एक प्राचीन सांस्कृतिक पद्धति है। कई परिवार इसे केवल जिज्ञासा और मनोरंजन के लिए देखते हैं।\n\n"
            "⚠️ चिकित्सकीय अस्वीकरण:\n"
            "केवल मनोरंजन हेतु पारंपरिक अनुमान — यह कैलेंडर पद्धति वैज्ञानिक रूप से सिद्ध नहीं है और जैविक लिंग का निर्धारण नहीं कर सकती। चिकित्सकीय जानकारी के लिए योग्य डॉक्टर से परामर्श लें।\n\n"
            "आप अपने डैशबोर्ड पर 'पारंपरिक लिंग भविष्यवक्ता' कार्ड में इसे आज़मा सकते हैं!"
        )
    elif "tamil" in lang:
        return (
            "🔮 பாரம்பரிய பாலின கணிப்பு:\n"
            "கருத்தரித்த போது தாயின் வயது மற்றும் கருத்தரித்த மாதத்தை அடிப்படையாகக் கொண்டு கணிக்கப்படும் ஒரு பாரம்பரிய முறை இதுவாகும்.\n\n"
            "⚠️ மருத்துவ மறுப்புரை:\n"
            "சுவாரசியத்திற்கான பாரம்பரிய கணிப்பு மட்டுமே — இந்த பாரம்பரிய காலண்டர் முறை அறிவியல் பூர்வமாக நிரூபிக்கப்படவில்லை. மருத்துவ ஆலோசனைக்கு மருத்துவரை அணுகவும்."
        )
    elif "kannada" in lang:
        return (
            "🔮 ಸಾಂಪ್ರದಾಯಿಕ ಲಿಂಗ ಊಹೆ:\n"
            "ಗರ್ಭಧಾರಣೆಯ ಸಮಯದಲ್ಲಿ ತಾಯಿಯ ವಯಸ್ಸು ಮತ್ತು ತಿಂಗಳನ್ನು ಆಧರಿಸಿದ ಪ್ರಾಚೀನ ಸಾಂಸ್ಕೃತಿಕ ಕ್ಯಾಲೆಂಡರ್ ವಿಧಾನವಿದು.\n\n"
            "⚠️ ವೈದ್ಯಕೀಯ ಹಕ್ಕುತ್ಯಾಗ:\n"
            "ಕೇವಲ ಮನರಂಜನೆಯ ಸಾಂಪ್ರದಾಯಿಕ ಊಹೆ — ಈ ಕ್ಯಾಲೆಂಡರ್ ವಿಧಾನವು ವೈಜ್ಞಾನಿಕವಾಗಿ ಸಾಬೀತಾಗಿಲ್ಲ. ವೈದ್ಯಕೀಯ ಮಾಹಿತಿಗಾಗಿ ನುರಿತ ವೈದ್ಯರನ್ನು ಸಂಪರ್ಕಿಸಿ."
        )
    elif "malayalam" in lang:
        return (
            "🔮 പരമ്പരാഗത ലിംഗ പ്രവചനം:\n"
            "ഗർഭധാരണ സമയത്തെ അമ്മയുടെ പ്രായവും മാസവും അടിസ്ഥാനമാക്കിയുള്ള ഒരു പരമ്പരാഗത കലണ്ടർ രീതിയാണിത്.\n\n"
            "⚠️ മെഡിക്കൽ മുന്നറിയിപ്പ്:\n"
            "വിനോദത്തിനായുള്ള പരമ്പരാഗത പ്രവചനം മാത്രം — ഇത് ശാസ്ത്രീയമായി തെളിയിക്കപ്പെട്ടതല്ല. വൈദ്യോപദേശത്തിന് ഡോക്ടറെ സമീപിക്കുക."
        )
    elif "marathi" in lang:
        return (
            "🔮 पारंपारिक लिंग अंदाज:\n"
            "गर्भधारणेच्या वेळी मातेचे वय आणि महिना यावर आधारित ही एक पारंपारिक कॅलेंडर पद्धत आहे.\n\n"
            "⚠️ वैद्यकीय अस्वीकरण:\n"
            "केवळ मनोरंजनासाठी पारंपारिक अंदाज — ही पद्धत वैज्ञानिकदृष्ट्या सिद्ध झालेली नाही. वैद्यकीय माहितीसाठी डॉक्टरांचा सल्ला घ्या."
        )
    elif "bengali" in lang:
        return (
            "🔮 ঐতিহ্যবাহী লিঙ্গ পূর্বাভাস:\n"
            "গর্ভধারণের সময় মায়ের বয়স এবং মাসের ওপর ভিত্তি করে এটি একটি ঐতিহ্যবাহী গণনা পদ্ধতি।\n\n"
            "⚠️ চিকিৎসা দাবিত্যাগ:\n"
            "শুধুমাত্র মজার জন্য ঐতিহ্যবাহী পূর্বাভাস — এই ঐতিহ্যবাহী পদ্ধতিটি বৈজ্ঞানিকভাবে প্রমাণিত নয়। সঠিক চিকিৎসা তথ্যের জন্য ডাক্তারের পরামর্শ নিন।"
        )
    return (
        "🔮 Traditional Gender Predictor:\n"
        "The traditional gender prediction method is an ancient calendar-based chart calculated from the mother's age at conception and the conception month. Many parents explore it purely for fun and cultural curiosity.\n\n"
        f"⚠️ Important Medical Disclaimer:\n{disclaimer}\n\n"
        "You can explore the interactive Traditional Gender Predictor card right below on your pregnancy dashboard!"
    )

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
    return "Basic pregnancy knowledge: nutrition, rest, hydration, prenatal vitamins, and regular checkups."

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

    # 2. Check for Traditional Gender Predictor inquiries
    msg_low = request.message.lower()
    gender_inquiry_keywords = [
        "gender", "predictor", "prediction", "boy or girl", "traditional prediction",
        "conception month", "chinese gender", "predict using my age", "what is this prediction",
        "లింగ", "అంచనా", "సాంప్రదాయ", "लिंग", "भविष्यवाणी", "பாலினம்", "கணிப்பு",
        "ಲಿಂಗ", "ಊಹೆ", "പ്രവചനം", "অন্দাজ", "পূর্বাভাস"
    ]
    if any(k in msg_low for k in gender_inquiry_keywords):
        return {
            "reply": get_traditional_gender_reply(request.language),
            "safety_alert": False,
            "is_gender_prediction_query": True
        }

    # 3. Load Knowledge (Offline RAG)
    knowledge = get_trimester_knowledge(request.week)

    # 4. Create Prompt with strict maternal guidelines
    system_prompt = f"""You are Janani, a caring, expert pregnancy and maternal care assistant.
The user is currently in Week {request.week} of pregnancy.
Reply clearly, kindly, and concisely (2 to 3 sentences) strictly in {request.language}.
Medical Context: {knowledge}
Never prescribe prescription medicines. If unsure or if symptoms seem unusual, advise consulting an OB-GYN doctor.
If discussing traditional predictions or cultural lore, always specify that it is for fun and not a medical diagnostic tool."""

    # 5. Call Local Ollama API (100% Offline, Fast CPU Inference)
    try:
        ollama_res = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "qwen2.5:1.5b",
                "prompt": f"System: {system_prompt}\nUser: {request.message}\nAnswer:",
                "stream": False,
                "keep_alive": "60m",
                "options": {
                    "num_predict": 120,
                    "temperature": 0.35,
                    "num_ctx": 1024,
                    "num_thread": 4,
                },
            },
            timeout=25,
        )
        if ollama_res.status_code == 200:
            return {"reply": ollama_res.json()["response"]}
    except Exception:
        pass

    # High-quality offline fallback synthesized from trimester knowledge base
    fallback_replies = {
        "telugu": f"నమస్కారం! గర్భధారణ వారం {request.week} లో మీ శరీరంలో మరియు శిశువు పెరుగుదలలో ఎన్నో ముఖ్యమైన మార్పులు జరుగుతాయి. సమతుల్య పోషకాహారం, తగినంత నీరు మరియు వైద్యుల పర్యవేక్షణ చాలా ముఖ్యం.",
        "hindi": f"नमस्ते! गर्भावस्था के सप्ताह {request.week} में शिशु का विकास निरंतर जारी रहता है। पौष्टिक आहार, पर्याप्त पानी और नियमित डॉक्टर जांच का ध्यान रखें।",
        "tamil": f"வணக்கம்! கர்ப்பத்தின் {request.week} வது வாரத்தில் குழந்தையின் வளர்ச்சி சீராக நடைபெறுகிறது. சத்தான உணவு மற்றும் வழக்கமான மருத்துவ ஆலோசனையைப் பெறவும்.",
        "kannada": f"ನಮಸ್ಕಾರ! ಗರ್ಭಧಾರಣೆಯ {request.week} ನೇ ವಾರದಲ್ಲಿ ಮಗುವಿನ ಬೆಳವಣಿಗೆ ವೇಗವಾಗಿರುತ್ತದೆ. ಪೌಷ್ಟಿಕ ಆಹಾರ ಮತ್ತು ವಿಶ್ರಾಂತಿಯನ್ನು ಕಾಪಾಡಿಕೊಳ್ಳಿ.",
        "malayalam": f"നമസ്കാരം! ഗർഭധാരണത്തിൻ്റെ {request.week}-ാം ആഴ്ചയിൽ പോഷകസമൃദ്ധമായ ഭക്ഷണവും ആവശ്യത്തിന് വിശ്രമവും ഉറപ്പാക്കുക.",
        "marathi": f"नमस्कार! गर्भधारणेच्या आठवडा {request.week} मध्ये योग्य पोषण, भरपूर पाणी आणि डॉक्टरांचा नियमित सल्ला अत्यंत आवश्यक आहे.",
        "bengali": f"নমস্কার! গর্ভাবস্থার {request.week} তম সপ্তাহে সুষম পুষ্টিকর খাবার, প্রচুর জল পান এবং নিয়মিত চিকিৎসকের পরামর্শ বজায় রাখুন।",
        "english": f"Hello! At Week {request.week} of pregnancy, your body is supporting crucial baby development. Prioritize balanced nutrition, hydration (8-10 glasses daily), rest, and regular prenatal checkups."
    }
    
    lang_key = "english"
    for lk in fallback_replies:
        if lk in request.language.lower():
            lang_key = lk
            break
            
    return {"reply": fallback_replies[lang_key]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
