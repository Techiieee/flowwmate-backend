from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
import re
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

app = Flask(__name__)
CORS(app)

# -------------------------
# Load OpenAI Key
# -------------------------
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_KEY:
    print("❌ ERROR: OPENAI_API_KEY not found in environment variables.")
else:
    print("✅ OpenAI API key loaded.")

client = OpenAI(api_key=OPENAI_KEY)

# -------------------------
# JSON Extractor
# -------------------------
def extract_json(text):
    """Extract JSON from AI output safely."""
    try:
        match = re.search(r"\{[\s\S]*\}", text)
        if match:
            return json.loads(match.group())
    except Exception as e:
        print("⚠️ JSON parse error:", e)

    return {
        "agents": {
            "producer": ["Error generating tasks."],
            "administrator": [],
            "entrepreneur": [],
            "integrator": []
        }
    }

# -------------------------
# Generate Plan API
# -------------------------
@app.route("/api/generate-plan", methods=["POST"])
def generate_plan():
    try:
        data = request.json
        mood = data.get("mood", "")
        energy = data.get("energy", "")
        goal = data.get("goal", "")

        prompt = f"""
        You are FlowMate, an AI task planner.
        Based on the user's mood, energy, and today's goal,
        generate a structured PAEI plan.

        Provide ONLY valid JSON in this format:

        {{
          "agents": {{
            "producer": ["task 1", "task 2", "task 3"],
            "administrator": ["task 1", "task 2", "task 3"],
            "entrepreneur": ["task 1", "task 2", "task 3"],
            "integrator": ["task 1", "task 2", "task 3"]
          }}
        }}
        """

        print("\n🚀 Calling OpenAI GPT-4o-mini...\n")

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": f"Mood: {mood}, Energy: {energy}, Goal: {goal}"}
            ],
            temperature=0.6
        )

        raw_output = response.choices[0].message["content"]

        print("\n===== RAW OPENAI OUTPUT =====")
        print(raw_output)
        print("=============================\n")

        data = extract_json(raw_output)
        return jsonify(data)

    except Exception as e:
        print("\n🔥 ERROR in /api/generate-plan")
        print(str(e))
        print("=================================\n")

        return jsonify({
            "agents": {
                "producer": [f"Backend error: {str(e)}"],
                "administrator": [],
                "entrepreneur": [],
                "integrator": []
            }
        }), 500


# -------------------------
# Health Route
# -------------------------
@app.route("/", methods=["GET"])
def home():
    return "FlowMate OpenAI Backend Running OK"


# -------------------------
# Run
# -------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
