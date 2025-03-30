from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import pandas as pd

app = Flask(__name__)

df = pd.read_csv("tire_data.csv")
user_sessions = {}

@app.route("/bot", methods=["POST"])
def bot():
    user_number = request.form.get("From", "")
    incoming_msg = request.form.get("Body", "").strip().lower()
    resp = MessagingResponse()
    msg = resp.message()

    if user_number not in user_sessions:
        user_sessions[user_number] = {"step": "start"}

    session = user_sessions[user_number]

    if incoming_msg == "start":
        session["step"] = "choose_location"
        locations = sorted(df["Location"].unique())
        session["locations"] = locations
        location_list = "\n".join([f"{i+1}. {loc}" for i, loc in enumerate(locations)])
        msg.body(f"📍 Please choose a location:\n\n{location_list}\n\nType the number (e.g., 1)")
        return str(resp)

    if incoming_msg == "back":
        session["step"] = "choose_location"
        locations = session["locations"]
        location_list = "\n".join([f"{i+1}. {loc}" for i, loc in enumerate(locations)])
        msg.body(f"📍 Back to location selection:\n\n{location_list}\n\nType the number (e.g., 1)")
        return str(resp)

    if session["step"] == "choose_location":
        try:
            index = int(incoming_msg) - 1
            location = session["locations"][index]
            session["selected_location"] = location
            session["step"] = "choose_vehicle"

            trucks = df[df["Location"] == location]["Truck"].tolist()
            session["trucks"] = trucks

            truck_list = "\n".join([f"{i+1}. {truck}" for i, truck in enumerate(trucks)])
            msg.body(f"🚛 Trucks in *{location}*:\n\n{truck_list}\n\nType the number to view details.\nType 'back' to change location.")
            print("🧠 Location selected:", location)
            print("📊 Trucks found:", trucks)
        except:
            msg.body("❌ Invalid input. Please type a number from the list.")
        return str(resp)

    if session["step"] == "choose_vehicle":
        try:
            index = int(incoming_msg) - 1
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
                f"🗓️ Next Service Due: {row['Next Service']}\n"
                f"💬 Status: {row['Status']}"
            )
            msg.body(detail + "\n\n🔁 Type 'back' to choose another truck or location.")
        except:
            msg.body("❌ Invalid input. Please type a valid number.\nOr type 'back' to go back.")
        return str(resp)

    msg.body("🔁 Type *start* to begin or *back* to go back.")
    return str(resp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
