from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import pandas as pd
import os

app = Flask(__name__)

df = pd.read_csv("tire_data.csv")
df.columns = df.columns.str.strip()

user_sessions = {}

@app.route("/bot", methods=["POST"])
def bot():
    incoming_msg = request.form.get("Body", "").strip().lower()
    user_number = request.form.get("From", "")
    print(f"📩 From: {user_number} | Message: {incoming_msg}")

    resp = MessagingResponse()
    msg = resp.message()

    if user_number not in user_sessions:
        user_sessions[user_number] = {"step": "start"}
        print(f"🆕 New user session started for {user_number}")

    session = user_sessions[user_number]
    print(f"🔁 Current step: {session['step']}")

    try:
        # RESTART
        if incoming_msg == "restart":
            locations = sorted(df["Location"].unique())
            user_sessions[user_number] = {
                "step": "choose_location",
                "locations": locations
            }
            session = user_sessions[user_number]
            print("🔄 Restarting session")

            location_list = "\n".join([f"{i+1}. {loc}" for i, loc in enumerate(locations)])
            msg.body(
                f"🔄 *Session restarted!*\n\n"
                f"📍 *Choose a Location:*\n\n{location_list}\n\n"
                f"✍️ _Reply with number (e.g., 1)_"
            )
            return str(resp)

        # START
        if incoming_msg == "start":
            session["step"] = "choose_location"
            locations = sorted(df["Location"].unique())
            session["locations"] = locations
            print("📍 Location selection initiated")

            location_list = "\n".join([f"{i+1}. {loc}" for i, loc in enumerate(locations)])
            msg.body(
                f"📍 *Select a Location:*\n\n{location_list}\n\n"
                f"✍️ _Reply with number (e.g., 1)_\n🔄 Type 'restart' anytime."
            )
            return str(resp)

        # BACK
        if incoming_msg == "back":
            session["step"] = "choose_location"
            locations = session.get("locations", sorted(df["Location"].unique()))
            print("🔙 Going back to location selection")

            location_list = "\n".join([f"{i+1}. {loc}" for i, loc in enumerate(locations)])
            msg.body(
                f"🔙 *Back to Location Selection:*\n\n{location_list}\n\n"
                f"✍️ _Reply with number (e.g., 1)_"
            )
            return str(resp)

        # LOCATION SELECT
        if session["step"] == "choose_location":
            try:
                index = int(incoming_msg) - 1
                location = session["locations"][index]
                session["selected_location"] = location
                session["step"] = "choose_vehicle"

                trucks = df[df["Location"] == location]["Truck"].tolist()
                session["trucks"] = trucks
                print(f"✅ Location selected: {location} | Trucks found: {len(trucks)}")

                truck_list = "\n".join([f"{i+1}. {truck}" for i, truck in enumerate(trucks)])
                msg.body(
                    f"🚛 *Trucks in {location}:*\n\n{truck_list}\n\n"
                    f"✍️ _Reply with number to view details_\n🔁 Type 'back' to change location"
                )
            except Exception as e:
                print("❌ Error selecting location:", e)
                msg.body("❌ Invalid number. Please try again.\nOr type 'restart' to start fresh.")
            return str(resp)

        # TRUCK SELECT
        if session["step"] == "choose_vehicle":
            try:
                index = int(incoming_msg) - 1
                truck = session["trucks"][index]
                session["step"] = "done"

                row = df[df["Truck"] == truck].iloc[0]
                print(f"✅ Truck selected: {truck}")

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
                print("❌ Error selecting truck:", e)
                msg.body("❌ Invalid number. Please try again.\nOr type 'restart'.")
            return str(resp)

        # Fallback
        print("⚠️ Message not understood.")
        msg.body("❓ I didn’t get that. Type *start* to begin or *restart* to reset.")
        return str(resp)

    except Exception as e:
        print("🔥 GLOBAL ERROR:", e)
        msg.body("⚠️ Something went wrong. Please type *restart* to try again.")
        return str(resp)

# For Railway/Render
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
