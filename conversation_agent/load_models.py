import os
import sys
from openai import OpenAI
from sentence_transformers import SentenceTransformer
from langchain_community.llms import Ollama
from langchain_openai import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from dotenv import load_dotenv
from functools import lru_cache
import warnings
from langchain_core._api import LangChainDeprecationWarning

warnings.filterwarnings("ignore", category=LangChainDeprecationWarning)
load_dotenv()



_embed_model = None
_therapist = None
_therapist_assistant_model = None

class ModelLoader:
    def __init__(self):
        pass


    @lru_cache(maxsize=1)
    def load_embed_model(self, embed_model_type="SentenceTransformer"):
        self.embed_model_type = embed_model_type
        if embed_model_type == "SentenceTransformer":
            self.embed_model = SENTENCE_TRANSFORMER_EMBED_MODEL
        elif embed_model_type == "OpenAI":
            self.embed_model = OPENAI_EMBED_MODEL

        global _embed_model
        if _embed_model is None:
            print("Loading Embedding Model into Memory...")
            if self.embed_model_type == "SentenceTransformer":
                _embed_model = SentenceTransformer(self.embed_model, device="cuda")
        return _embed_model
    

    @lru_cache(maxsize=1)
    def load_therapist(self, therapist_thinker_model_type="ollama", model="gpt-oss:latest", temp=0.6):
        self.therapist_thinker_model_type = therapist_thinker_model_type

        global _therapist
        if _therapist is None:
            print("Loading Therapist Thinker Model into Memory...")

            if self.therapist_thinker_model_type == "ollama":
                self.therapist_thinker_model = model

                print(f"Model Specs:\nModel:{self.therapist_thinker_model}\n")

                memory = ConversationBufferMemory(memory_key="history", return_messages=True)
                _therapist_model = Ollama(model=self.therapist_thinker_model, base_url="http://localhost:11434")
                _therapist = ConversationChain(
                    llm=_therapist_model,
                    memory=memory,
                    # verbose=True
                )

            if self.therapist_thinker_model_type == "openai":
                self.therapist_thinker_model = model if model == "gpt-4o-mini" or model == "gpt-4.1-mini" else "gpt-4.1-mini"
                
                print(f"Therapist Agent Model Specs:\nModel:{self.therapist_thinker_model}\n")

                memory = ConversationBufferMemory(memory_key="history", return_messages=True)
                _therapist_model = ChatOpenAI(model_name=self.therapist_thinker_model, temperature=temp, openai_api_key=os.getenv("OPENAI_API_KEY"))
                _therapist = ConversationChain(
                    llm=_therapist_model,
                    memory=memory,
                    # verbose=True
                )

        return _therapist

    @lru_cache(maxsize=1)
    def load_therapist_assistant(self, therapist_assistant_model_type="ollama", model="gpt-oss:latest", temp=0.6):
        self.therapist_assistant_model_type = therapist_assistant_model_type

        global _therapist_assistant_model
        if _therapist_assistant_model is None:
            print("Loading Therapist Assistant Model into Memory...")

            if self.therapist_assistant_model_type == "ollama":
                self.therapist_assistant_model = model

                print(f"Therapist Assistant Model Specs:\nModel:{self.therapist_assistant_model}\n")

                _therapist_assistant_model = Ollama(model=self.therapist_assistant_model, base_url="http://localhost:11434")
                _therapist_assistant_model = ConversationChain(
                    llm=_therapist_assistant_model,
                    memory=None,
                )

            if self.therapist_assistant_model_type == "openai":
                self.therapist_assistant_model = model if model == "gpt-4o-mini" or model == "gpt-4.1-mini" else "gpt-4.1-mini"
                
                print(f"Therapist Assistant Model Specs:\nModel:{self.therapist_assistant_model}\n")

                # _therapist_assistant_model = ChatOpenAI(model_name=self.therapist_assistant_model, temperature=temp, openai_api_key=os.getenv("OPENAI_API_KEY"))
                # _therapist_assistant = ConversationChain(
                #     llm=_therapist_assistant_model,
                #     memory=None,
                # )
                _therapist_assistant_model = ChatOpenAI(model_name=self.therapist_assistant_model, temperature=temp, openai_api_key=os.getenv("OPENAI_API_KEY"))


        return _therapist_assistant_model


OPENAI_EMBED_MODEL = "text-embedding-3-large"
SENTENCE_TRANSFORMER_EMBED_MODEL = "BAAI/bge-large-en-v1.5"
