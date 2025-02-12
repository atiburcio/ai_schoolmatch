"""
Merger Analysis Module

This module provides functionality for analyzing potential mergers between educational institutions.
It uses LangChain for natural language processing and ChromaDB for vector similarity search.
"""

from typing import Callable
from langchain.prompts.chat import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from models import (
    AnalysisState,
)
from langchain_app.nodes.extract_target_features.prompt import HUMAN_TEMPLATE, SYSTEM_TEMPLATE


