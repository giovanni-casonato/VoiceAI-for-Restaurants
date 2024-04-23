import requests
import os
import base64


class DeepgramAPI:
    def __init__(self):
        self.url = "https://api.deepgram.com/v1/speak?model=aura-stella-en"
        self.api_key = os.getenv("DEEPGRAM_API_KEY")
        if not self.api_key:
            raise ValueError("Deepgram API key not found.")
        self.headers = {
            "Authorization": f"Token {self.api_key}",
            "Content-Type": "application/json"
        }

    def get_b64_audio_from_text(self, text):
        payload = {
            "text": text
        }
        response = requests.post(self.url, headers=self.headers, json=payload, params={"encoding": "mulaw"})
        if response.status_code == 200:
            audio_data = response.content
            payload_b64 = base64.b64encode(audio_data).decode('utf-8')
            file_path = os.path.join("b64_client_data", f"output.txt")
            with open(file_path, "w") as f:
                f.write(payload_b64)
            print(f"File saved successfully at {file_path}\n")
        
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return False