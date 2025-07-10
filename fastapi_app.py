import os
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from dotenv import load_dotenv
from openai import OpenAI
import json
import torch
from pathlib import Path


base_dir = Path(__file__).resolve().parent

# Force CPU usage for all torch operations
torch.set_default_device('cpu')
torch.set_num_threads(1)  # Optimize for CPU usage

from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever
from sentence_transformers import CrossEncoder
from utils import make_prompt, load_json_file
from database import DocumentDatabase
from langchain_core.documents.base import Document

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('fastapi_app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
logger.info("Environment variables loaded")

# Configure OpenAI API
try:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    logger.info("OpenAI client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize OpenAI client: {e}")
    raise

# Initialize FastAPI app
app = FastAPI(title="RAG Core Service", description="Building Code Q&A API", version="1.0.0")
logger.info("FastAPI app initialized")

# Global variables for cached resources
db = None
model = None
bm25_retriever = None
document_objects = []

class Reference(BaseModel):
    ref_num: str
    page: int

class QueryRequest(BaseModel):
    User_question: str = Field(..., description="The user's question")
    Rerank: bool = Field(False, description="Enable re-ranking")
    Hybrid_search: float = Field(0.4, ge=0.0, le=1.0, description="Weight for BM25 retriever (0-1)")
    LLM: str = Field("o4-mini", description="LLM model to use")

class QueryResponse(BaseModel):
    content: str
    resp: str
    refs: List[Reference]
    book_name: str = "OBC2014"

def load_model():
    """Load the CrossEncoder model for re-ranking (CPU-only)"""
    try:
        logger.info("Loading CrossEncoder model for CPU-only operation...")
        # Force CPU usage for the CrossEncoder model
        model = CrossEncoder("mixedbread-ai/mxbai-rerank-base-v1", device='cpu')
        logger.info("CrossEncoder model loaded successfully on CPU")
        return model
    except Exception as e:
        logger.error(f"Failed to load CrossEncoder model: {e}")
        raise

def load_database():
    """Load the document database"""
    try:
        logger.info("Loading document database...")
        db_path = base_dir / "chroma_db_claude_NBC_2020"
        
        # Check if database exists
        if not os.path.exists(db_path) or not os.path.exists(os.path.join(db_path, "chroma.sqlite3")):
            logger.error(f"Database not found at {db_path}")
            logger.error("Please run 'python create_database.py' to create the database first")
            raise FileNotFoundError(f"Database not found at {db_path}. Run 'python create_database.py' to create it.")
        
        database = DocumentDatabase(persist_directory=str(db_path))
        db = database.return_db()
        logger.info("Document database loaded successfully")
        return db
    except Exception as e:
        logger.error(f"Failed to load document database: {e}")
        raise

def initialize_resources():
    """Initialize all resources needed for the RAG system"""
    global db, model, bm25_retriever, document_objects
    
    try:
        logger.info("Starting resource initialization...")
        
        # Load database and model
        logger.info("Loading database...")
        db = load_database()
        logger.info("Database loaded successfully")
        
        logger.info("Loading model...")
        model = load_model()
        logger.info("Model loaded successfully")
          # Load JSON data and create BM25 retriever
        logger.info("Loading JSON data...")
        file_path = './data/extracted_clauses_OBC_2020.json'
        
        # Check if JSON file exists
        if not os.path.exists(file_path):
            logger.error(f"JSON data file not found at {file_path}")
            raise FileNotFoundError(f"JSON data file not found at {file_path}")
        
        data_dict = load_json_file(file_path)
        logger.info(f"JSON data loaded successfully. Found {len(data_dict)} entries")
        
        logger.info("Creating document objects...")
        document_objects = []
        for i, entry in enumerate(data_dict):
            try:
                for clause in entry['clauses']:
                    metadata = {
                        'section': entry['section'],
                        'title': entry['title'].strip(),
                        'page_num': entry['page_num']
                    }
                    clause = [item for item in clause if item is not None]
                    document = Document(
                        page_content=entry['title'] + ' ' + ' '.join(clause), 
                        metadata=metadata
                    )
                    document_objects.append(document)
            except Exception as e:
                logger.warning(f"Error processing entry {i}: {e}")
                continue
        
        logger.info(f"Created {len(document_objects)} document objects")
        
        logger.info("Creating BM25 retriever...")
        bm25_retriever = BM25Retriever.from_documents(document_objects)
        logger.info("BM25 retriever created successfully")
        
        logger.info("Resource initialization completed successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize resources: {e}")
        raise

@app.on_event("startup")
async def startup_event():
    """Initialize resources on startup"""
    try:
        logger.info("Starting FastAPI application startup...")
        initialize_resources()
        logger.info("FastAPI application startup completed successfully")
    except Exception as e:
        logger.error(f"FastAPI application startup failed: {e}")
        raise

@app.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """
    Process a query against the document database
    """
    try:
        logger.info(f"Received query request: {request.User_question}")
        logger.info(f"Query parameters - Rerank: {request.Rerank}, Hybrid_search: {request.Hybrid_search}, LLM: {request.LLM}")
        
        # Validate that resources are loaded
        if db is None or model is None or bm25_retriever is None:
            logger.error("Resources not properly initialized")
            raise HTTPException(status_code=500, detail="Resources not properly initialized")
        
        logger.info("Setting up retrievers...")
        # Set up retrievers
        try:
            retriever_chroma = db.as_retriever(search_kwargs={"k": 100})
            weights = [request.Hybrid_search, 1.0 - request.Hybrid_search]
            ensemble_retriever = EnsembleRetriever(
                retrievers=[bm25_retriever, retriever_chroma], 
                weights=weights
            )
            logger.info(f"Ensemble retriever created with weights: {weights}")
        except Exception as e:
            logger.error(f"Failed to set up retrievers: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to set up retrievers: {e}")
        
        # Retrieve documents
        logger.info("Retrieving documents...")
        try:
            docs = ensemble_retriever.invoke(request.User_question)
            logger.info(f"Retrieved {len(docs)} documents")
        except Exception as e:
            logger.error(f"Failed to retrieve documents: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to retrieve documents: {e}")
        
        if not docs:
            logger.warning("No relevant documents found")
            return QueryResponse(
                content="No relevant documents found.",
                resp="No relevant documents found.",
                refs=[],
                book_name="OBC2014"
            )
        
        # Apply re-ranking if enabled
        if request.Rerank:
            logger.info("Applying re-ranking...")
            try:
                documents = [doc.page_content for doc in docs]
                ranked_indices = model.rank(
                    request.User_question, 
                    documents, 
                    return_documents=False, 
                    top_k=5
                )
                indices = [ranked_indice['corpus_id'] for ranked_indice in ranked_indices]
                ranked_docs = [docs[idx] for idx in indices]
                logger.info(f"Re-ranking completed. Top 5 documents selected from {len(docs)} candidates")
            except Exception as e:
                logger.error(f"Failed to apply re-ranking: {e}")
                raise HTTPException(status_code=500, detail=f"Failed to apply re-ranking: {e}")
        else:
            ranked_docs = docs[:5]
            logger.info(f"Using top 5 documents without re-ranking")
        
        # Generate response using OpenAI
        logger.info("Generating response using OpenAI...")
        try:
            combined_text = " ".join([d.page_content for d in ranked_docs])
            prompt = make_prompt(request.User_question, combined_text)
            logger.info(f"Generated prompt with {len(combined_text)} characters")
        except Exception as e:
            logger.error(f"Failed to create prompt: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to create prompt: {e}")
        try:
            # Use chat completions API (recommended approach)
            logger.info(f"Making OpenAI API call with model: {request.LLM}")
            
            # Handle different parameter names for different models
            if request.LLM in ["o1-preview", "o1-mini", "o4-mini"]:
                # New models use max_completion_tokens instead of max_tokens
                response = client.responses.create(
                model="o4-mini",
                input=[
                    {
                        "role": "developer",
                        "content": "Talk like a architect engineer. if not sure about the answer, please response dont know"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            # else:
            #     # Traditional models use max_tokens
            #     response = client.chat.completions.create(
            #         model=request.LLM,
            #         messages=[
            #             {
            #                 "role": "system",
            #                 "content": "Talk like an architect engineer. If not sure about the answer, please respond 'don't know'"
            #             },
            #             {
            #                 "role": "user",
            #                 "content": prompt
            #             }
            #         ],
            #         max_tokens=1500,
            #         temperature=0.3
            #     )
            
            answer = response.output_text
            logger.info("OpenAI API call completed successfully")
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")
        
        # Extract references from ranked documents
        logger.info("Extracting references...")
        try:
            refs = []
            for doc in ranked_docs:
                ref = Reference(
                    ref_num=doc.metadata.get('section', 'Unknown'),
                    page=doc.metadata.get('page_num', 0)
                )
                refs.append(ref)
            logger.info(f"Extracted {len(refs)} references")
        except Exception as e:
            logger.error(f"Failed to extract references: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to extract references: {e}")
        
        logger.info("Query processing completed successfully")
        return QueryResponse(
            content=answer,
            resp=answer,
            refs=refs,
            book_name="OBC2014"
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions as they are
        raise
    except Exception as e:
        logger.error(f"Unexpected error in query processing: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        logger.info("Health check requested")
        # Check if resources are initialized
        resources_status = {
            "db": db is not None,
            "model": model is not None,
            "bm25_retriever": bm25_retriever is not None
        }
        logger.info(f"Resource status: {resources_status}")
        
        if all(resources_status.values()):
            return {"status": "healthy", "message": "RAG Core Service is running", "resources": resources_status}
        else:
            return {"status": "partial", "message": "Some resources not initialized", "resources": resources_status}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "unhealthy", "message": f"Health check failed: {e}"}

@app.get("/")
async def root():
    """Root endpoint with API information"""
    logger.info("Root endpoint accessed")
    return {
        "message": "RAG Core Service API",
        "version": "1.0.0",
        "endpoints": {
            "query": "/query",
            "health": "/health",
            "docs": "/docs"
        }
    }

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting FastAPI application directly...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
