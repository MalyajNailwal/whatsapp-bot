from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import pandas as pd

app = Flask(__name__)

@app.route("/bot", methods=["POST"])
def bot():
    print("📥 Received POST /bot")
    try:
        incoming_msg = request.form.get("Body", "").strip().lower()
        print("💬 User said:", incoming_msg)

        df = pd.read_csv("movies_data.csv")
        matched = df[df['Title'].str.lower() == incoming_msg]

        resp = MessagingResponse()
        msg = resp.message()

        if not matched.empty:
            m = matched.iloc[0]
            reply = (
                f"*{m['Title']}* ({m['Year']})\n"
                f"Directed by: {m['Director']}\n"
                f"Genre: {m['Genre']}\n"
                f"Synopsis: {m['Synopsis']}"
            )
        else:
            reply = "❌ Movie not found. Try again."

        msg.body(reply)
        return str(resp)

    except Exception as e:
        print("❌ ERROR:", e)
        return "Internal Server Error", 500

if __name__ == "__main__":
    print("🚀 Running Flask bot...")
    app.run(host="0.0.0.0", port=5000)

