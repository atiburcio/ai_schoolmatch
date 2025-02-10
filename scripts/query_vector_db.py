import chromadb
from chromadb.utils import embedding_functions
import os
from dotenv import load_dotenv
import json
from pprint import pprint

# Load environment variables
load_dotenv()

def main():
    # Initialize OpenAI embedding function
    openai_ef = embedding_functions.OpenAIEmbeddingFunction(
        api_key=os.getenv("OPENAI_API_KEY"),
        model_name="text-embedding-ada-002"
    )
    
    # Initialize Chroma client
    chroma_client = chromadb.PersistentClient(path="chroma_db")
    
    # Get the collection
    collection = chroma_client.get_collection(
        name="ipeds_colleges",
        embedding_function=openai_ef
    )
    
    # Query for Stanford University
    results = collection.query(
        query_texts=["Alabama State University"],
        n_results=3
    )
    
    # Print full results
    for i, (doc, metadata) in enumerate(zip(results['documents'][0], results['metadatas'][0])):
        print(f"\nResult {i+1}:")
        print(doc)
        print("\nMetadata:")
        if 'TUITION1' in metadata:
            print(f"In-state tuition: ${metadata['TUITION1']:,.2f}")
        if 'TUITION2' in metadata:
            print(f"Out-of-state tuition: ${metadata['TUITION2']:,.2f}")
    
    # Get the data
    doc = results['documents'][0][0]
    metadata = results['metadatas'][0][0]
    
    print("\nDetailed Data for Stanford University")
    print("=" * 50)
    
    # Basic Information (HD2023)
    print("\nBasic Information (HD2023):")
    print("-" * 30)
    basic_fields = ['INSTNM', 'CITY', 'STABBR', 'ZIP', 'WEBADDR', 'ADMINURL', 
                   'FAIDURL', 'NPRICURL', 'SECTOR', 'CONTROL', 'LOCALE', 'LATITUDE', 'LONGITUDE']
    for field in basic_fields:
        if field in metadata:
            print(f"{field}: {metadata[field]}")
    
    # Institutional Characteristics (IC2023)
    print("\nInstitutional Characteristics (IC2023):")
    print("-" * 30)
    
    # Programs offered
    print("\nPrograms Offered:")
    levels = {
        'LEVEL1': 'Less than one year certificate',
        'LEVEL2': 'One but less than two years certificate',
        'LEVEL3': "Associate's degree",
        'LEVEL4': 'Two but less than 4 years certificate',
        'LEVEL5': "Bachelor's degree",
        'LEVEL6': 'Postbaccalaureate certificate',
        'LEVEL7': "Master's degree",
        'LEVEL8': 'Post-master\'s certificate',
        'LEVEL17': 'Doctor\'s degree - research/scholarship',
        'LEVEL18': 'Doctor\'s degree - professional practice',
        'LEVEL19': 'Doctor\'s degree - other'
    }
    for level, desc in levels.items():
        if level in metadata and metadata[level] == 1:
            print(f"- {desc}")
    
    # Student Services
    print("\nStudent Services:")
    services = {
        'STUSRV1': 'Remedial services',
        'STUSRV2': 'Academic/career counseling',
        'STUSRV3': 'Employment services for current students',
        'STUSRV4': 'Placement services for program completers',
        'STUSRV8': 'On-campus day care for children of students',
        'STUSRV9': 'None of the above'
    }
    for service, desc in services.items():
        if service in metadata and metadata[service] == 1:
            print(f"- {desc}")
    
    # Distance Education
    print("\nDistance Education:")
    if 'DISTCRS' in metadata:
        print("Offers distance education courses" if metadata['DISTCRS'] == 1 else "Does not offer distance education courses")
    
    # Mission Statement (IC2023Mission)
    print("\nMission Statement:")
    print("-" * 30)
    if 'mission' in metadata:
        print(metadata['mission'] if metadata['mission'] != 'nan' else "No mission statement available")
    
    # Generated Description
    print("\nGenerated Description:")
    print("-" * 30)
    print(doc)

if __name__ == "__main__":
    main()
