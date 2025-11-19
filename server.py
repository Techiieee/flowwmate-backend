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
    print("❌ ERROR: Gemini API Key missing!")
else:
    print("✅ Gemini key loaded.")

genai.configure(api_key=GEMINI_API_KEY)

# FIXED MODEL ID (this was the error)
model = genai.GenerativeModel("gemini-1.5-flash-latest")

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
You are FlowMate AI. Based on the user's mood, energy, and goal,
generate 3–5 short actionable suggestions for each PAEI role.

Return ONLY this JSON (no explanations):

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
            f"Mood: {mood}\nEnergy: {energy}\nGoal: {goal}\n\n{prompt}"
        )

        raw = response.text.strip()

        if raw.startswith("```"):
            raw = raw.replace("```json", "").replace("```", "").strip()

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
