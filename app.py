from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import pandas as pd
import os

app = Flask(__name__)

# Load tire data
df = pd.read_csv("tire_data.csv")
df.columns = df.columns.str.strip()

# Sessions
user_sessions = {}

@app.route("/bot", methods=["POST"])
def bot():
    incoming_msg = request.form.get("Body", "").strip().lower()
    user_number = request.form.get("From", "")
    print(f"📨 {user_number}: {incoming_msg}")

    resp = MessagingResponse()
    msg = resp.message()

    # Set up session
    if user_number not in user_sessions:
        user_sessions[user_number] = {"step": "start"}
    session = user_sessions[user_number]

    # 🔄 Restart
    if incoming_msg == "restart":
        locations = sorted(df["Location"].dropna().unique())
        user_sessions[user_number] = {
            "step": "choose_location",
            "locations": locations
        }
        session = user_sessions[user_number]
        loc_text = "\n".join([f"{i+1}. {loc}" for i, loc in enumerate(locations)])
        msg.body(
            f"🔄 *Session restarted!*\n\n"
            f"📍 *Choose a Location:*\n\n{loc_text}\n\n✍️ Reply with a number (e.g., 1)"
        )
        return str(resp)

    # ▶️ Start
    if incoming_msg == "start":
        locations = sorted(df["Location"].dropna().unique())
        session["step"] = "choose_location"
        session["locations"] = locations
        loc_text = "\n".join([f"{i+1}. {loc}" for i, loc in enumerate(locations)])
        msg.body(
            f"📍 *Select a Location:*\n\n{loc_text}\n\n✍️ Reply with a number (e.g., 1)"
        )
        return str(resp)

    # 🔙 Back
    if incoming_msg == "back":
        if "locations" in session:
            session["step"] = "choose_location"
            loc_text = "\n".join([f"{i+1}. {loc}" for i, loc in enumerate(session["locations"])])
            msg.body(
                f"🔙 *Back to Location Selection:*\n\n{loc_text}\n\n✍️ Reply with a number (e.g., 1)"
            )
        else:
            msg.body("⚠️ Session error. Please type *restart* to start over.")
        return str(resp)

    # 🧭 Choosing location
    if session.get("step") == "choose_location":
        try:
            index = int(incoming_msg) - 1
            location = session["locations"][index]
            session["selected_location"] = location
            session["step"] = "choose_vehicle"

            trucks = df[df["Location"] == location]["Truck"].dropna().tolist()
            session["trucks"] = trucks
            truck_text = "\n".join([f"{i+1}. {t}" for i, t in enumerate(trucks)])
            msg.body(
                f"🚛 *Trucks in {location}:*\n\n{truck_text}\n\n"
                f"✍️ Reply with truck number\n🔁 Type 'back' to go back"
            )
        except:
            msg.body("❌ Invalid input. Please reply with a valid number.")
        return str(resp)

    # 🚛 Choosing vehicle
    if session.get("step") == "choose_vehicle":
        try:
            index = int(incoming_msg) - 1
            truck = session["trucks"][index]
            row = df[df["Truck"] == truck].iloc[0]
            session["step"] = "done"

            report = (
                f"📍 *{row['Truck']} Status Report*\n\n"
                f"🛞 Tire: {row['Tire']}\n"
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
                f"🗓️ Next Service: {row['Next Service']}\n"
                f"💬 Status: {row['Status']}"
            )
            msg.body(report + "\n\n🔁 Type 'back' or 'restart'")
        except:
            msg.body("❌ Invalid truck number. Try again or type 'back'.")
        return str(resp)

    # ❓ Fallback
    msg.body("❓ I didn’t understand that. Type *start* or *restart* to begin.")
    return str(resp)

# 🔁 Render-compatible runner
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
