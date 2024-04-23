# Environment and Credentials Setup

1. Create a virtual environment

```shell
# Mac/Linux
python3 -m venv venv
. venv/bin/activate

# Windows
python -m venv venv
.\venv\Scripts\activate.bat
```

2. Install required packages

```shell
pip install -r requirements.txt
```
Note: Be sure to add necessary folder for audio output of assembly and deepgram
# Run the application

Execute `python server.py` or `python3 server.py` in the project directory to start the application. Then, call your Twilio phone number and begin speaking. You will see your speech transcribed in the console.

# How it works

1. Twilio (server.py)
    - Get audio from incoming call, stream it to AssemblyAI

2. AssemblyAI (twilio_transcriber.py)
    - Convert the streamed audio into text

3. OpenAI Assistant (openai_assistant.py)
    - Feed the text into the assistant and get the response

4. Deepgram (tts_deepgram)
    - Get text response from OpenAI and convert it into audio

5. Twilio (server.py)
    - Send audio to call.

6. Always runs when server is on

#TODO

7. Transfer algorithm to deli phone number

8. Handle multiple calls at the same time (it should break on AssemblyAI websocket connection)

9. Host on the web (AWS or other)

10. Create ticket system when call is over

More....