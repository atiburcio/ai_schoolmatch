from __future__ import annotations

import argparse
import warnings

warnings.filterwarnings('ignore', message='typing.NotRequired is not a Python type')
warnings.filterwarnings('ignore', category=UserWarning, module='pydantic._internal._generate_schema')

from langsmith import tracing_context

from db.college_vector_store import CollegeVectorStore
from langchain_app.school_matcher_graph import (
    create_graph_config,
    create_school_matcher_graph,
    run_school_matcher,
)


def main() -> None:
    parser = argparse.ArgumentParser(prog="schoolmatch")
    parser.add_argument(
        "--school",
        required=True,
        help="Free-text description of the target institution",
    )
    args = parser.parse_args()

    with tracing_context(project_name="schoolmatch"):
        vector_store = CollegeVectorStore()
        graph = create_school_matcher_graph(vector_store)
        run_school_matcher(graph, args.school, create_graph_config())


if __name__ == "__main__":
    main()
