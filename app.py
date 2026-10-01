import os

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from google import genai

from chatbot_config import SYSTEM_PROMPT, CHATBOT_TITLE

load_dotenv()

app = Flask(__name__)

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = "gemini-3.1-flash-lite"

if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not configured.")

client = genai.Client(api_key=API_KEY)


@app.route("/")
def index():
    return render_template("index.html", chatbot_title=CHATBOT_TITLE)


@app.post("/chat")
def chat():
    data = request.get_json(silent=True) or {}
    user_message = (data.get("message") or "").strip()

    if not user_message:
        return jsonify({"error": "Please enter a question."}), 400

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=f"{SYSTEM_PROMPT}\n\nStudent question:\n{user_message}",
        )

        answer = (response.text or "").strip()
        if not answer:
            answer = "I couldn't generate an answer right now."

        return jsonify({"answer": answer})

    except Exception:
        return jsonify({
            "error": "Unable to generate the answer right now. Please try again."
        }), 500


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=False)
