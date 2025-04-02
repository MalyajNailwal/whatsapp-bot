# 🎬 WhatsApp Movie Info Bot

A cloud-deployed WhatsApp bot built with Python, Flask, Twilio, and Render. When you send a truck title via WhatsApp, it responds with truck information.
## 🚀 Features
- 💬 Chat on WhatsApp to search any truck_detail
- 🔍 Data comes from movies_data.csv
- 📲 Instant replies with movie details
- ☁️ Hosted on Render with public webhook
- 🔁 Easily updatable CSV data
- 📱 Can be upgraded to your personal WhatsApp number

## ⚙️ Technologies Used
- Python 3.9+
- Flask
- Twilio
- Pandas
- Render
- Ngrok (for local testing)

## ✅ How to Run Locally
1. Clone the project:
git clone https://github.com/MalyajNaiwal/whatsapp-bot.git
cd whatsapp-bot

2. Create a virtual environment:
python -m venv try2

3. Activate the environment:
On macOS/Linux: source venv/bin/activate
On Windows: try2\Scripts\activate

4. Install dependencies:
pip install -r requirements.txt

5. Run Flask server:
python app.py

6. Open a second terminal and run ngrok:
ngrok http 5000

7. Copy your ngrok HTTPS URL and paste into Twilio Sandbox:
https://xxxx-xxxx.ngrok-free.app/bot (method = POST)

## 🌐 How to Deploy on Render
1. Push your project to GitHub
2. Go to https://render.com
3. Click “New Web Service”
4. Connect your GitHub repo
5. Use the following settings:
   - Build Command: pip install -r requirements.txt
   - Start Command: python app.py
   - Python Version: 3.9
6. In your app.py, make sure this is the last line:
app.run(host="0.0.0.0", port=5000)
7. Deploy → Copy your live URL
8. Add /bot to the end and paste into Twilio webhook:
https://your-bot.onrender.com/bot (method = POST)

## 🔄 How to Update Movie Data

Option 1 (Manual):
- Replace tire_data.csv with new data
- Run:
git add tire_data.csv
git commit -m "update movie list"
git push

Option 2 (Live CSV URL):
- Replace:
pd.read_csv("tire_data.csv")
- With:
pd.read_csv("https://your-live-data-link.com/movies.csv")

## 📱 Use Your Own WhatsApp Number (Not Sandbox)
1. Go to https://business.facebook.com and verify your business
2. Buy a Twilio number
3. Go to https://www.twilio.com/console/sms/whatsapp/senders
4. Add your real phone number and complete approval (takes 1–2 days)
5. Replace sandbox webhook with your production webhook
6. Done ✅

## 💬 Example WhatsApp Interaction

You send:
your_truck_name

You receive:
**All info**

## 📁 Folder Structure

whatsapp-bot/
├── app.py
├── tire_data.csv
├── requirements.txt
├── README.md



## 🔐 Built with 💬 Flask + ☁️ Render + ⚡ Twilio + ❤️ for WICK
