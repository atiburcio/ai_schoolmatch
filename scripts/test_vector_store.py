import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.college_vector_store import CollegeVectorStore

def main():
    # Initialize the vector store
    vector_store = CollegeVectorStore()
    
    # Test query for a well-known university to verify IPEDS data
    test_query = "Find universities similar to Harvard University"
    results = vector_store.find_similar_colleges(test_query, n_results=10)
    
    print("\nQuerying for:", test_query)
    print("\nResults from vector store:")
    print("-" * 50)
    
    for idx, result in enumerate(results, 1):
        metadata = result.get('metadata', {})
        print(f"\n{idx}. Institution: {metadata.get('INSTNM', 'N/A')}")
        print(f"   Location: {metadata.get('CITY', 'N/A')}, {metadata.get('STABBR', 'N/A')}")
        print(f"   Type: {metadata.get('SECTOR', 'N/A')}")
        if 'INSTURL' in metadata:
            print(f"   Website: {metadata.get('INSTURL', 'N/A')}")

if __name__ == "__main__":
    main()
