# Local Setup Script
# Run this to set up your local development environment

echo "========================================="
echo "AI RAG Agent - Local Setup"
echo "========================================="

# Check Python version
echo "Checking Python version..."
python3 --version || { echo "Python 3 not found. Please install Python 3.11+"; exit 1; }

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Edit .env and add your OPENAI_API_KEY"
    echo "   nano .env  # or use your preferred editor"
    echo ""
fi

echo "========================================="
echo "✓ Setup Complete!"
echo "========================================="
echo ""
echo "Next Steps:"
echo "1. Edit .env and add your OpenAI API key:"
echo "   nano .env"
echo ""
echo "2. Activate the virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "3. Run the application:"
echo "   uvicorn app.main:app --reload"
echo ""
echo "4. Visit http://localhost:8000/docs to see the API documentation"
echo "========================================="
