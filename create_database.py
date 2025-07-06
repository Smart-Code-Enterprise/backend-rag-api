#!/usr/bin/env python3
"""
Database creation script for RAG Backend API (CPU-only version)
Creates ChromaDB vector database from JSON document data if it doesn't exist.
"""
import os
import json
import logging
from pathlib import Path
import torch

# Force CPU usage for all torch operations
torch.set_default_device('cpu')
torch.set_num_threads(1)  # Optimize for CPU usage

from langchain_core.documents.base import Document
from database import DocumentDatabase

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('create_database.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def load_json_file(file_path):
    """Load and return JSON data from a given file path."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        logger.info(f"Successfully loaded JSON data from {file_path}")
        return data
    except Exception as e:
        logger.error(f"Failed to load JSON file {file_path}: {e}")
        raise

def find_depth(data):
    """Recursively find the maximum depth of the data structure."""
    if isinstance(data, dict):
        return 1 + max((find_depth(value) for value in data.values()), default=0)
    elif isinstance(data, list):
        return max((find_depth(item) for item in data), default=0)
    return 0

def check_database_exists(directory):
    """Check if the database directory exists and contains database files."""
    db_path = Path(directory)
    if not db_path.exists():
        return False
    
    # Check for ChromaDB files
    sqlite_file = db_path / "chroma.sqlite3"
    return sqlite_file.exists()

def process_and_add_to_db(json_file_path=None, db_directory=None):
    """Process JSON data from file and add documents to the database."""
    
    # Set default paths relative to the script location
    script_dir = Path(__file__).parent
    
    if json_file_path is None:
        json_file_path = script_dir / "data" / "extracted_clauses_OBC_2020.json"
    
    if db_directory is None:
        db_directory = script_dir / "chroma_db_claude_NBC_2020"
    
    # Convert to string paths for compatibility
    json_file_path = str(json_file_path)
    db_directory = str(db_directory)
    
    logger.info(f"JSON file path: {json_file_path}")
    logger.info(f"Database directory: {db_directory}")
    
    # Check if database already exists
    if check_database_exists(db_directory):
        logger.info(f"Database already exists at {db_directory}")
        response = input("Database already exists. Do you want to recreate it? (y/N): ")
        if response.lower() != 'y':
            logger.info("Database creation cancelled by user")
            return
        else:
            logger.info("User chose to recreate the database")
    
    # Check if JSON file exists
    if not os.path.exists(json_file_path):
        logger.error(f"JSON file not found: {json_file_path}")
        raise FileNotFoundError(f"JSON file not found: {json_file_path}")
    
    # Load JSON data
    logger.info("Loading JSON data...")
    data_dict = load_json_file(json_file_path)
    logger.info(f"Loaded {len(data_dict)} entries from JSON file")
    
    # Process documents
    logger.info("Processing documents...")
    document_objects = []
    
    for i, entry in enumerate(data_dict):
        try:
            # Handle different JSON structures
            if 'clauses' in entry:
                for clause in entry['clauses']:
                    metadata = {
                        'section': entry.get('section', 'Unknown'),
                        'title': entry.get('title', '').strip(),
                        'page_num': entry.get('page_num', 0)
                    }
                    
                    # Clean clause data - remove None values
                    if isinstance(clause, list):
                        clause_text = ' '.join([str(item) for item in clause if item is not None])
                    else:
                        clause_text = str(clause) if clause is not None else ''
                    
                    # Create document content
                    content = f"{entry.get('section', '')} {entry.get('title', '')} {clause_text}".strip()
                    
                    if content:  # Only add non-empty content
                        document = Document(
                            page_content=content, 
                            metadata=metadata
                        )
                        document_objects.append(document)
            else:
                # Handle simpler JSON structure
                metadata = {
                    'section': entry.get('section', 'Unknown'),
                    'title': entry.get('title', '').strip(),
                    'page_num': entry.get('page_num', 0)
                }
                
                content = str(entry.get('content', '')).strip()
                if content:
                    document = Document(
                        page_content=content,
                        metadata=metadata
                    )
                    document_objects.append(document)
                    
        except Exception as e:
            logger.warning(f"Error processing entry {i}: {e}")
            continue
    
    logger.info(f"Created {len(document_objects)} document objects")
    
    if not document_objects:
        logger.error("No valid documents found to add to database")
        return
    
    # Create database and add documents
    logger.info("Creating database and adding documents...")
    try:
        db = DocumentDatabase(persist_directory=db_directory)
        db.add_document(document_objects)
        logger.info(f"Successfully created database at {db_directory}")
        logger.info(f"Added {len(document_objects)} documents to the database")
    except Exception as e:
        logger.error(f"Failed to create database: {e}")
        raise

def main():
    """Main function to create database with command line options."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Create ChromaDB database from JSON data')
    parser.add_argument('--json-file', type=str, help='Path to JSON file containing document data')
    parser.add_argument('--db-dir', type=str, help='Directory to store the database')
    parser.add_argument('--force', action='store_true', help='Force recreation of existing database')
    
    args = parser.parse_args()
    
    try:
        # Set paths
        json_file_path = args.json_file
        db_directory = args.db_dir
        
        # If force is specified, skip the interactive check
        if args.force:
            logger.info("Force flag specified, will recreate database if it exists")
        
        # Create database
        process_and_add_to_db(json_file_path, db_directory)
        
        logger.info("Database creation completed successfully!")
        
    except Exception as e:
        logger.error(f"Database creation failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
