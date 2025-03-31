from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import pandas as pd
import os

app = Flask(__name__)

# Load the tire dataset
try:
    df = pd.read_csv("tire_data.csv")
    df.columns = df.columns.str.strip()
    print("✅ CSV loaded successfully.")
except Exception as e:
    print("❌ CSV load failed:", e)
    df = pd.DataFrame()

# Store user sessions in memory
user_sessions = {}

@app.route("/", methods=["GET"])
def home():
    return "👋 Bot is up and running!"

@app.route("/bot", methods=["POST"])
def bot():
    try:
        incoming_msg = request.form.get("Body", "").strip()
        user_number = request.form.get("From", "")
        normalized_msg = incoming_msg.lower()
        print(f"📩 From: {user_number} | Message: '{incoming_msg}'")

        resp = MessagingResponse()
        msg = resp.message()

        # Initialize session
        if user_number not in user_sessions:
            user_sessions[user_number] = {"step": "start"}
        session = user_sessions[user_number]

        # 🔁 Restart
        if normalized_msg == "restart":
            locations = sorted(df["Location"].dropna().unique())
            user_sessions[user_number] = {
                "step": "choose_location",
                "locations": locations
            }
            session = user_sessions[user_number]
            location_list = "\n".join([f"{i+1}. {loc}" for i, loc in enumerate(locations)])
            msg.body(
                f"🔄 *Session restarted!*\n\n"
                f"📍 *Choose a Location:*\n\n{location_list}\n\n"
                f"✍️ Reply with number (e.g., 1)"
            )
            return str(resp)

        # ▶️ Start
        if normalized_msg == "start":
            session["step"] = "choose_location"
            locations = sorted(df["Location"].dropna().unique())
            session["locations"] = locations
            location_list = "\n".join([f"{i+1}. {loc}" for i, loc in enumerate(locations)])
            msg.body(
                f"📍 *Select a Location:*\n\n{location_list}\n\n"
                f"✍️ Reply with number (e.g., 1)\n🔁 Type 'restart' anytime"
            )
            return str(resp)

        # ⬅️ Back
        if normalized_msg == "back":
            session["step"] = "choose_location"
            locations = session.get("locations", sorted(df["Location"].dropna().unique()))
            session["locations"] = locations
            location_list = "\n".join([f"{i+1}. {loc}" for i, loc in enumerate(locations)])
            msg.body(
                f"🔙 *Back to Location Selection:*\n\n{location_list}\n\n"
                f"✍️ Reply with number (e.g., 1)"
            )
            return str(resp)

        # 📍 Choose location
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
                    f"✍️ Reply with number to view details\n🔁 Type 'back' to change location"
                )
            except Exception as e:
                msg.body("❌ Invalid number. Please try again or type 'restart'.")
                print("❌ Error choosing location:", e)
            return str(resp)

        # 🚚 Choose truck
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
            except Exception as e:
                msg.body("❌ Invalid truck number. Try again or type 'restart'.")
                print("❌ Error selecting truck:", e)
            return str(resp)

        # Fallback
        msg.body("❓ I didn’t get that. Type *start* to begin or *restart* to reset.")
        return str(resp)

    except Exception as e:
        print("🔥 GLOBAL ERROR:", e)
        resp.message("⚠️ Something went wrong. Type 'restart' to try again.")
        return str(resp)

# Run the app on Render
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
