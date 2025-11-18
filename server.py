from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# DeepSeek API Client
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

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
        You are FlowMate AI. Based on user's mood, energy level, and goal,
        generate 3–5 short actionable suggestions for each PAEI role.

        P – Producer → work tasks related to the goal  
        A – Administrator → routine/admin tasks  
        E – Entrepreneur → creative/idea tasks  
        I – Integrator → self-care/social balance tasks  

        Respond ONLY in valid JSON:
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
            temperature=0.7
        )

        raw = response.choices[0].message.content.strip()

        # Convert DeepSeek's JSON string to Python dict
        result = eval(raw)

        return jsonify(result)

    except Exception as e:
        print("Error:", e)
        # Safe fallback
        return jsonify({
            "agents": {
                "producer": ["Error generating tasks."],
                "administrator": [],
                "entrepreneur": [],
                "integrator": []
            }
        }), 500


@app.route("/", methods=["GET"])
def home():
    return "FlowMate DeepSeek Backend Running"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

