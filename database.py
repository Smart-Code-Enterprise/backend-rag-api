import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings
import sys
import torch

# Force CPU usage for all torch operations
torch.set_default_device('cpu')
torch.set_num_threads(1)  # Optimize for CPU usage

# Try to use pysqlite3 if available, otherwise fall back to sqlite3
try:
    __import__('pysqlite3')
    import pysqlite3
    sys.modules['sqlite3'] = sys.modules["pysqlite3"]
except ImportError:
    # Fall back to standard sqlite3 if pysqlite3 is not available
    import sqlite3

from langchain_chroma import Chroma

class DocumentDatabase:
    def __init__(self, persist_directory="./chroma_db_claude"):
        self.persist_directory = persist_directory
        # Force CPU-only embeddings with explicit device configuration
        self.embedding_function = SentenceTransformerEmbeddings(
            model_name="all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}
        )
        self.db_path = os.path.join(self.persist_directory, "chroma_db_claude")
        self.pages = []
        
        # TODO: Convert to in-memory database for production deployment
        # For production, consider using: 
        # self.db = Chroma(embedding_function=self.embedding_function)  # In-memory only
        # Current implementation uses persistent storage (chroma_db_claude_NBC_2020/ is gitignored)
        self.db = Chroma(persist_directory=self.persist_directory, embedding_function=self.embedding_function)
    def add_document(self,Document):
        self.db.add_documents(Document)
    def load_database(self):
        self.db = Chroma(persist_directory=self.persist_directory , embedding_function=self.embedding_function)
    def similarity_search(self, query, k=20):
        return self.db.similarity_search(query,k)
    
    def return_db(self):
        return self.db