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
