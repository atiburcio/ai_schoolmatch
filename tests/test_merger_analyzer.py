from langchain_openai import ChatOpenAI
from langchain_app.merger_analyzer import (
    create_feature_extractor,
    create_ipeds_semantic_search,
    create_recommendation_formatter,
    create_final_recommender
)
from db.college_vector_store import CollegeVectorStore
import os
from dotenv import load_dotenv

def test_merger_analyzer():
    # Load environment variables
    load_dotenv()
    
    # Initialize the LLM
    llm = ChatOpenAI(
        model="gpt-4",
        temperature=0,
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    # Initialize vector store
    vector_store = CollegeVectorStore(persist_directory="chroma_db")
    
    # Create all nodes
    feature_extractor = create_feature_extractor(llm)
    ipeds_semantic_search = create_ipeds_semantic_search(vector_store, llm)
    recommendation_formatter = create_recommendation_formatter(llm)
    final_recommender = create_final_recommender(llm)
    
    # Test with a sample school
    test_state = {
        "school": """
        The University of California, Berkeley is a public research university in Berkeley, California.
        Founded in 1868, it is the flagship campus of the University of California system and a founding 
        member of the Association of American Universities.
        
        Berkeley is a large, highly residential research university with a majority of its enrollment in 
        undergraduate programs. The university has been accredited by the Western Association of Schools 
        and Colleges Senior College and University Commission since 1949. The university is one of the 
        most selective in the country, with an acceptance rate around 15%.
        
        The university is well known for its STEM programs, particularly in engineering, computer science,
        chemistry, and physics. It also has strong programs in social sciences, humanities, and business.
        Berkeley's research expenditure was $1.7 billion in 2020, making it one of the largest research
        institutions in the United States.
        
        The university has approximately 31,000 undergraduate and 13,000 graduate students, with a 
        student-to-faculty ratio of about 20:1. Berkeley's athletic teams compete in Division I of the 
        NCAA as the California Golden Bears.
        """
    }
    
    print("\nTesting Merger Analyzer Pipeline...")
    
    # Test feature extractor
    print("\n1. Testing Feature Extractor...")
    try:
        state = feature_extractor(test_state)
        print("\nFeatures extracted:")
        print(state["features"])
        assert "features" in state, "Features not found in state"
    except Exception as e:
        print(f"Error in feature extractor: {str(e)}")
        return False
    
    # Test compatibility analyzer
    print("\n2. Testing Compatibility Analyzer...")
    try:
        state = ipeds_semantic_search(state)
        print(f"\nFound {len(state['analyses'])} potential partners")
        for analysis in state["analyses"]:
            print(f"\nPartner: {analysis['school']}")
            print(f"Location: {analysis['location']}")
            print(f"Similarity Score: {analysis['similarity_score']:.4f}")
        assert "analyses" in state, "Analyses not found in state"
    except Exception as e:
        print(f"Error in compatibility analyzer: {str(e)}")
        return False
    
    # Test recommendation formatter
    print("\n3. Testing Recommendation Formatter...")
    try:
        state = recommendation_formatter(state)
        print("\nRecommendations generated:")
        print(state["recommendations"])
        assert "recommendations" in state, "Recommendations not found in state"
    except Exception as e:
        print(f"Error in recommendation formatter: {str(e)}")
        return False
    
    # Test final recommender
    print("\n4. Testing Final Recommender...")
    try:
        state = final_recommender(state)
        print("\nFinal recommendation:")
        print(state["final_recommendation"])
        assert "final_recommendation" in state, "Final recommendation not found in state"
    except Exception as e:
        print(f"Error in final recommender: {str(e)}")
        return False
    
    print("\nAll tests completed successfully!")
    return True

if __name__ == "__main__":
    test_merger_analyzer()
