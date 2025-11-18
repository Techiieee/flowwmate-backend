from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import os
import json
import re
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# -------------------------
# Load API Key
# -------------------------
DEEPSEEK_KEY = os.getenv("DEEPSEEK_API_KEY")

if not DEEPSEEK_KEY:
    print("❌ ERROR: DeepSeek API key not found in environment variables.")
else:
    print("✅ DeepSeek key loaded.")

client = OpenAI(
    api_key=DEEPSEEK_KEY,
    base_url="https://api.deepseek.com"
)

# -------------------------
# JSON Extractor
# -------------------------
def extract_json(text):
    """Extracts first valid JSON object from raw model output."""
    try:
        # Find JSON-like structure
        match = re.search(r"\{[\s\S]*\}", text)
        if match:
            return json.loads(match.group())
    except Exception as e:
        print("⚠️ JSON parse error:", e)

    # fallback structure
    return {
        "agents": {
            "producer": ["Error generating tasks."],
            "administrator": [],
            "entrepreneur": [],
            "integrator": []
        }
    }

# -------------------------
# Generate Plan Endpoint
# -------------------------
@app.route("/api/generate-plan", methods=["POST"])
def generate_plan():
    try:
        data = request.json
        mood = data.get("mood", "")
        energy = data.get("energy", "")
        goal = data.get("goal", "")

        prompt = f"""
        You are FlowMate AI. Based on user's mood, energy, and today's goal,
        generate a PAEI task plan.

        The response MUST BE valid JSON:

        {{
          "agents": {{
            "producer": [...],
            "administrator": [...],
            "entrepreneur": [...],
            "integrator": [...]
          }}
        }}
        """

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": f"Mood: {mood}, Energy: {energy}, Goal: {goal}"}
            ],
            temperature=0.6
        )

        print("\n\n===== RAW API OBJECT =====")
        print(response)
        print("==========================\n\n")

        # Support both response styles
        if hasattr(response.choices[0].message, "content"):
            raw_output = response.choices[0].message.content
        else:
            raw_output = response.choices[0].text

        print("\n\n===== RAW DEEPSEEK OUTPUT =====")
        print(raw_output)
        print("================================\n\n")

        result = extract_json(raw_output)
        return jsonify(result)

    except Exception as e:
        print("\n🔥 ERROR in /api/generate-plan")
        print(str(e))
        print("================================\n")
        return jsonify({
            "agents": {
                "producer": [f"Backend error: {str(e)}"],
                "administrator": [],
                "entrepreneur": [],
                "integrator": []
            }
        }), 500


# -------------------------
# Root Test Route
# -------------------------
@app.route("/", methods=["GET"])
def home():
    return "FlowMate DeepSeek Backend Running OK"


# -------------------------
# Run App
# -------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
