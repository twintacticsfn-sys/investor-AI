import os
from flask import Flask, render_template, request, jsonify
from openai import OpenAI

app = Flask(__name__)

def get_client():
    return OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

SYSTEM_PROMPT = """You are Penny, a fun and friendly AI money coach for kids and beginners!
You use simple words, emojis, and fun examples to explain money and investing.
You talk like a cool friend, not a boring teacher.

You help with:
- What is money and how it grows 💰
- Saving vs spending
- What stocks, ETFs, and investing mean in simple terms
- Fun ways to think about building wealth
- Answering any question a curious kid or beginner might have

Rules:
- Always use emojis to make it fun 🎉
- Use simple everyday examples (like pizza, video games, lemonade stands)
- Be encouraging and positive
- Keep answers short and easy to understand
- If someone just wants to chat, chat with them! Be friendly and fun.
- Remind users this is for learning, not real financial advice."""

conversation_history = []

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message", "")
    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    conversation_history.append({"role": "user", "content": user_message})

    try:
        client = get_client()
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + conversation_history,
            max_tokens=500,
            temperature=0.7
        )
        reply = response.choices[0].message.content
        conversation_history.append({"role": "assistant", "content": reply})
        return jsonify({"reply": reply})
    except Exception as e:
        conversation_history.pop()  # remove the failed user message
        return jsonify({"error": f"API error: {str(e)}"}), 500

@app.route("/reset", methods=["POST"])
def reset():
    conversation_history.clear()
    return jsonify({"status": "reset"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
