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
    
    # Initialize Chroma client with absolute path
    chroma_client = chromadb.PersistentClient(path="/Users/anthonytiburcio/Documents/GitHub/schoolmatch_v1/chroma_db")
    
    # Get the collection
    collection = chroma_client.get_collection(
        name="ipeds_colleges",
        embedding_function=openai_ef
    )
    
    # Get user input for query
    query = input("Enter a school name or description to search for: ")
    if not query.strip():
        query = "Stanford University"  # Default if nothing entered
    
    # Set number of results
    num_results = input("How many results would you like to see? (default: 3): ")
    try:
        n_results = int(num_results)
    except (ValueError, TypeError):
        n_results = 3  # Default if invalid input
    
    print(f"\nSearching for: '{query}' (showing top {n_results} results)")
    
    # Execute the query
    results = collection.query(
        query_texts=[query],
        n_results=n_results,
        include=["documents", "metadatas", "distances"]
    )
    
    # Print results
    if not results['documents'][0]:
        print("No results found.")
        return
    
    for i, (doc, metadata, distance) in enumerate(zip(
        results['documents'][0], 
        results['metadatas'][0],
        results['distances'][0]
    )):
        print(f"\n{'=' * 60}")
        print(f"Result {i+1} (Similarity: {1-distance:.2f})")
        print(f"{'=' * 60}")
        
        # Basic info
        print(f"Institution: {metadata.get('INSTNM', 'Unknown')}")
        location = f"{metadata.get('CITY', '')}, {metadata.get('STABBR', '')}"
        print(f"Location: {location}")
        print(f"Website: {metadata.get('WEBADDR', 'N/A')}")
        print(f"Control: {'Public' if metadata.get('CONTROL') == 1 else 'Private non-profit' if metadata.get('CONTROL') == 2 else 'Private for-profit' if metadata.get('CONTROL') == 3 else 'Unknown'}")
        
        # Tuition
        if 'TUITION1' in metadata:
            print(f"In-state tuition: ${float(metadata['TUITION1']):,.2f}")
        if 'TUITION2' in metadata:
            print(f"Out-of-state tuition: ${float(metadata['TUITION2']):,.2f}")
        
        # Financial data
        print("\nFinancial Information:")
        
        # Check for F1A (public) data
        f1a_fields = {
            'F1A18': "Total revenues",
            'F1A43': "Total expenses", 
            'F1A02': "Total assets"
        }
        fin_found = False
        for field, label in f1a_fields.items():
            if field in metadata and metadata[field]:
                if not fin_found:
                    print("  Public Institution Data:")
                    fin_found = True
                print(f"  - {label}: ${float(metadata[field]):,.2f}")
        
        # Check for F2 (private for-profit) data
        f2_fields = {
            'F2D01': "Total revenues", 
            'F2D02': "Total expenses",
            'F2C19': "Total assets"
        }
        fin_found = False
        for field, label in f2_fields.items():
            if field in metadata and metadata[field]:
                if not fin_found:
                    print("  Private For-Profit Institution Data:")
                    fin_found = True
                print(f"  - {label}: ${float(metadata[field]):,.2f}")
        
        # Check for F3 (private non-profit) data
        f3_fields = {
            'F3D01': "Total revenues", 
            'F3D02': "Total expenses",
            'F3C19': "Total assets",
            'F3H01': "Endowment assets"
        }
        fin_found = False
        for field, label in f3_fields.items():
            if field in metadata and metadata[field]:
                if not fin_found:
                    print("  Private Non-Profit Institution Data:")
                    fin_found = True
                print(f"  - {label}: ${float(metadata[field]):,.2f}")
        
        # Mission statement URL
        if 'missionURL' in metadata and metadata['missionURL']:
            print(f"\nMission Statement URL: {metadata['missionURL']}")
        
        # Brief text excerpt
        print("\nExcerpt:")
        excerpt = doc[:500] + "..." if len(doc) > 500 else doc
        print(excerpt)
    
    print("\nQuery complete.")

if __name__ == "__main__":
    main()
