#!/usr/bin/env python3
"""
Script: store_diagnostic_criteria_pinecone.py
Purpose:
  - Read .txt files containing disorder information
  - Extract diagnostic criteria via LLM
  - Create embeddings
  - Store in Pinecone vector database
"""

import os
from pathlib import Path
from openai import OpenAI
import ollama
import json
import unicodedata
import re
import sys
import google.generativeai as genai
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone, ServerlessSpec
from utils.token_count import count_tokens

from dotenv import load_dotenv

load_dotenv()

class VDB:
    def __init__(self, model="SentenceTransformer", sample=100):
        self.vdb_dim = 1024
        self.index_name = INDEX_NAME
        if model == "SentenceTransformer":
            self.embed_model = SENTENCE_TRANSFORMER_EMBED_MODEL
        elif model == "OpenAI":
            self.embed_model = OPENAI_EMBED_MODEL
        self.model_type = model
        self.model = None
        self.sample = sample
        self.stored_file = Path(STORED_FILE)

    def ensure_index(self):
        """Create Pinecone index if not exists"""
        if self.index_name not in [idx["name"] for idx in pc.list_indexes()]:
            pc.create_index(
                name=self.index_name,
                dimension=self.vdb_dim,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1"),
            )
        return pc.Index(self.index_name)

    def read_text_file(self, file_path: Path) -> str:
        """Read file content."""
        return file_path.read_text(encoding="utf-8")

    def read_json_file(self, file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data

    def load_stored(self):
        """Load already stored disorders from file."""
        if self.stored_file.exists():
            with open(self.stored_file, "r", encoding="utf-8") as f:
                return set(json.load(f))
        return set()

    def update_stored(self, disorder_name):
        """Add a disorder to the local file."""
        stored = self.load_stored()
        stored.add(disorder_name)
        with open(self.stored_file, "w", encoding="utf-8") as f:
            json.dump(list(stored), f, indent=2)

    def ascii_id(self, s: str) -> str:
        s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
        s = re.sub(r"[^a-zA-Z0-9_-]", "_", s)
        return s

    def embed_text(self, text: str):
        """Create embeddings from text."""
        if self.model_type == "OpenAI":
            emb = openai_client.embeddings.create(
                model=self.embed_model,
                input=text
            )
            return emb.data[0].embedding
        elif self.model_type == "SentenceTransformer":
            if not self.model:
                print(f"Initializing Model")
                self.model = SentenceTransformer(self.embed_model, device="cuda")
            vector = self.model.encode(text, convert_to_tensor=False).tolist()
            return vector



    def process(self, file_path: Path, isStore=False):
        """Process one disorder file and upsert into Pinecone."""
        disorder_criterias = self.read_json_file(file_path)
        stored_disorders = self.load_stored()

        for each in disorder_criterias:
            disorder_name = each["disorder"]

            if disorder_name in stored_disorders:
                print(f"Skipping already stored disorder: {disorder_name}")
                continue

            self.criteria = each["criteria"]

            print(f"Disorder: {disorder_name} | Token Count: {count_tokens(self.criteria)}")

            self.embedding = self.embed_text(self.criteria)
            try:
                print(f"Embedding dimension: {len(self.embedding)}")
            except Exception as e:
                print(e)
                sys.exit()

            if isStore:
                self.store(disorder_name, file_path)
                self.update_stored(disorder_name)


    def store(self, disorder_name, file_path: Path):
        self.index = self.ensure_index()
        self.index.upsert(
            vectors=[
                {
                    "id": self.ascii_id(disorder_name),
                    "values": self.embedding,
                    "metadata": {
                        "file": str(file_path),
                        "diagnostic_criteria": self.criteria,
                    },
                }
            ]
        )
        print(f"Stored diagnostic criteria for: {disorder_name}")


    def run(self):
        input_dir = Path(INPUT_DIR)
        count = 0

        for file_path in input_dir.glob("*.json"):
            if count == self.sample:
                break
            self.process(file_path, isStore=True)

            count += 1

# ========= CONFIG =========
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

STORED_FILE = "indexed_disorders.json"
INDEX_NAME = "deepheal-disorders"
INPUT_DIR = "docs/criteria4"   # folder with .txt files
OPENAI_EMBED_MODEL = "text-embedding-3-large"
# SENTENCE_TRANSFORMER_EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
SENTENCE_TRANSFORMER_EMBED_MODEL = "BAAI/bge-large-en-v1.5"

# ==========================

# init clients
openai_client = OpenAI(api_key=OPENAI_API_KEY)
pc = Pinecone(api_key=PINECONE_API_KEY)


if __name__ == "__main__":
    vdb = VDB(model="SentenceTransformer")
    vdb.run()
