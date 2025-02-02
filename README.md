# SchoolMatch AI

An intelligent college recommendation system built with LangGraph and LangChain that helps find similar colleges based on preferences. The system uses advanced language models and vector similarity search to provide personalized college recommendations.

## Features

- Find similar colleges based on multiple criteria including:
  - School type (public/private)
  - Size category
  - Academic reputation
  - Location type
  - Cost category
  - Key academic programs
- Vector database storage for efficient similarity search
- Interactive feedback system to refine recommendations
- LangGraph Studio integration for workflow visualization and debugging
- FastAPI backend for API access

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
Create a `.env` file with your API keys and configuration:
```
OPENAI_API_KEY=your_openai_api_key
LANGCHAIN_API_KEY=your_langchain_api_key
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
LANGCHAIN_PROJECT=schoolmatch-ai
```

## Project Structure

- `langchain_app/`: Contains the core recommendation engine and LangGraph workflow
  - `school_matcher.py`: Main recommendation logic
  - `cli.py`: Command-line interface
- `models/`: Data models for college information
- `db/`: Vector database operations for college similarity search
- `api/`: FastAPI endpoints for web access
- `scripts/`: Utility scripts including database population
- `chroma_db/`: Vector database storage

## Usage

1. Populate the college database:
```bash
python scripts/populate_colleges.py
```

2. Run the recommendation system:
```python
from langchain_app.school_matcher import get_school_recommendations

# Get recommendations with interactive feedback
recommendations = get_school_recommendations(
    school_name="Your Target School",
    interactive=True
)
```

3. View traces and debug workflows in LangGraph Studio at [smith.langchain.com](https://smith.langchain.com)
