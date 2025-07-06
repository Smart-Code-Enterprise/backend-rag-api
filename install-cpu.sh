#!/bin/bash
# CPU-only installation script for RAG Backend API

echo "🚀 Setting up RAG Backend API (CPU-only version)..."

# Check if Python is available
if ! command -v python &> /dev/null; then
    echo "❌ Python is not installed. Please install Python 3.11+ first."
    exit 1
fi

# Check Python version
python_version=$(python -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "📍 Using Python $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "🔧 Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "⚡ Activating virtual environment..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install CPU-only PyTorch first
echo "🧠 Installing CPU-only PyTorch..."
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Install other dependencies
echo "📚 Installing other dependencies..."
pip install -r requirements-cpu.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo "⚙️  Creating .env file from example..."
        cp .env.example .env
        echo "📝 Please edit .env file and add your OpenAI API key"
    else
        echo "📝 Please create a .env file with your OpenAI API key:"
        echo "OPENAI_API_KEY=your_actual_api_key_here"
    fi
fi

# Check if database exists
if [ ! -d "chroma_db_claude_NBC_2020" ] || [ ! -f "chroma_db_claude_NBC_2020/chroma.sqlite3" ]; then
    echo "🗄️  Database not found. Creating database..."
    python create_database.py
else
    echo "✅ Database already exists"
fi

echo "🎉 Installation complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file and add your OpenAI API key"
echo "2. Run 'python start_server.py' to start the API server"
echo "3. Run 'streamlit run streamlit_ui.py' for the web interface"
echo ""
echo "API will be available at: http://localhost:8000"
echo "Web interface at: http://localhost:8501"
