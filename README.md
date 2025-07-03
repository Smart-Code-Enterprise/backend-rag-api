# RAG Backend API

A comprehensive FastAPI-based backend service for Retrieval-Augmented Generation (RAG) queries against building code documents. This API provides intelligent document search and answer generation using hybrid retrieval (BM25 + vector search) with optional re-ranking, specifically designed for Ontario Building Code (OBC).

## 🚀 Features

- **🔍 Hybrid Document Retrieval**: Combines BM25 (keyword-based) and ChromaDB vector similarity search
- **🎯 Smart Re-ranking**: Uses CrossEncoder (mixedbread-ai/mxbai-rerank-base-v1) for improved document relevance
- **🏗️ Building Code Expertise**: Specialized for Ontario Building Code (OBC 2014)
- **📊 Comprehensive Logging**: Detailed logging with file and console output for debugging and monitoring
- **🔗 RESTful API**: Clean, documented API endpoints with automatic validation
- **⚡ Real-time Processing**: Fast response times with efficient caching and resource management
- **🐳 Docker Support**: Full containerization with Docker and Docker Compose
- **🧪 Automated Testing**: Built-in test suite for API validation
- **🔧 Environment Configuration**: Flexible configuration through environment variables
- **🏥 Health Monitoring**: Comprehensive health checks and resource status reporting

## 📋 Requirements

- **Python**: 3.11+)
- **Memory**: 8GB+ RAM (for model loading and processing)
- **GPU**: If want to use rerank model for high accuracy search 
- **API Key**: OpenAI API key with sufficient credits

## 📁 Project Structure

```
backend-rag-api/
├── fastapi_app.py          # Main FastAPI application
├── start_server.py         # Server startup script
├── create_database.py      # Database creation script
├── database.py            # Database management
├── utils.py               # Utility functions
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker configuration
├── docker-compose.yml    # Docker Compose setup
├── .env.example          # Environment variables template
├── README.md             # This file
├── data/                 # Document data
│   ├── extracted_clauses_OBC_2020.json
│   ├── OBC-2014.pdf
│   └── NBC 2020.pdf
└── chroma_db_claude_NBC_2020/  # Vector database (created by create_database.py)
    └── chroma.sqlite3
```

## 🛠️ Installation

### 1. Clone and Setup

```bash
cd backend-rag-api
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```


#### Environment Configuration

Create a `.env` file from the example:

```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:

```env
OPENAI_API_KEY=your_actual_api_key_here
```

#### Create Database (First Time Only)

If the database doesn't exist, create it from the JSON data:

```bash
python create_database.py
```

**Options:**
- `--json-file PATH`: Specify custom JSON file path
- `--db-dir PATH`: Specify custom database directory  
- `--force`: Force recreation of existing database

**Example:**
```bash
# Create with default paths
python create_database.py

# Create with custom paths
python create_database.py --json-file ./data/my_data.json --db-dir ./my_db

# Force recreation
python create_database.py --force
```

## 🚀 Quick Start

### Start the Server

```bash
python start_server.py
```

The API will be available at:
- **Main API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc


## 🖥️ Streamlit Web Interface

In addition to the REST API, a user-friendly web interface is available via Streamlit for interactive querying.

### Start the Streamlit UI

```bash
streamlit run streamlit_ui.py
```

The web interface will be available at: `http://localhost:8501`

### Usage

1. Start the FastAPI backend server (see [Quick Start](#-quick-start))
2. In a new terminal, launch the Streamlit interface:
   ```bash
   streamlit run streamlit_ui.py
   ```
3. Open your browser to `http://localhost:8501`
4. Enter your building code question and adjust settings as needed
5. Click "Submit" to get AI-powered answers with references

## 📚 API Endpoints

### 🔍 Health Check
```http
GET /health
```

**Response:**
```json
{
    "status": "healthy",
    "message": "RAG Core Service is running",
    "resources": {
        "db": true,
        "model": true,
        "bm25_retriever": true
    }
}
```

### 🤖 Query Documents
```http
POST /query
```

**Request Body:**
```json
{
    "User_question": "What are the fire safety requirements for buildings?",
    "Rerank": False,
    "Hybrid_search": 0.4,
    "LLM": "o4-mini"
}
```

**Parameters:**
- `User_question` (string, required): The question to ask
- `Rerank` (boolean, default: false): Enable document re-ranking
- `Hybrid_search` (float, 0.0-1.0, default: 0.4): Weight for BM25 retriever
- `LLM` (string, default: "o4-mini"): OpenAI model to use

**Response:**
```json
{
    "content": "According to the Ontario Building Code...",
    "resp": "According to the Ontario Building Code...",
    "refs": [
        {
            "ref_num": "9.4.4.3",
            "page": 142
        },
        {
            "ref_num": "9.7.2.1", 
            "page": 198
        }
    ],
    "book_name": "OBC2014"
}
```

### 📋 API Information
```http
GET /
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | Required |
| `HOST` | Server host | 0.0.0.0 |
| `PORT` | Server port | 8000 |
| `LOG_LEVEL` | Logging level | INFO |
| `CHROMA_DB_PATH` | ChromaDB path | ./chroma_db_claude_NBC_2020 |
| `JSON_DATA_PATH` | JSON data path | ./data/extracted_clauses_OBC_2020.json |

### Hybrid Search Weights

The `Hybrid_search` parameter controls the balance between search methods:
- **0.0**: Pure vector similarity search
- **0.5**: Balanced hybrid search  
- **1.0**: Pure BM25 keyword search
- **Recommended**: 0.4 (slight preference for BM25)


## 🐛 Troubleshooting

### Common Issues

#### 1. "Database not found" Error
**Error**: `Database not found at ./chroma_db_claude_NBC_2020`
**Solution**: Create the database first:
```bash
python create_database.py
```

#### 2. "Resources not properly initialized"
**Solution**: Check that all required files exist:
- `./chroma_db_claude_NBC_2020/` (database directory)
- `./chroma_db_claude_NBC_2020/chroma.sqlite3` (database file)
- `./data/extracted_clauses_OBC_2020.json` (data file)

If missing, run:
```bash
python create_database.py
```

#### 3. "JSON data file not found"
**Solution**: Ensure the data file exists at `./data/extracted_clauses_OBC_2020.json`

#### 4. "OpenAI API error"
**Solutions**:
- Verify your API key in `.env`
- Check your OpenAI account credits
- Ensure model name is correct

#### 5. "ModuleNotFoundError"
**Solution**: Install missing dependencies:
```bash
pip install -r requirements.txt
```

#### 6. Out of Memory Errors
**Solutions**:
- Reduce batch size in retrieval
- Use CPU instead of GPU
- Close other applications

### Logs and Debugging

Check the logs for detailed error information:
- **Console**: Real-time logs during operation
- **File**: `fastapi_app.log` (persistent logs)

Enable debug logging:
```bash
LOG_LEVEL=DEBUG python start_server.py
```

### Manual Testing
```bash
# Health check
curl http://localhost:8000/health

# Simple query
curl -X POST "http://localhost:8000/query" \
     -H "Content-Type: application/json" \
     -d '{"User_question": "What are building height limits?", "LLM": "o4-mini"}'
```


## 🔄 Updates

Stay updated with the latest changes:
- Monitor OpenAI API updates for new models
- Update dependencies regularly: `pip install --upgrade -r requirements.txt`
- Check for ChromaDB updates for performance improvements
