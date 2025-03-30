from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import pandas as pd

app = Flask(__name__)

# Load the tire data
df = pd.read_csv("movies_data.csv")  # using the tire data renamed to this

# In-memory session state
user_sessions = {}

@app.route("/bot", methods=["POST"])
def bot():
    user_number = request.form.get("From", "")
    incoming_msg = request.form.get("Body", "").strip().lower()

    resp = MessagingResponse()
    msg = resp.message()

    # First-time user setup
    if user_number not in user_sessions:
        user_sessions[user_number] = {"active": True}

    session = user_sessions[user_number]

    if incoming_msg == "exit":
        session["active"] = False
        msg.body("👋 Session ended. Type 'start' anytime to begin again.")
        return str(resp)

    if incoming_msg == "start":
        session["active"] = True
        # Format and show tire data
        replies = []
        for _, row in df.iterrows():
            report = (
                f"📍 *{row['Truck']} Status Report*\n\n"
                f"🛞 *Tire:* {row['Tire']}\n"
                f"🔧 Pressure: {row['Pressure']} | Tread: {row['Tread']}\n"
                f"⚙️ Inflation System: {row['Inflation System']}\n"
                f"📅 Installed: {row['Installed']}\n\n"
                f"⛽ Fuel Efficiency: {row['Fuel Efficiency']}\n"
                f"🚛 Load: {row['Load']}\n"
                f"🛣️ Distance Covered Today: {row['Distance Today']}\n"
                f"🕒 Engine Hours: {row['Engine Hours']}\n\n"
                f"📌 Current Location: {row['Location']}\n"
                f"📍 Heading To: {row['Heading To']}\n"
                f"🕓 ETA: {row['ETA']}\n\n"
                f"🧰 Last Service: {row['Last Service']}\n"
                f"🗓️ Next Service Due: {row['Next Service']}\n"
                f"💬 Status: {row['Status']}\n"
            )
            replies.append(report)

        full_reply = "\n------------------------\n".join(replies)
        msg.body(full_reply[:1600])  # SMS/WhatsApp limit
        msg.body("✅ Type *exit* to stop or *start* again to reload reports.")
        return str(resp)

    # If not started yet
    if not session.get("active", False):
        return ("", 204)  # No reply

    # If message doesn't match any known command
    msg.body("⚙️ Type *start* to begin or *exit* to stop.")
    return str(resp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
