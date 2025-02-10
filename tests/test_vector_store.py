import os
from dotenv import load_dotenv
from db.college_vector_store import CollegeVectorStore

def test_find_similar_colleges():
    # Load environment variables
    load_dotenv()
    
    # Initialize vector store with the same path as query_vector_db.py
    vector_store = CollegeVectorStore(persist_directory="chroma_db")
    
    # First, check if there are any colleges in the database
    all_colleges = vector_store.get_all_colleges()
    print(f"\nNumber of colleges in database: {len(all_colleges)}")
    
    if len(all_colleges) == 0:
        print("The vector store is empty. Please ensure the database is populated.")
        return
    
    # Print some sample colleges to verify the data
    print("\nSample colleges in database:")
    for college in all_colleges[:3]:  # Show first 3 colleges
        print(f"- {college['metadata']['INSTNM']} ({college['metadata'].get('STABBR', 'N/A')})")
    
    # Test query
    test_description = """A public university located in an urban setting with strong STEM programs,
    particularly in engineering and computer science. The university has a diverse student body and 
    offers both undergraduate and graduate programs."""
    
    print("\nSearching for colleges similar to description...")
    results = vector_store.find_similar_colleges(test_description, n_results=5)
    
    print(f"\nFound {len(results)} similar colleges:")
    
    # Debug: Print metadata fields for first result
    if results:
        print("\nAvailable metadata fields:")
        print(results[0]['metadata'].keys())
        print("\nFirst result metadata:")
        print(results[0]['metadata'])
        print("\nFirst result document:")
        print(results[0]['document'])
    
    for result in results:
        print("\n-----------------------------------")
        metadata = result['metadata']
        
        # Use get() to safely access fields
        name = metadata.get('INSTNM', metadata.get('name', 'Unknown Institution'))
        city = metadata.get('CITY', metadata.get('city', 'N/A'))
        state = metadata.get('STABBR', metadata.get('state', 'N/A'))
        
        print(f"College: {name}")
        print(f"Location: {city}, {state}")
        
        # Convert sector codes to readable format if available
        sector = metadata.get('SECTOR', metadata.get('sector', 'N/A'))
        sector_map = {
            1: "Public, 4-year or above",
            2: "Private nonprofit, 4-year or above",
            3: "Private for-profit, 4-year or above",
            4: "Public, 2-year",
            5: "Private nonprofit, 2-year",
            6: "Private for-profit, 2-year",
            7: "Public, less than 2-year",
            8: "Private nonprofit, less than 2-year",
            9: "Private for-profit, less than 2-year"
        }
        sector_name = sector_map.get(sector, f"Unknown sector ({sector})")
        print(f"Type: {sector_name}")
        
        print(f"Similarity Score: {1 - result['distance']:.4f}")  # Convert distance to similarity
        
        # Print available program levels if they exist
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
        
        print("Programs offered:")
        has_programs = False
        for level, desc in levels.items():
            if metadata.get(level) == 1:
                print(f"- {desc}")
                has_programs = True
        if not has_programs:
            print("- Program information not available")
        
        print("-----------------------------------")

if __name__ == "__main__":
    test_find_similar_colleges()
