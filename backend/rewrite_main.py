import os

main_path = r"c:\Users\BANVEN\Desktop\mediscan\backend\main.py"
with open(main_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

middle_part = "".join(lines[121:366])  # SYMPTOM_KEYWORDS through CONDITION_DESCRIPTIONS

top_replacement = """from __future__ import annotations
import json
import os
import pickle
import re
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
import numpy as np

# Load ML models
script_dir = os.path.dirname(os.path.abspath(__file__))
models_dir = os.path.join(script_dir, "models")

condition_model = None
triage_model = None
model_metadata = None

def load_models():
    global condition_model, triage_model, model_metadata
    try:
        with open(os.path.join(models_dir, "condition_model.pkl"), 'rb') as f:
            condition_model = pickle.load(f)
        with open(os.path.join(models_dir, "triage_model.pkl"), 'rb') as f:
            triage_model = pickle.load(f)
        with open(os.path.join(models_dir, "metadata.pkl"), 'rb') as f:
            model_metadata = pickle.load(f)
        print("Models loaded successfully")
    except Exception as e:
        print(f"Warning: Could not load models: {e}")

load_models()

TRIAGE_TITLES: dict[str, str] = {
    "home": "Home care likely appropriate",
    "doctor": "Consider seeing a clinician",
    "emergency": "Seek emergency care now",
}

TRIAGE_DESCS: dict[str, str] = {
    "home": "Your symptoms may be manageable with self-care. Monitor closely, and seek care if things worsen.",
    "doctor": "Your symptoms may warrant medical evaluation. If symptoms worsen or you feel unsafe, seek urgent care.",
    "emergency": "These symptoms could be serious. Consider emergency care, especially with chest pain, severe breathing trouble, fainting, confusion, or severe weakness.",
}

class PossibleCondition:
    def __init__(self, name: str, description: str, confidence: float):
        self.name = name
        self.description = description
        self.confidence = confidence

    def to_dict(self):
        return {"name": self.name, "description": self.description, "confidence": self.confidence}

def _ensure_models_loaded() -> None:
    if condition_model is None or triage_model is None or model_metadata is None:
        raise Exception("Local models are not loaded.")

"""

bottom_replacement = """
def _fallback_response() -> dict:
    return {
        "triageLevel": "doctor",
        "triageTitle": "Consider seeing a clinician",
        "triageDesc": "I couldn't safely complete an AI analysis right now. If symptoms are severe, worsening, or you're worried, seek medical advice.",
        "possibleConditions": [{"name": "Unable to analyze", "description": "AI service unavailable; please try again.", "confidence": 0.2}],
        "recommendedNextSteps": ["If you have severe symptoms, seek emergency care.", "Otherwise, consider contacting a healthcare professional."],
        "warningSigns": ["Trouble breathing", "Chest pain or pressure", "Blue lips/face", "Confusion or fainting", "Severe dehydration"],
        "followUpQuestions": ["Do you have a measured fever?", "Any chest pain, shortness of breath, or severe weakness?", "Any known medical conditions?", "Are symptoms getting worse quickly?"]
    }

def analyze_logic(req_data: dict) -> dict:
    _ensure_models_loaded()
    try:
        symptomsText = req_data.get("symptomsText", "")
        symptom_vector = extract_symptoms_from_text(symptomsText)
        if not symptom_vector or sum(symptom_vector) == 0:
            return {
                "triageLevel": "doctor",
                "triageTitle": TRIAGE_TITLES["doctor"],
                "triageDesc": "I couldn't confidently match your description to known symptom keywords. Try listing symptoms explicitly.",
                "possibleConditions": [],
                "recommendedNextSteps": ["If you have severe symptoms, seek emergency care.", "Otherwise, consider contacting a healthcare professional."],
                "warningSigns": ["Trouble breathing", "Chest pain", "Blue lips", "Confusion", "Severe dehydration"],
                "followUpQuestions": ["What are your top 3 symptoms?", "How long have you had these symptoms?", "Do you have a measured fever?"],
            }

        X = np.array([symptom_vector])
        triage_level = str(triage_model.predict(X)[0])
        possible_conditions = _top_conditions(symptom_vector, k=3)

        for pc in possible_conditions:
            if pc.name in ("Heart attack", "Paralysis (brain hemorrhage)"):
                triage_level = "emergency"
                break

        recommended_next_steps = {
            "home": ["Rest, hydrate, and monitor symptoms.", "If symptoms worsen, consider seeing a clinician."],
            "doctor": ["Consider booking an appointment with a clinician.", "Seek urgent care if symptoms worsen quickly."],
            "emergency": ["Seek emergency care now (local emergency number or nearest ER).", "If chest pain or breathing trouble: do not drive yourself."],
        }.get(triage_level, [])

        return {
            "triageLevel": triage_level,
            "triageTitle": TRIAGE_TITLES.get(triage_level, TRIAGE_TITLES["doctor"]),
            "triageDesc": TRIAGE_DESCS.get(triage_level, TRIAGE_DESCS["doctor"]),
            "possibleConditions": [pc.to_dict() for pc in possible_conditions],
            "recommendedNextSteps": recommended_next_steps,
            "warningSigns": ["Trouble breathing", "Chest pain or pressure", "Blue lips/face", "Confusion or fainting", "Severe dehydration", "New weakness on one side of the body"],
            "followUpQuestions": ["Do you have a measured fever?", "Any chest pain, shortness of breath, or severe weakness?", "Any known medical conditions?", "Are symptoms getting worse quickly?"]
        }
    except Exception as e:
        print("Analyze Error:", e)
        return _fallback_response()

def followup_logic(req_data: dict) -> dict:
    q = (req_data.get("question") or "").strip().lower()
    if not q:
        return {"answer": "Please type a follow-up question."}

    context = req_data.get("context", {})
    result = context.get("result", {})
    triage_level = str(result.get("triage", "doctor"))
    conditions = [c.get("name") for c in result.get("conditions", [])]

    answer = "I can provide general information based on your symptoms, but I cannot give a definitive medical diagnosis. "
    
    if "medicine" in q or "medication" in q or "pill" in q or "treatment" in q:
        answer += "For over-the-counter treatments, consider pain relievers (like ibuprofen or acetaminophen) for fever/pain. However, it's best to consult a pharmacist or doctor for specific medication advice."
    elif "how long" in q or "duration" in q:
        answer += "Symptom duration varies by condition. Minor viral infections often improve in 3-7 days. If your symptoms persist beyond a week, or worsen significantly, please see a healthcare provider."
    elif "contagious" in q or "spread" in q:
        answer += "If you suspect an infectious condition (like a cold, flu, or gastroenteritis), it's best to practice good hygiene: wash your hands frequently and consider wearing a mask if around others."
    elif "doctor" in q or "hospital" in q or "when to go" in q:
        if triage_level == "emergency":
            answer += "Your symptoms suggest you should seek EMERGENCY care immediately. Do not wait."
        elif triage_level == "doctor":
            answer += "You should aim to see a doctor soon, ideally within the next 24-48 hours, depending on how you feel."
        else:
            answer += "Since your symptoms seem manageable at home, you only need to see a doctor if they don't improve in a few days, or if new, severe symptoms develop."
    elif conditions and any(c.lower() in q for c in conditions):
        answer += f"Regarding the possible conditions mentioned earlier, a healthcare provider can run appropriate tests to confirm or rule them out."
    else:
        if triage_level == "emergency":
            answer += "Because your symptoms are flagged as high risk, please prioritize seeking emergency medical attention over further self-analysis."
        elif triage_level == "doctor":
            answer += "Consider booking an appointment with a clinician to discuss your concerns in detail."
        else:
            answer += "Monitor your symptoms closely. Rest, stay hydrated, and seek care if things get worse."

    return {"answer": answer}

class RequestHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200, "ok")
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header("Access-Control-Allow-Headers", "X-Requested-With, Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == "/health":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"ok": True}).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        parsed_path = urlparse(self.path)
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            req_json = json.loads(post_data.decode('utf-8'))
        except:
            req_json = {}

        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        if parsed_path.path == "/api/analyze":
            resp_data = analyze_logic(req_json)
        elif parsed_path.path == "/api/followup":
            resp_data = followup_logic(req_json)
        else:
            self.send_response(404)
            return

        self.wfile.write(json.dumps(resp_data).encode("utf-8"))

def run_server():
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, RequestHandler)
    print("Backend running on http://127.0.0.1:8000")
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()
"""

new_content = top_replacement + middle_part + bottom_replacement

with open(main_path, "w", encoding="utf-8") as f:
    f.write(new_content)

print("Rewrote main.py successfully!")
