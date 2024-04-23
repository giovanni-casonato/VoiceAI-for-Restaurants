import base64
import json
import os

from flask import Flask, request, send_from_directory, Response
from flask_sock import Sock
import ngrok
from twilio.rest import Client
from dotenv import load_dotenv
load_dotenv()

from twilio.twiml.voice_response import Connect, VoiceResponse

from src.twilio_transcriber import TwilioTranscriber

# Flask settings
PORT = 4000
DEBUG = False
INCOMING_CALL_ROUTE = '/'
WEBSOCKET_ROUTE = '/realtime'
FOLDER_PATH = 'src/b64_client_data'

# Twilio authentication
twilio_account_sid = os.environ['TWILIO_ACCOUNT_SID']
twilio_api_key = os.environ['TWILIO_API_KEY_SID']
twilio_api_secret = os.environ['TWILIO_API_SECRET']
client = Client(twilio_api_key, twilio_api_secret, twilio_account_sid)

# Twilio phone number to call
TWILIO_NUMBER = os.environ['TWILIO_NUMBER']

# ngrok authentication
ngrok.set_auth_token(os.getenv("NGROK_AUTHTOKEN"))

app = Flask(__name__)
sock = Sock(app)


@app.route(INCOMING_CALL_ROUTE, methods=['GET', 'POST'])
def receive_call():
    if request.method == 'POST':
        response = VoiceResponse()
        response.play(f'https://{request.host}/static/initial_greeting.mp3')
        connect = Connect()
        connect.stream(url=f'wss://{request.host}{WEBSOCKET_ROUTE}')
        response.append(connect)

        return Response(str(response), mimetype='text/xml')
    return "Hello World"

@sock.route(WEBSOCKET_ROUTE)
def transcription_websocket(ws):
    while True:
        if not os.path.exists(FOLDER_PATH):
            print("Folder does not exist.")
            return

        files = os.listdir(FOLDER_PATH)
        if not files:
            data = json.loads(ws.receive())
            match data['event']:
                case "connected":
                    transcriber = TwilioTranscriber()
                    transcriber.connect() # Connect to the AssemblyAI WebSocket, need to create multiple websocket connections for multiple calls
                    print('transcriber connected')
                case "start":
                    print('twilio started')
                    stream_sid = data['streamSid']
                case "media": 
                    payload_b64 = data['media']['payload']
                    payload_mulaw = base64.b64decode(payload_b64)
                    transcriber.stream(payload_mulaw)
                case "stop":
                    print('\ntwilio stopped')
                    transcriber.close()
                    print('transcriber closed')
                    # cleaning up output file if it still exists after call
                    if os.path.exists(os.path.join(FOLDER_PATH, 'output.txt')):
                        os.remove(os.path.join(FOLDER_PATH, 'output.txt'))

        for file_name in files:
            print("System: Sending file\n")
            file_path = os.path.join(FOLDER_PATH, file_name)
            with open(file_path, "r") as f:
                file_data = f.read()
                ws.send(json.dumps({'event': 'media', "streamSid": f"{stream_sid}", 'media': {'payload': file_data}}))
            os.remove(file_path)


@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

if __name__ == "__main__":
    try:
        # # Open Ngrok tunnel
        # listener = ngrok.forward(f"http://localhost:{PORT}")
        # print(f"Ngrok tunnel opened at {listener.url()} for port {PORT}")
        # NGROK_URL = listener.url()

        # Set ngrok URL to ne the webhook for the appropriate Twilio number
        twilio_numbers = client.incoming_phone_numbers.list()
        twilio_number_sid = [num.sid for num in twilio_numbers if num.phone_number == TWILIO_NUMBER][0]
        client.incoming_phone_numbers(twilio_number_sid).update(twilio_account_sid, voice_url=f"{'URL'}{INCOMING_CALL_ROUTE}")

        # run the app
        app.run(port=PORT, debug=DEBUG)
    finally:
        # Always disconnect the ngrok tunnel
        ngrok.disconnect()