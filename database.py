import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings
import sys

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
        self.embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
        self.db_path = os.path.join(self.persist_directory, "chroma_db_claude")
        self.pages = []
        
        # Initialize the database
        self.db = Chroma(persist_directory=self.persist_directory, embedding_function=self.embedding_function)
    def add_document(self,Document):
        self.db.add_documents(Document)
    def load_database(self):
        self.db = Chroma(persist_directory=self.persist_directory , embedding_function=self.embedding_function)
    def similarity_search(self, query, k=20):
        return self.db.similarity_search(query,k)
    
    def return_db(self):
        return self.db