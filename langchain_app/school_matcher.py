from typing import Dict, TypedDict, List, Annotated
from langgraph.graph import Graph
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.callbacks import tracing_v2_enabled
import json
import os
import sys

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.college_vector_store import CollegeVectorStore
from models.college import College
from config import get_openai_api_key

# Configure LangSmith tracing
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_PROJECT"] = "schoolmatch-ai"

# Define the state type for our graph
class GraphState(TypedDict):
    target_school: str
    extracted_features: Dict
    matches: List[Dict]
    final_recommendations: str
    feedback: str
    iteration: int
    should_continue: bool

def create_feature_extractor(llm):
    """Creates a node that extracts relevant features from the target school."""
    
    template = """Given a target school, analyze its characteristics and extract the key features that would be most relevant for finding similar schools.
    Consider these aspects:
    - School type (public/private)
    - Size category (small: <5000, medium: 5000-15000, large: >15000)
    - Academic reputation (based on rankings, acceptance rate, research output)
    - Location type (urban/rural/suburban)
    - Cost category (based on tuition: low: <$20k, medium: $20k-$40k, high: >$40k)
    - Key academic programs and strengths
    - Use the description of the school to provide more context and information.
    
    Target School: {school}
    
    Return the features as a JSON object with these keys:
    {{
        "type": "",
        "size_category": "",
        "academic_level": "",
        "location_type": "",
        "cost_category": "",
        "key_programs": [],
        "description": "",
    }}
    
    Be specific and accurate in your categorization to help find the most relevant matches.
    """
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", template),
        ("human", "{school}")
    ])
    
    chain = prompt | llm
    
    def feature_extractor(state: GraphState) -> GraphState:
        school_name = state["target_school"]
        result = chain.invoke({"school": school_name})
        features = json.loads(result.content)
        state["extracted_features"] = features
        return state
    
    return feature_extractor

def create_school_matcher(vector_store: CollegeVectorStore):
    """Creates a node that finds similar schools based on extracted features."""
    
    def school_matcher(state: GraphState) -> GraphState:
        features = state["extracted_features"]
        target_school = state["target_school"]
        
        # Convert features to a search query
        query = f"""Looking for schools that are:
        - {features['type']} institutions
        - {features['size_category']} in size
        - {features['academic_level']} academic reputation
        - Located in {features['location_type']} areas
        - {features['cost_category']} cost range
        - Strong in programs like: {', '.join(features['key_programs'])}
        - Description matching: {features['description']}
        """
        
        # Get similar schools from vector store
        matches = vector_store.find_similar_colleges(query, n_results=6)
        
        # Filter out the target school and keep only unique schools
        seen_ids = set()
        filtered_matches = []
        for match in matches:
            if match["metadata"]["name"].lower() != target_school.lower() and match["id"] not in seen_ids:
                filtered_matches.append(match)
                seen_ids.add(match["id"])
        
        state["matches"] = filtered_matches[:5]
        return state
    
    return school_matcher

def create_recommendation_formatter(llm):
    """Creates a node that formats the recommendations in a user-friendly way."""
    
    template = """Given a target school and a list of similar schools, create a detailed but concise explanation of why each school is a good match.
    For each recommended school, highlight:
    Begin with the name of the school
    1. Key similarities with the target school
    2. Unique strengths and opportunities
    3. Academic program alignment
    4. Campus environment and culture fit, state the key features that helped find this recommendation
    5. Cost and financial considerations
    6. Religious and faith based differences to consider
    
    Target School: {target_school}
    
    Similar Schools:
    {matches}
    
    Format your response as a numbered list with clear sections for each school. Focus on what makes each school a compelling alternative to the target school.
    """
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", template),
        ("human", "Target: {target_school}\nMatches: {matches}")
    ])
    
    chain = prompt | llm
    
    def format_recommendations(state: GraphState) -> GraphState:
        # Format matches into a readable string
        matches_str = ""
        for match in state["matches"]:
            metadata = match["metadata"]
            matches_str += f"\n- {metadata['name']} ({metadata['type']})"
            matches_str += f"\n  Location: {metadata['location']}, {metadata['state']}"
            matches_str += f"\n  Programs: {metadata['programs']}"
            matches_str += f"\n  Enrollment: {metadata['total_enrollment']}"
            matches_str += f"\n  Acceptance Rate: {metadata['acceptance_rate']}%"
            matches_str += f"\n  Notable Features: {metadata['notable_features']}\n"
        
        result = chain.invoke({
            "target_school": state["target_school"],
            "matches": matches_str
        })
        state["final_recommendations"] = result.content
        return state
    
    return format_recommendations

