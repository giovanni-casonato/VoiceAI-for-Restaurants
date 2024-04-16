from typing_extensions import override
from openai import OpenAI, AssistantEventHandler
from openai.types.beta.threads import Message
from tts_deepgram import DeepgramAPI

deepgram = DeepgramAPI()

class FoodOrderAssistant:
    def __init__(self, company_name, company_location):
        self.client = OpenAI()
        self.company_name = company_name
        self.company_location = company_location
        self.assistant = None
        self.thread = None

    def initialize_assistant(self):
        with open('instructions.txt', "r") as f:
            instructions = f.read()
        
        self.assistant = self.client.beta.assistants.create(
            name="Food Orders",
            instructions=f"You are Sophia, an employee at {self.company_name} in {self.company_location} who picks up the phone to take orders from customers. {instructions}",
            tools=[{"type": "retrieval"}],
            model="gpt-4-turbo",
        )

        self.thread = self.client.beta.threads.create()

    class EventHandler(AssistantEventHandler):

        @override
        def on_text_created(self, text) -> None:
            print(f"Assistant: ", end="", flush=True)
            
        @override
        def on_text_delta(self, delta, snapshot):
            print(f"{delta.value}", end="", flush=True)

        @override
        def on_message_done(self, message: Message) -> None:
            # check if message contains food order

            assistant_response = message.content[0].text.value
            deepgram.get_b64_audio_from_text(assistant_response)
            return super().on_message_done(message)

        
        def on_tool_call_created(self, tool_call):
            print(f"\nAssistant: {tool_call.type}\n", flush=True)
          
        def on_tool_call_delta(self, delta, snapshot):
            if delta.type == 'code_interpreter':
                if delta.code_interpreter.input:
                    print(delta.code_interpreter.input, end="", flush=True)
                if delta.code_interpreter.outputs:
                    print(f"\n\noutput: ", flush=True)
                    for output in delta.code_interpreter.outputs:
                        if output.type == "logs":
                            print(f"\n{output.logs}", flush=True)

    def start_conversation(self):
        event_handler = self.EventHandler()
        
        with self.client.beta.threads.runs.create_and_stream(
            thread_id=self.thread.id,
            assistant_id=self.assistant.id,
            instructions=self.assistant.instructions,
            event_handler=event_handler,
        ) as stream:
            stream.until_done()
    
    # TODO: Fix thread interactions, seems like new thread is being started after each transcript
    def end_conversation(self):
        event_handler = self.EventHandler()
        with self.client.beta.threads.runs.create_and_stream(
            thread_id=self.thread.id,
            assistant_id=self.assistant.id,
            instructions= "Now that you have received a food order, I need you to output the order into a JSON format",
            event_handler = event_handler,
        ) as stream:
            stream.until_done()
        
        print('Trying to place order')


