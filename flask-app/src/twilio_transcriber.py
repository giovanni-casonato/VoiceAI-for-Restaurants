import os

import assemblyai as aai
from dotenv import load_dotenv
load_dotenv()
from src.openai_assistant import FoodOrderAssistant

aai.settings.api_key = os.getenv('ASSEMBLYAI_API_KEY')

#OpenAI assistant setup
company_name = "Jasper Deli"
company_location = "NYC"

# Create an instance of FoodOrderAssistant
assistant = FoodOrderAssistant(company_name, company_location)

TWILIO_SAMPLE_RATE = 8000 # Hz

def on_open(session_opened: aai.RealtimeSessionOpened):
    "Called when the connection has been established."
    #each call gets its own assistant
    assistant.initialize_assistant()
    print("Session ID:", session_opened.session_id) 


def on_data(transcript: aai.RealtimeTranscript):
    "Called when a new transcript has been received."

    if not transcript.text:
        return

    if isinstance(transcript, aai.RealtimeFinalTranscript):
        print(f"Caller: {transcript.text}", end="\r\n")
        
        assistant.client.beta.threads.messages.create(
            thread_id=assistant.thread.id,
            role="user",
            content=transcript.text,
        )
        # PROBLEM : conversation starts after each transcript
        assistant.start_conversation()
    else:
        print(f"{transcript.text}", end="\r")


def on_error(error: aai.RealtimeError):
    "Called when the connection has been closed."
    print("An error occured:", error)


def on_close():
    "Called when the connection has been closed."
    assistant.end_conversation()
    assistant.client.beta.assistants.delete(assistant.assistant.id)
    print("Closing Assistant Session")
    



class TwilioTranscriber(aai.RealtimeTranscriber):
    def __init__(self):
        super().__init__(
            on_data=on_data,
            on_error=on_error,
            on_open=on_open, # optional
            on_close=on_close, # optional
            sample_rate=TWILIO_SAMPLE_RATE,
            encoding=aai.AudioEncoding.pcm_mulaw
        )