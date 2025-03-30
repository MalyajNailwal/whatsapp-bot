from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import pandas as pd

app = Flask(__name__)

# Load movie data
df = pd.read_csv("movies_data.csv")

# In-memory user session state
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

    if incoming_msg == "start" and session["step"] == "start":
        session["step"] = "awaiting_genre"
        msg.body("👋 Welcome! What genre are you interested in? (e.g., Horror, Thriller, Sci-Fi)")
        return str(resp)

    elif session["step"] == "awaiting_genre":
        genre = incoming_msg.title()
        filtered_df = df[df["Genre"].str.lower() == incoming_msg.lower()]
        if filtered_df.empty:
            msg.body("❌ Sorry, no movies found in that genre. Try another one.")
        else:
            session["step"] = "awaiting_director"
            session["genre"] = genre
            directors = filtered_df["Director"].unique().tolist()
            director_list = "\n".join(f"- {d}" for d in directors)
            msg.body(f"🎬 Here are directors in '{genre}' genre:\n{director_list}\n\nType one to get movie details.")
        return str(resp)

    elif session["step"] == "awaiting_director":
        genre = session.get("genre", "")
        filtered_df = df[(df["Genre"].str.lower() == genre.lower()) & (df["Director"].str.lower() == incoming_msg.lower())]
        if filtered_df.empty:
            msg.body("❌ No matching director found in that genre. Try typing a correct name.")
        else:
            movie = filtered_df.iloc[0]
            reply = (
                f"*{movie['Title']}* ({movie['Year']})\n"
                f"Directed by: {movie['Director']}\n"
                f"Genre: {movie['Genre']}\n"
                f"Synopsis: {movie['Synopsis']}"
            )
            msg.body(reply + "\n\nWant another genre? Just type it!")
            session["step"] = "awaiting_genre"
        return str(resp)

    else:
        msg.body("Type 'start' to begin exploring movies 🎬")
        return str(resp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
