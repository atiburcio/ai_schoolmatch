from langchain_openai import ChatOpenAI
from langchain_app.merger_analyzer import create_merger_feature_extractor
import os
from dotenv import load_dotenv

def test_merger_feature_extractor():
    # Load environment variables
    load_dotenv()
    
    # Initialize the LLM
    llm = ChatOpenAI(
        model="gpt-4",
        temperature=0,
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    # Create the feature extractor node
    feature_extractor = create_merger_feature_extractor(llm)
    
    # Test with a sample school
    test_state = {
        "school": """
        Stanford University is a private research university in Stanford, California. 
        The university's academic programs include seven schools: School of Engineering, 
        School of Humanities and Sciences, School of Earth, Energy & Environmental Sciences, 
        School of Medicine, Graduate School of Education, Graduate School of Business, and Stanford Law School.
        
        Stanford has a highly selective undergraduate program with an acceptance rate below 5%. 
        The university has an endowment of over $37 billion and annual research budget of $1.63 billion. 
        It is known for its entrepreneurial spirit and close ties to Silicon Valley.
        
        The university has approximately 7,000 undergraduate students and 9,000 graduate students, 
        with a student-to-faculty ratio of 5:1. Stanford offers comprehensive financial aid, 
        meeting 100% of demonstrated need for undergraduates.
        """
    }
    
    # Run the feature extractor
    try:
        result = feature_extractor(test_state)
        print("\nFeature Extraction Result:")
        print(result["features"])
        return True
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    test_merger_feature_extractor()
