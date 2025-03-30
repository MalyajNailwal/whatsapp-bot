from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import pandas as pd

app = Flask(__name__)

# Load tire data
df = pd.read_csv("tire_data.csv")

# In-memory session storage
user_sessions = {}

@app.route("/bot", methods=["POST"])
def bot():
    user_number = request.form.get("From", "")
    incoming_msg = request.form.get("Body", "").strip().lower()

    print("📥 FROM:", user_number)
    print("💬 MSG:", incoming_msg)

    resp = MessagingResponse()
    msg = resp.message()

    # New session
    if user_number not in user_sessions:
        user_sessions[user_number] = {"active": True}

    session = user_sessions[user_number]

    # Exit command
    if incoming_msg == "exit":
        session["active"] = False
        msg.body("👋 Session ended. Type *start* anytime to begin again.")
        print("📤 Sending: Session ended message")
        return str(resp)

    # Start command
    if incoming_msg == "start":
        session["active"] = True

        replies = []
        for _, row in df.head(2).iterrows():  # only send 2 for now
            report = (
                f"📍 *{row['Truck']} Status Report*\n\n"
                f"🛞 *Tire:* {row['Tire']}\n"
                f"🔧 Pressure: {row['Pressure']} | Tread: {row['Tread']}\n"
                f"⚙️ Inflation System: {row['Inflation System']}\n"
                f"📅 Installed: {row['Installed']}\n\n"
                f"⛽ Fuel Efficiency: {row['Fuel Efficiency']}\n"
                f"🚛 Load: {row['Load']}\n"
                f"🛣️ Distance Today: {row['Distance Today']}\n"
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
        print("📤 Sending tire report:")
        print(full_reply[:100] + "...")  # show start of message in logs

        msg.body(full_reply[:1600])  # cap it under WhatsApp limit
        msg.body("✅ Type *exit* to stop or *start* again to reload reports.")
        return str(resp)

    # If session is inactive
    if not session.get("active", False):
        print("🚫 Inactive session - no reply sent")
        return ("", 204)

    # Invalid command
    msg.body("⚙️ Invalid input. Type *start* to begin or *exit* to stop.")
    print("📤 Sending: Invalid input message")
    return str(resp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
