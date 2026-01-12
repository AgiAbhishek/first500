# AI RAG Agent - Intelligent Question-Answering System

A production-ready AI-powered question-answering system with Retrieval Augmented Generation (RAG) capabilities. Features free local embeddings, Azure OpenAI integration, and a beautiful chat interface.

## 🎯 Features

- ✨ **Free Local Embeddings** using sentence-transformers (all-MiniLM-L6-v2)
- 🤖 **Azure OpenAI Integration** for intelligent responses
- 💬 **Beautiful Chat UI** with glassmorphism design
- 📚 **RAG Pipeline** with source attribution
- 🔄 **Session Memory** for multi-turn conversations
- 🚀 **FastAPI Backend** with auto-generated docs

## 🚀 Quick Start

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Configure environment**:
```bash
cp .env.example .env
# Edit .env with your Azure OpenAI credentials
```

3. **Run the server**:
```bash
uvicorn app.main:app --reload
```

4. **Open the chat UI**:
```bash
open frontend/index.html
```

## 📡 API Endpoints

- `POST /api/ask` - Ask questions (main functionality)
- `GET /api/health` - Check service health
- `GET /docs` - Interactive API documentation

## 🎨 Chat Interface

Beautiful glassmorphism UI with:
- Animated gradient background
- Real-time messaging
- Source attribution display
- Session persistence

## 🛠️ Tech Stack

- **Backend**: FastAPI, Python 3.11+
- **AI**: Azure OpenAI (GPT), sentence-transformers
- **Vector Store**: FAISS
- **Frontend**: Vanilla JS, HTML5, CSS3

## 📄 License

MIT License