def create_feedback_processor(llm):
    """Creates a node that processes human feedback and adjusts the search criteria."""
    
    template = """Given the user's feedback about school recommendations, analyze their preferences and adjust the search criteria.
    Current features: {current_features}
    User feedback: {feedback}
    
    If the feedback is positive (e.g., "looks good", "that's perfect", etc.), return the current features unchanged.
    Otherwise, adjust the search criteria while maintaining reasonable similarity to the target school.
    
    Consider these aspects when adjusting:
    - School type preference (public/private)
    - Size preference
    - Location preference
    - Program emphasis
    - Cost considerations
    - Campus culture
    
    Return the adjusted features as a JSON object with these exact keys:
    {{
        "type": "",
        "size_category": "",
        "academic_level": "",
        "location_type": "",
        "cost_category": "",
        "key_programs": [],
        "description": ""
    }}
    """
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", template),
        ("human", "Current features: {current_features}\nFeedback: {feedback}")
    ])
    
    chain = prompt | llm
    
    def process_feedback(state: GraphState) -> GraphState:
        if not state["feedback"]:
            state["should_continue"] = False
            return state
            
        # Check for positive feedback
        positive_feedback = any(phrase in state["feedback"].lower() for phrase in 
                              ["good", "perfect", "great", "excellent", "fine", "yes"])
        
        if positive_feedback:
            # Keep current features and stop iteration
            state["should_continue"] = False
            return state
            
        result = chain.invoke({
            "current_features": json.dumps(state["extracted_features"], indent=2),
            "feedback": state["feedback"]
        })
        
        # Update features based on feedback
        try:
            state["extracted_features"] = json.loads(result.content)
        except json.JSONDecodeError:
            # If we can't parse the response, keep current features and stop iteration
            state["should_continue"] = False
            return state
            
        state["iteration"] += 1
        state["should_continue"] = state["iteration"] < 3  # Limit to 3 iterations
        return state
    
    return process_feedback

def get_school_recommendations(school_name: str, vector_store: CollegeVectorStore, feedback: str = "", interactive: bool = True) -> str:
    """Main function to get school recommendations with optional interactive feedback."""
    
    # Initialize LLM
    llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0.0,
        api_key=get_openai_api_key()
    )
    
    # Create initial state
    state = GraphState(
        target_school=school_name,
        extracted_features={},
        matches=[],
        final_recommendations="",
        feedback=feedback,
        iteration=0,
        should_continue=True
    )
    
    iteration = 0
    # Use tracing context manager
    with tracing_v2_enabled(tags=["schoolmatch-ai"]):
        # Extract initial features
        feature_extractor = create_feature_extractor(llm)
        state = feature_extractor(state)
        
        while True:
            # Process feedback if any
            if state["feedback"]:
                feedback_processor = create_feedback_processor(llm)
                state = feedback_processor(state)
            
            # Find matches
            school_matcher = create_school_matcher(vector_store)
            state = school_matcher(state)
            
            # Format recommendations
            recommendation_formatter = create_recommendation_formatter(llm)
            state = recommendation_formatter(state)
            
            # Print current recommendations
            print("\nCurrent Recommendations:")
            print(state["final_recommendations"])
            
            # If not interactive or we've reached max iterations, break
            if not interactive or state["iteration"] >= 3:
                break
                
            # Get feedback from user
            print("\n🔄 Would you like to refine these recommendations?")
            print("Examples of feedback you can provide:")
            print("- 'I prefer schools in urban areas'")
            print("- 'Looking for schools with strong engineering programs'")
            print("- 'Interested in schools with a smaller student body'")
            print("- 'Want schools with strong research opportunities'")
            print("\nPress Enter to finish, or type your feedback:")
            
            feedback = input("> ").strip()
            if not feedback:
                break
                
            # Update state with new feedback
            state["feedback"] = feedback
            state["iteration"] += 1
            iteration += 1
            
            print(f"\n📝 Processing feedback: '{feedback}'")
            print("Please wait...")
    
    return state["final_recommendations"]

if __name__ == "__main__":
    try:
        print("🎓 Testing School Recommendation System")
        print("-" * 50)
        
        # Initialize vector store
        vector_store = CollegeVectorStore()
        
        # Get recommendations with interactive feedback
        print("\n📚 Getting recommendations for Stanford University...")
        recommendations = get_school_recommendations("Stanford University", vector_store)
        
    except Exception as e:
        print(f"\n❌ An error occurred: {str(e)}")
        print("\nTroubleshooting steps:")
        print("1. Check if your OpenAI API key is set in .env file")
        print("2. Ensure the vector store is populated with college data")
        print("3. Verify all required packages are installed")
