from flask import Flask, request, jsonify
from twilio.rest import Client
import requests
import threading
import time

app = Flask(__name__)

# Twilio configuration
TWILIO_SID = 'your_twilio_sid'
TWILIO_AUTH_TOKEN = 'your_twilio_auth_token'
TWILIO_PHONE = 'your_twilio_phone_number'

client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)

def check_website(url, phone_number, duration_in_seconds):
    end_time = time.time() + duration_in_seconds
    while time.time() < end_time:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code != 200:
                raise ValueError("Website down")
        except Exception:
            send_notification(phone_number, f"The website {url} is down!")
            break
        time.sleep(600)  # Check every 10 minutes

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
    duration_hours = int(data.get('duration'))
    duration_seconds = duration_hours * 3600  # Convert hours to seconds
    
    # Starting a new thread for website monitoring
    threading.Thread(target=check_website, args=(url, phone_number, duration_seconds)).start()
    return jsonify({"message": "Website monitoring started"}), 200

if __name__ == '__main__':
    app.run(debug=True)