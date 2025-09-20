from conversation_agent.load_models import ModelLoader
from dotenv import load_dotenv
from datetime import datetime
import json

load_dotenv()



SYSTEM_PROMPT = """You are an assistant to me, who is a professional therapist. I will provide you with my question, patient's response and the relevant potential mental health disorders.
I will also provide you with diagnostic criteria of all these potential disorders. From the patient response and the disorder context, do the following:
- Summarise the issues the patient is facing in a concise manner based on just current info (don't emphasize too much since it is just temporary context).
- For all of these listed disorders, add a precise summary of diagnostic criteria with only the most crucial symptoms.

- Suggest further possible symptoms I should ask the patient about to decide on possible disorders from this list.

My Question: {question}

Patient Response: {response}

Relevant Disorders: {disorders}
"""



class TherapistAssistant:
    def __init__(self, model_type="ollama", model="gpt-oss:latest"):
        self.therapist_assistant_model_type = model_type
        if model_type == "ollama":
            self.therapist_assistant_model = model or "gpt-oss:latest"
        elif model_type == "openai":
            self.therapist_assistant_model = model or "gpt-4o-mini"
        temperature = 0.7

        model_loader = ModelLoader()
        self.therapist_assistant = model_loader.load_therapist_assistant(self.therapist_assistant_model_type, self.therapist_assistant_model, temperature)


    def get_system_prompt(self, fetched_disorders="", last_convo=[]):
        system_prompt = SYSTEM_PROMPT.format(
            question=last_convo[-2] if len(last_convo) > 1 else "",
            response=last_convo[-1] if len(last_convo) > 0 else "",
            disorders=fetched_disorders,
        )
        return system_prompt

    def help(self, fetched_disorders, memory, casual=False):
        last_convo = []
        if not memory:
            print("No conversation history found.")
        else:
            last_two = memory[-2:] if len(memory) >= 2 else memory[-len(memory):]
            for msg in last_two:
                last_convo.append(msg.content)

        prompt = self.get_system_prompt(fetched_disorders, last_convo)
        response = self.run(prompt)
        return response, prompt
    
    def run(self, prompt):
        response = self.therapist_assistant.invoke(prompt)
        return response.content
  