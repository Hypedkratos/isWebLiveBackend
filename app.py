from flask import Flask, request, jsonify
from twilio.rest import Client
import requests
import threading
import time
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

# Twilio configuration
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE = '+15108580913'

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def check_website(url, phone_number, duration_in_seconds):
    end_time = time.time() + duration_in_seconds
    while time.time() < end_time:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code != 200:
                raise ValueError("Website down")
        except Exception as e:
            print(f"Error in website check: {e}")
            send_notification(phone_number, f"The website {url} is down!")
            break
        time.sleep(600)

def send_notification(phone_number, message):
    # Sending SMS
    client.messages.create(
        body=message,
        from_=TWILIO_PHONE,
        to=phone_number
    )

    # Sending WhatsApp message 
    client.messages.create(
        body=message,
        from_='whatsapp:' + TWILIO_PHONE,
        to='whatsapp:' + phone_number
    )

@app.route('/monitor', methods=['POST'])
def monitor_website():
    data = request.json
    url = data.get('url')
    phone_number = data.get('phone_number')
    duration = data.get('duration')

    if not url or not phone_number or not duration:
        return jsonify({"error": "Missing required fields"}), 400

    try:
        duration_hours = int(duration)
        duration_seconds = duration_hours * 3600
        threading.Thread(target=check_website, args=(url, phone_number, duration_seconds)).start()
        return jsonify({"message": "Website monitoring started"}), 200
    except ValueError:
        return jsonify({"error": "Invalid duration value"}), 400


if __name__ == '__main__':
    app.run(debug=True)
