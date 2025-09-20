# Install required packages
# pip install pinecone-client openai

import os
from pinecone import Pinecone, ServerlessSpec
from openai import OpenAI
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from conversation_agent.load_models import ModelLoader

load_dotenv()


class Fetcher:
    def __init__(self, model_type="SentenceTransformer"):
        pc = Pinecone(api_key=PINECONE_API_KEY)
        self.index = pc.Index(INDEX_NAME)
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model_type = model_type
        if model_type == "SentenceTransformer":
            self.embed_model = SENTENCE_TRANSFORMER_EMBED_MODEL
        elif model_type == "OpenAI":
            self.embed_model = OPENAI_EMBED_MODEL

    def embed_text(self, text: str, model):
        """Create embeddings from text."""
        if self.model_type == "OpenAI":
            emb = self.openai_client.embeddings.create(
                model=self.embed_model,
                input=text
            )
            return emb.data[0].embedding
        elif self.model_type == "SentenceTransformer":
            if not model:
                model_loader = ModelLoader()    
                model = model_loader.load_embed_model(embed_model_type=self.model_type)
            vector = model.encode(text, convert_to_tensor=False).tolist()
            return vector

    def fetch(self, query_text, model=None, top_k = 10):
        query_embedding = self.embed_text(query_text, model)

        response = self.index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True
        )
        
        results = []
        for match in response['matches']:
            results.append({
                "id": match['id'],
                "score": match['score'],
                "metadata": match.get('metadata', {})
            })
        return results
    



# -----------------------------
# Configuration
# -----------------------------
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = "us-east-1"
INDEX_NAME = "deepheal-disorders"
OPENAI_EMBED_MODEL = "text-embedding-3-large"
SENTENCE_TRANSFORMER_EMBED_MODEL = "BAAI/bge-large-en-v1.5"


import time

if __name__ == "__main__":
    t1 = time.time()
    query_text = "I am having insomnia. Can not sleep at night."

    fetcher = Fetcher()
    results = fetcher.fetch(query_text, top_k=2)
    
    print("Top Results:")
    for i, res in enumerate(results, 1):
        print(f"{i}. ID: {res['id']}, Score: {res['score']}, Metadata: {res['metadata']}")

    t2 = time.time()
    print(f"\n\nNEXT\n")
    query_text = "I am having insomnia. Can not sleep at night."

    fetcher = Fetcher()
    results = fetcher.fetch(query_text, top_k=2)
    
    print("Top Results:")
    for i, res in enumerate(results, 1):
        print(f"{i}. ID: {res['id']}, Score: {res['score']}, Metadata: {res['metadata']}")

    t3 = time.time()
    print(f"\n\nNEXT\n")
    query_text = "I am having insomnia. Can not sleep at night."

    fetcher = Fetcher()
    results = fetcher.fetch(query_text, top_k=2)
    
    print("Top Results:")
    for i, res in enumerate(results, 1):
        print(f"{i}. ID: {res['id']}, Score: {res['score']}, Metadata: {res['metadata']}")

    t4 = time.time()
    print(f"\n\nNEXT\n")
    query_text = "I am having insomnia. Can not sleep at night."

    fetcher = Fetcher()
    results = fetcher.fetch(query_text, top_k=2)
    
    print("Top Results:")
    for i, res in enumerate(results, 1):
        print(f"{i}. ID: {res['id']}, Score: {res['score']}, Metadata: {res['metadata']}")
    t5 = time.time()

    print(f"\n\nTimes:\nT1: {t2-t1}\nT2: {t3-t2}\nT3: {t4-t3}\nT4: {t5-t4}\n")