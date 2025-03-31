from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import pandas as pd
import os

app = Flask(__name__)

# Load tire data
df = pd.read_csv("tire_data.csv")
df.columns = df.columns.str.strip()

# Store session state
user_sessions = {}

@app.route("/bot", methods=["POST"])
def bot():
    incoming_msg = request.form.get("Body", "").strip()
    user_number = request.form.get("From", "")
    normalized_msg = incoming_msg.lower()
    print(f"📩 From: {user_number} | Message: {incoming_msg}")

    resp = MessagingResponse()
    msg = resp.message()

    # Initialize user session
    if user_number not in user_sessions:
        user_sessions[user_number] = {"step": "start"}
    session = user_sessions[user_number]

    # 🔁 Restart: Always works
    if normalized_msg == "restart":
        locations = sorted(df["Location"].unique())
        user_sessions[user_number] = {
            "step": "choose_location",
            "locations": locations
        }
        location_list = "\n".join([f"{i+1}. {loc}" for i, loc in enumerate(locations)])
        msg.body(
            f"🔄 *Session restarted!*\n\n"
            f"📍 *Choose a Location:*\n\n{location_list}\n\n"
            f"✍️ _Reply with number (e.g., 1)_"
        )
        return str(resp)

    # ▶️ Start
    if normalized_msg == "start":
        session["step"] = "choose_location"
        locations = sorted(df["Location"].unique())
        session["locations"] = locations
        location_list = "\n".join([f"{i+1}. {loc}" for i, loc in enumerate(locations)])
        msg.body(
            f"📍 *Select a Location:*\n\n{location_list}\n\n"
            f"✍️ _Reply with number (e.g., 1)_\n🔁 Type 'restart' anytime."
        )
        return str(resp)

    # ⬅️ Back to location
    if normalized_msg == "back":
        session["step"] = "choose_location"
        locations = session.get("locations", sorted(df["Location"].unique()))
        session["locations"] = locations
        location_list = "\n".join([f"{i+1}. {loc}" for i, loc in enumerate(locations)])
        msg.body(
            f"🔙 *Back to Location Selection:*\n\n{location_list}\n\n"
            f"✍️ _Reply with number (e.g., 1)_"
        )
        return str(resp)

    # 🧭 Location Selection
    if session.get("step") == "choose_location":
        try:
            index = int(normalized_msg) - 1
            location = session["locations"][index]
            session["selected_location"] = location
            session["step"] = "choose_vehicle"

            trucks = df[df["Location"] == location]["Truck"].tolist()
            session["trucks"] = trucks

            truck_list = "\n".join([f"{i+1}. {truck}" for i, truck in enumerate(trucks)])
            msg.body(
                f"🚛 *Trucks in {location}:*\n\n{truck_list}\n\n"
                f"✍️ _Reply with number to view details_\n🔁 Type 'back' to change location"
            )
        except:
            msg.body("❌ Invalid number. Please try again.\nOr type 'restart' to start fresh.")
        return str(resp)

    # 🚛 Truck Details
    if session.get("step") == "choose_vehicle":
        try:
            index = int(normalized_msg) - 1
            truck = session["trucks"][index]
            session["step"] = "done"

            row = df[df["Truck"] == truck].iloc[0]
            detail = (
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
                f"🗓️ Next Service: {row['Next Service']}\n"
                f"💬 Status: {row['Status']}"
            )
            msg.body(detail + "\n\n🔁 Type 'back' or 'restart'")
        except:
            msg.body("❌ Invalid number. Try again or type 'restart'.")
        return str(resp)

    # 🧭 Fallback
    msg.body("❓ I didn’t get that. Type *start* to begin or *restart* to reset.")
    return str(resp)

# Run for Render or Railway
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
