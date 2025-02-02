import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
from models.college import College

class CollegeVectorStore:
    def __init__(self, persist_directory: str = "./chroma_db"):
        self.client = chromadb.Client(Settings(
            persist_directory=persist_directory,
            is_persistent=True
        ))
        self.collection = self.client.get_or_create_collection("colleges")

    def _clean_metadata(self, value: Any) -> str:
        """Convert None values to empty string and all other values to string."""
        return str(value) if value is not None else ""

    def add_college(self, college: College):
        """Add a college to the vector store."""
        self.collection.add(
            documents=[college.description],
            metadatas=[{
                "name": college.name,
                "location": college.location,
                "state": college.state,
                "type": college.type,
                "total_enrollment": str(college.total_enrollment),
                "acceptance_rate": str(college.acceptance_rate),
                "tuition_in_state": str(college.tuition_in_state),
                "tuition_out_state": str(college.tuition_out_state),
                "programs": ",".join(college.programs),
                "student_faculty_ratio": str(college.student_faculty_ratio),
                "graduation_rate": str(college.graduation_rate),
                "campus_setting": college.campus_setting,
                "athletics_division": college.athletics_division,
                "housing_available": str(college.housing_available),
                "notable_features": ",".join(college.notable_features),
                "median_sat_score": self._clean_metadata(college.median_sat_score),
                "median_act_score": self._clean_metadata(college.median_act_score),
                "ranking_national": self._clean_metadata(college.ranking_national)
            }],
            ids=[college.id]
        )

    def find_similar_colleges(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Find colleges similar to the query description."""
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        return [
            {
                "id": id,
                "metadata": metadata,
                "distance": distance
            }
            for id, metadata, distance in zip(
                results["ids"][0],
                results["metadatas"][0],
                results["distances"][0]
            )
        ]

    def find_colleges_by_criteria(
        self,
        state: Optional[str] = None,
        type: Optional[str] = None,
        max_tuition: Optional[int] = None,
        min_acceptance_rate: Optional[float] = None,
        max_acceptance_rate: Optional[float] = None,
        programs: Optional[List[str]] = None,
        campus_setting: Optional[str] = None,
        athletics_division: Optional[str] = None,
        min_sat_score: Optional[int] = None,
        max_sat_score: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Find colleges matching specific criteria."""
        # Get all colleges first
        all_colleges = self.collection.get(include=['metadatas', 'documents'])
        matching_colleges = []
        
        for i, metadata in enumerate(all_colleges["metadatas"]):
            matches_criteria = True
            
            if state and metadata["state"] != state:
                matches_criteria = False
            if type and metadata["type"] != type:
                matches_criteria = False
            if max_tuition and int(metadata["tuition_in_state"]) > max_tuition:
                matches_criteria = False
            if min_acceptance_rate and float(metadata["acceptance_rate"]) < min_acceptance_rate:
                matches_criteria = False
            if max_acceptance_rate and float(metadata["acceptance_rate"]) > max_acceptance_rate:
                matches_criteria = False
            if programs and not any(prog in metadata["programs"] for prog in programs):
                matches_criteria = False
            if campus_setting and metadata["campus_setting"] != campus_setting:
                matches_criteria = False
            if athletics_division and metadata["athletics_division"] != athletics_division:
                matches_criteria = False
            if min_sat_score and metadata["median_sat_score"] and int(metadata["median_sat_score"]) < min_sat_score:
                matches_criteria = False
            if max_sat_score and metadata["median_sat_score"] and int(metadata["median_sat_score"]) > max_sat_score:
                matches_criteria = False
            
            if matches_criteria:
                matching_colleges.append({
                    "id": all_colleges["ids"][i],
                    "metadata": metadata,
                    "description": all_colleges["documents"][i]
                })
        
        return matching_colleges

    def get_college(self, college_id: str) -> Dict[str, Any]:
        """Get a college by its ID."""
        result = self.collection.get(
            ids=[college_id],
            include=['metadatas', 'documents']
        )
        if not result['ids']:
            return None
        return {
            "id": result["ids"][0],
            "metadata": result["metadatas"][0],
            "description": result["documents"][0]
        }

    def update_college(self, college: College) -> None:
        """Update a college's information in the vector store."""
        existing_college = self.get_college(college.id)
        if not existing_college:
            raise ValueError(f"College with ID {college.id} not found")
        
        self.delete_college(college.id)
        self.add_college(college)

    def delete_college(self, college_id: str) -> None:
        """Delete a college from the vector store."""
        self.collection.delete(ids=[college_id])

    def get_all_colleges(self) -> List[Dict[str, Any]]:
        """Get all colleges in the vector store."""
        result = self.collection.get(include=['metadatas', 'documents'])
        return [
            {
                "id": id,
                "metadata": metadata,
                "description": document
            }
            for id, metadata, document in zip(
                result["ids"],
                result["metadatas"],
                result["documents"]
            )
        ]
