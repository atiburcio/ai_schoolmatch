# Book Comparison Agent

An agentic system built with LangGraph for comparing books based on various criteria including genre, publish date, page count, and description.

## Features

- Compare books using multiple criteria
- Vector database storage for efficient similarity search
- Agentic system for intelligent book matching
- Interactive user interface for querying book matches

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file with your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

## Project Structure

- `agents/`: Contains agent definitions and tools
- `models/`: Data models and schemas
- `db/`: Vector database operations
- `api/`: FastAPI endpoints
- `utils/`: Utility functions
