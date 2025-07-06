@echo off
REM CPU-only installation script for RAG Backend API (Windows)

echo 🚀 Setting up RAG Backend API (CPU-only version)...

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.11+ first.
    pause
    exit /b 1
)

REM Get Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set python_version=%%i
echo 📍 Using Python %python_version%

REM Create virtual environment if it doesn't exist
if not exist "venv\" (
    echo 🔧 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo ⚡ Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo 📦 Upgrading pip...
pip install --upgrade pip

REM Install CPU-only PyTorch first
echo 🧠 Installing CPU-only PyTorch...
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

REM Install other dependencies
echo 📚 Installing other dependencies...
pip install -r requirements-cpu.txt

REM Check if .env file exists
if not exist ".env" (
    if exist ".env.example" (
        echo ⚙️  Creating .env file from example...
        copy .env.example .env
        echo 📝 Please edit .env file and add your OpenAI API key
    ) else (
        echo 📝 Please create a .env file with your OpenAI API key:
        echo OPENAI_API_KEY=your_actual_api_key_here
    )
)

REM Check if database exists
if not exist "chroma_db_claude_NBC_2020\" (
    echo 🗄️  Database not found. Creating database...
    python create_database.py
) else if not exist "chroma_db_claude_NBC_2020\chroma.sqlite3" (
    echo 🗄️  Database incomplete. Creating database...
    python create_database.py
) else (
    echo ✅ Database already exists
)

echo 🎉 Installation complete!
echo.
echo Next steps:
echo 1. Edit .env file and add your OpenAI API key
echo 2. Run 'python start_server.py' to start the API server
echo 3. Run 'streamlit run streamlit_ui.py' for the web interface
echo.
echo API will be available at: http://localhost:8000
echo Web interface at: http://localhost:8501
echo.
pause
