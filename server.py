from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import os
from dotenv import load_dotenv
import json

load_dotenv()

app = Flask(__name__)
CORS(app)

# -----------------------------
# Configure Gemini API
# -----------------------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("❌ ERROR: Gemini API Key missing in environment variables!")
else:
    print("✅ Gemini key loaded.")

genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-1.5-flash")


# -----------------------------
# Generate Plan Endpoint
# -----------------------------
@app.route("/api/generate-plan", methods=["POST"])
def generate_plan():
    try:
        data = request.json
        mood = data.get("mood", "")
        energy = data.get("energy", "")
        goal = data.get("goal", "")

        prompt = f"""
You are FlowMate AI. Based on the user's mood, energy level, and daily goal,
generate 3–5 short actionable suggestions for each PAEI role.

PAEI ROLES:
- Producer → work tasks related to goal
- Administrator → routine/admin tasks
- Entrepreneur → creative/idea tasks
- Integrator → self-care/social balance tasks

Return ONLY a VALID JSON object like:
{{
  "agents": {{
    "producer": ["...", "..."],
    "administrator": ["...", "..."],
    "entrepreneur": ["...", "..."],
    "integrator": ["...", "..."]
  }}
}}
"""

        response = model.generate_content(
            [
                {"role": "user", "parts": [{"text": f"Mood: {mood}, Energy: {energy}, Goal: {goal}"}]},
                {"role": "system", "parts": [{"text": prompt}]}
            ]
        )

        raw = response.text.strip()

        # Gemini sometimes returns in a code block → clean it
        if raw.startswith("```"):
            raw = raw.strip("```json").strip("```")

        result = json.loads(raw)

        return jsonify(result)

    except Exception as e:
        print("Backend Error:", e)
        return jsonify({
            "agents": {
                "producer": [f"Backend error: {str(e)}"],
                "administrator": [],
                "entrepreneur": [],
                "integrator": []
            }
        }), 500


@app.route("/", methods=["GET"])
def home():
    return "🌸 FlowMate Gemini Backend Running!"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
