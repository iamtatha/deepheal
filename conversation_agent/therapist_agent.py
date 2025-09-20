
from conversation_agent.load_models import ModelLoader
from conversation_agent.fetch_disorders import Fetcher
from conversation_agent.therapist_assistant import TherapistAssistant
from utils.token_count import count_tokens
from dotenv import load_dotenv
from datetime import datetime
import json
import os

load_dotenv()

class Therapist:
    def __init__(self, model_type="ollama", model="gpt-oss:latest", isAssistant=True, fetcher=None, logging=True, mock=False):
        self.therapist_model_type = model_type
        if model_type == "ollama":
            self.therapist_model = model or "gpt-oss:latest"
        elif model_type == "openai":
            self.therapist_model = model or "gpt-4o-mini"
        temperature = 0.7

        model_loader = ModelLoader()
        self.therapist = model_loader.load_therapist(self.therapist_model_type, self.therapist_model, temperature)
        self.therapist_assistant = TherapistAssistant(model_type=model_type) if isAssistant else None

        self.isAssistant = isAssistant
        if fetcher is None:
            self.disorder_context = False
        else:
            self.disorder_context = True
            self.fetcher = fetcher

        self.logging = logging
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = f"logs/conv_{timestamp}.json"

        if os.path.exists(self.log_file):
            print(f"Log file {self.log_file} already exists. Removing it.")
            os.remove(self.log_file)

        self.mock = mock

    def write_log(self, role, info={}, action_name=""):
        if self.logging and len(info.keys()) > 0:
            if role == "AI" or role == "Human" or role == "Prompt":
                log_entry = {
                    "role": role,
                    "details": info,
                    "timestamp": datetime.now().isoformat(),
                }
            if role == "Action":
                log_entry = {
                    "role": role,
                    "name": action_name,
                    "details": info,
                    "timestamp": datetime.now().isoformat(),
                }

            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

    def get_system_prompt(self, query="", disorder_context=""):
        if len(self.therapist.memory.chat_memory.messages) == 0:
            with open(f"prompts/therapist_initial_prompt.txt", 'r') as f:
                self.initial_system_prompt = f.read()
            with open(f"prompts/therapist_intermediate_prompt.txt", 'r') as f:
                self.intermediate_system_prompt = f.read()

            prompt = f"{self.initial_system_prompt}"
            self.write_log('Prompt', {"prompt": prompt})
            return prompt

        prompt = f"{self.intermediate_system_prompt}\n"
        if self.disorder_context and disorder_context:
            prompt += f"\n{disorder_context}\n"
        prompt += f"Patient Response: {query}"
        self.write_log("Prompt", {"prompt": self.intermediate_system_prompt})
        return prompt

    def fetch_disorder_info(self, query, top_k=5, threshold=0.59):
        if self.disorder_context and len(self.therapist.memory.chat_memory.messages) > 2:
            results = self.fetcher.fetch(query, top_k=top_k)
            summary_results = "Possible Disorder Matches:\n"
            log_results = ""

            for i, res in enumerate(results, 1):
                title = res['id']
                score = res['score']
                criteria = res['metadata']['diagnostic_criteria']
                
                if score > threshold:
                    summary_results += f"Disorder Match {i}. {title} (Score: {score:.2f})\nDiagnostic Criteria: {criteria}\n"
                    log_results += f"{i}. ID: {title}, Score: {score:.2f}"

            self.write_log("Action", {"response": log_results}, "Fetcher")
            return self.assistant(summary_results, log_results)
        return ""
    
    def assistant(self, summary_results, log_results):
        if not self.isAssistant or len(log_results.strip()) == 0:
            return summary_results
        assistant_response, assistant_prompt = self.therapist_assistant.help(summary_results, self.therapist.memory.chat_memory.messages)
        self.write_log("Action", {"response": assistant_response, "input": assistant_prompt, "Input_tokens": count_tokens(assistant_prompt), "Output_tokens": assistant_response}, "Therapist_Assistant")
        return assistant_response


    def proactive_start(self):
        prompt = self.get_system_prompt("")
        if not self.mock:
            response = self.therapist.run(prompt)
        else:
            response = "A: Proactive start"
        self.write_log("AI", {"response": response, "Input_tokens": count_tokens(prompt), "Output_tokens": count_tokens(response)})
        return response
    

    def ask(self, query, casual=False):
        self.write_log("Human", {"query": query})

        disorder_context = self.fetch_disorder_info(query)
        prompt = self.get_system_prompt(query, disorder_context)
        if not self.mock:
            response = self.therapist.run(prompt)
        else:
            response = f"B: User: {query}"
        
        self.write_log("AI", {"response": response, "Input_tokens": count_tokens(prompt), "Output_tokens": count_tokens(response)})    
        return response
    
