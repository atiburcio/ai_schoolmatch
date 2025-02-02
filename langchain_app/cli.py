import argparse
from school_matcher import get_school_recommendations
from db.college_vector_store import CollegeVectorStore

def main():
    parser = argparse.ArgumentParser(description='Find similar schools to a target school')
    parser.add_argument('school', type=str, help='Name of the target school')
    
    args = parser.parse_args()
    
    vector_store = CollegeVectorStore()
    recommendations = get_school_recommendations(args.school, vector_store)
    
    print("\nSchool Recommendations:")
    print("=" * 50)
    print(recommendations)

if __name__ == "__main__":
    main()
