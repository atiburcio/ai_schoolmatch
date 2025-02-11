import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from typing import List, Dict, Any, Optional
from models.college import College
import os
import logging

class CollegeVectorStore:
    def __init__(self, persist_directory: str = "./chroma_db"):
        # Configure ChromaDB logging
        logging.getLogger('chromadb').setLevel(logging.ERROR)
        
        # Initialize OpenAI embedding function
        self.embedding_function = embedding_functions.OpenAIEmbeddingFunction(
            api_key=os.getenv("OPENAI_API_KEY"),
            model_name="text-embedding-ada-002"
        )
        
        # Initialize Chroma client
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # Get or create collection with embedding function
        self.collection = self.client.get_or_create_collection(
            name="ipeds_colleges",
            embedding_function=self.embedding_function
        )

    def find_similar_colleges(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Find colleges similar to the query description."""
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            include=['metadatas', 'distances', 'documents']
        )
        
        return [
            {
                "id": id,
                "metadata": metadata,
                "distance": distance,
                "document": document
            }
            for id, metadata, distance, document in zip(
                results["ids"][0],
                results["metadatas"][0],
                results["distances"][0],
                results["documents"][0]
            )
        ]

    def get_all_colleges(self) -> List[Dict[str, Any]]:
        """Get all colleges in the vector store."""
        result = self.collection.get(include=['metadatas', 'documents'])
        if not result["ids"]:
            return []
            
        return [
            {
                "id": id,
                "metadata": metadata,
                "document": document
            }
            for id, metadata, document in zip(
                result["ids"],
                result["metadatas"],
                result["documents"]
            )
        ]
