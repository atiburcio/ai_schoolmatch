# SchoolMatch AI

An intelligent college merger analysis system built with LangGraph and LangChain that helps evaluate potential college partnerships and mergers. The system uses advanced language models to analyze compatibility between institutions and provide detailed recommendations.

## Features

- Comprehensive merger analysis including:
  - Strategic fit assessment (40%)
  - Cultural alignment evaluation (30%)
  - Operational feasibility analysis (30%)
- Detailed compatibility scoring for potential partners
- Structured recommendations with:
  - Key synergies identification
  - Risk assessment
  - Financial impact analysis
- LangGraph workflow for systematic analysis
- Vector database for efficient college data storage and retrieval

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
Create a `.env` file with your API keys:
```
OPENAI_API_KEY=your_openai_api_key
```

## Project Structure

- `langchain_app/`: Core analysis engine and LangGraph workflow
  - `merger_analyzer.py`: Compatibility analysis logic
  - `school_matcher_graph.py`: LangGraph workflow definition
  - `school_matcher.py`: College matching logic
- `models/`: Data models for college information
- `db/`: Vector database operations and college data
- `scripts/`: Utility scripts for database operations
- `chroma_db/`: Vector database storage (not tracked in git)

## Running the Analysis

### Using the Jupyter Notebook

1. Start Jupyter:
```bash
jupyter notebook
```

2. Open `school_matcher_demo.ipynb`

3. Run all cells in sequence. The notebook will:
   - Initialize the LangGraph workflow
   - Load the college vector database
   - Analyze compatibility with potential partners
   - Generate a detailed recommendation

Example usage in the notebook:
```python
result = run_school_matcher(graph, "Your University Name")

# Print analyses
for analysis in result["compatibility_analyses"]:
    print(analysis)

# Print final recommendation
print("\nFinal Recommendation:")
print(result["final_recommendation"])
```

### Using the Python API

```python
from langchain_app.school_matcher import create_school_matcher_graph
from db.college_vector_store import CollegeVectorStore

# Initialize components
vector_store = CollegeVectorStore()
graph = create_school_matcher_graph(vector_store)

# Run analysis
result = graph.run({
    "messages": [{"role": "user", "content": "Your University Name"}]
})
```

## Data Storage

The system uses a ChromaDB vector database to store college information. The database files are not tracked in git due to size constraints. To set up the database:

1. Run the database population script:
```bash
python scripts/access_to_vector_mac.py.py
```

2. The script will create the necessary database files in the `chroma_db/` directory

## Notes

- The system currently uses the GPT-3.5-turbo model for analysis
- Make sure your OpenAI API key has sufficient credits
- Keep the `chroma_db/` directory in your `.gitignore` to avoid large file issues
