# SchoolMatch AI

An intelligent college merger analysis system built with LangGraph and LangChain that helps evaluate potential college partnerships and mergers. The system uses advanced language models to analyze compatibility between institutions and provide detailed recommendations.

## Features

- Comprehensive merger analysis pipeline:
  - Feature extraction from target institution
  - Compatibility analysis with potential partners
  - Recommendation formatting
  - Final recommendation with human feedback loop
- Detailed compatibility analysis including:
  - Strategic fit assessment (40%)
  - Cultural alignment evaluation (30%)
  - Operational feasibility analysis (30%)
- Vector-based college matching using ChromaDB
- Interactive human feedback system
- Structured recommendations with:
  - Key synergies identification
  - Risk assessment
  - Potential challenges
  - Compatibility scores

## Architecture
![SchoolMatch AI Architecture](schoolmatch_v1/data/schoolmatch_graph.png)

## Setup

1. Create a virtual environment:
```bash
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
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

- `langchain_app/`: Core application logic
  - `nodes/`: LangGraph node implementations
    - `compatibility_analyzer/`: Analyzes compatibility between institutions
    - `extract_target_features/`: Extracts relevant features from target institution
    - `final_rec/`: Generates final recommendation
    - `human_feedback/`: Handles human feedback loop
    - `rec_formatter/`: Formats recommendations
  - `school_matcher_graph.py`: Main LangGraph workflow definition
  - `utils/`: Utility functions and helpers
- `models/`: Data models and state definitions
  - `state.py`: Core state model and node names
  - `analysis_state.py`: Analysis-specific models
- `db/`: Database operations
  - `college_vector_store.py`: ChromaDB vector store operations
- `notebooks/`: Jupyter notebooks for demos and testing
  - `school_matcher_demo.ipynb`: Main demo notebook

## Usage

### Using the Demo Notebook

1. Open `school_matcher_demo.ipynb`
2. Run all cells to initialize the graph and components
3. Input a target institution name
4. Review the analysis results and provide feedback when prompted

The system will:
1. Extract key features from the target institution
2. Find and analyze potential partner institutions
3. Generate formatted recommendations
4. Provide a final recommendation
5. Allow for human feedback to refine the recommendation

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
