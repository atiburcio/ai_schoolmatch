# SchoolMatch AI

An AI-powered tool for identifying potential merger and acquisition (M&A) partners for educational institutions, leveraging LangChain, LangGraph, and Deep Agents for intelligent analysis and recommendations.

## Overview

The system follows a structured workflow:

1. Feature Extraction
   - Analyzes input institution details
   - Identifies key characteristics and requirements
   - Extracts searchable features

2. Semantic Search using IPEDS Vector Store
   - Performs semantic search across potential partners
   - Evaluates strategic alignment
   - Generates detailed similarity scores
   - Considers multiple dimensions:
     - Financial compatibility
     - Academic program alignment
     - Cultural fit
     - Market positioning

3. Recommendation Generation
   - Formats detailed analyses for each potential partner
   - Generates comprehensive M&A recommendations
   - Provides structured reports with:
     - Executive summaries
     - Strategic rationale
     - Risk assessments
     - Next steps

4. Web Search (Deep Agents)
   - Uses a Deep Agent with a `web-research` skill for higher-ed due diligence
   - Progressively discloses research instructions via the skill system
   - Integrates search results directly into the recommendation process
   - Provides up-to-date information to the user

5. Interactive Feedback
   - Collects user feedback on recommendations
   - Refines suggestions based on input
   - Allows for iterative improvement

## Architecture
![SchoolMatch AI Architecture](data/schoolmatch_graph.png)

## Technologies

- **LangChain v1**: Framework for LLM application development
- **LangGraph**: For building structured AI workflows
- **Deep Agents**: For the web search node with skills-based progressive disclosure
- **ChromaDB**: Vector store for semantic search of institutions
- **Pydantic v2**: For data validation and state management

## Setup

### System Requirements

1. Python 3.11
2. Access Database Engine (required for reading .accdb files):
   - Windows: Download and install [Microsoft Access Database Engine 2016](https://www.microsoft.com/en-us/download/details.aspx?id=54920)
   - Mac: Install mdbtools:
     ```bash
     brew install mdbtools
     ```

### Installation

1. Create a virtual environment:
   ```bash
   python -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Download IPEDS Data:
   - Visit the [IPEDS Data Center](https://nces.ed.gov/ipeds/use-the-data/download-access-database)
   - Download the latest Access Database (.accdb file) 2023-2024
   - Create an `ipeds_data` directory in the project root IF it does not exist:
     ```bash
     mkdir ipeds_data
     ```
   - Place the downloaded .accdb file in the `ipeds_data` directory

4. Set up environment variables:
   Create a `.env` file in the project root with:
   ```
   OPENAI_API_KEY=your_api_key_here
   LANGCHAIN_TRACING_V2=true
   LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
   LANGCHAIN_PROJECT=schoolmatch
   ```

5. Initialize the Vector Store:
   ```bash
   python scripts/optimized_access_to_vector_mac.py
   ```

6. Verify the setup:
   ```bash
   python scripts/query_vector_db.py
   ```

The system will create a `chroma_db` directory to store the vector embeddings. This only needs to be done once unless you want to update the IPEDS data.

### Troubleshooting

If you encounter any issues:
1. Ensure the IPEDS .accdb file is in the correct location
2. Check that your OpenAI API key is valid
3. Make sure all dependencies are installed
4. Verify the `chroma_db` directory was created successfully
5. For Access Database issues:
   - Windows: Make sure both 32-bit and 64-bit versions of the Access Database Engine are installed
   - Mac: Verify mdbtools is installed correctly: `brew info mdbtools`

### Data Updates

To update the college data:
1. Download a new IPEDS Access Database
2. Replace the existing .accdb file in `ipeds_data`
3. Run the initialization script again:
   ```bash
   python scripts/access_to_vector_mac.py
   ```

## Usage

### CLI

```bash
schoolmatch --school "A private liberal arts college with 2,000 students, strong humanities programs, and interest in expanding STEM offerings. Located in New England with \$50M endowment."
```

### Python

```python
from langchain_app.school_matcher_graph import (
    create_school_matcher_graph, run_school_matcher, create_graph_config
)
from db.college_vector_store import CollegeVectorStore

vector_store = CollegeVectorStore()
graph = create_school_matcher_graph(vector_store)
run_school_matcher(graph, "your school description", create_graph_config())
```

### Notebook

See `school_matcher_demo.ipynb` for an interactive walkthrough.

## Project Structure

```
schoolmatch_v1/
├── langchain_app/
│   ├── cli.py                       # CLI entry point
│   ├── school_matcher_graph.py      # Graph definition
│   ├── nodes/                       # Graph nodes
│   │   ├── extract_target_features/ # Feature extraction
│   │   ├── ipeds_semantic_search/   # Partner analysis
│   │   ├── rec_formatter/           # Recommendation formatting
│   │   ├── final_rec/               # Final recommendation
│   │   ├── web_search/              # Deep Agents web search
│   │   └── human_feedback/          # Feedback handling
│   └── utils/                       # Utility functions
├── skills/
│   └── web-research/                # Deep Agents skill for web search
│       └── SKILL.md
├── db/                              # Vector store implementation
├── models/                          # Data models and state definitions
└── data/                            # Resources and data
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request
