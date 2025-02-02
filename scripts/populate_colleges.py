import uuid
import sys
import os
from datetime import date

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.college_vector_store import CollegeVectorStore
from models.college import College

# Sample college data
SAMPLE_COLLEGES = [
    {
        "name": "Stanford University",
        "location": "Stanford",
        "state": "California",
        "type": "Private",
        "total_enrollment": 17249,
        "acceptance_rate": 4.34,
        "tuition_in_state": 56169,
        "tuition_out_state": 56169,
        "programs": [
            "Computer Science",
            "Engineering",
            "Business",
            "Medicine",
            "Law",
            "Humanities",
            "Social Sciences"
        ],
        "student_faculty_ratio": 5.0,
        "graduation_rate": 94.0,
        "campus_setting": "Suburban",
        "athletics_division": "NCAA Division I",
        "housing_available": True,
        "description": """Stanford University, located in the heart of Silicon Valley, is one of the world's leading teaching and research institutions. Known for its entrepreneurial spirit and strong ties to the tech industry, Stanford offers a comprehensive range of programs across seven schools. The university's beautiful campus spans 8,180 acres and features distinctive Main Quad architecture. Stanford is renowned for its innovation in computer science and engineering, while also maintaining excellence in humanities, social sciences, and professional programs. The university emphasizes interdisciplinary studies and research, with numerous institutes and centers facilitating collaboration across disciplines.""",
        "notable_features": [
            "Silicon Valley location",
            "Strong entrepreneurship programs",
            "World-class research facilities",
            "Extensive research funding",
            "Strong athletic programs"
        ],
        "median_sat_score": 1440,
        "median_act_score": 34,
        "ranking_national": 3
    },
    {
        "name": "University of California, Berkeley",
        "location": "Berkeley",
        "state": "California",
        "type": "Public",
        "total_enrollment": 42327,
        "acceptance_rate": 14.5,
        "tuition_in_state": 14226,
        "tuition_out_state": 44007,
        "programs": [
            "Engineering",
            "Computer Science",
            "Business",
            "Physics",
            "Chemistry",
            "Economics",
            "Political Science"
        ],
        "student_faculty_ratio": 18.0,
        "graduation_rate": 91.0,
        "campus_setting": "Urban",
        "athletics_division": "NCAA Division I",
        "housing_available": True,
        "description": """UC Berkeley, the flagship campus of the University of California system, is renowned for its academic excellence, pioneering research, and social activism heritage. Located in the San Francisco Bay Area, Berkeley offers a vibrant urban setting with access to countless cultural and professional opportunities. The university is particularly known for its strength in sciences, with multiple Nobel laureates among its faculty. Berkeley combines rigorous academics with a strong commitment to public service and diversity.""",
        "notable_features": [
            "Top-ranked public university",
            "Strong research programs",
            "Diverse student body",
            "Rich history of activism",
            "Beautiful Bay Area location"
        ],
        "median_sat_score": 1405,
        "median_act_score": 31,
        "ranking_national": 20
    },
    {
        "name": "De Anza College",
        "location": "Cupertino",
        "state": "California",
        "type": "Community College",
        "total_enrollment": 18000,
        "acceptance_rate": 100.0,
        "tuition_in_state": 1561,
        "tuition_out_state": 9853,
        "programs": [
            "Computer Science",
            "Business",
            "Nursing",
            "Liberal Arts",
            "Design",
            "Environmental Studies"
        ],
        "student_faculty_ratio": 25.0,
        "graduation_rate": 65.0,
        "campus_setting": "Suburban",
        "athletics_division": "CCCAA",
        "housing_available": False,
        "description": """De Anza College is one of the top community colleges in California, known for its high transfer rates to four-year universities. Located in the heart of Silicon Valley, it offers excellent STEM programs and strong connections to the tech industry. The college emphasizes student success through comprehensive support services, small class sizes, and dedicated faculty. De Anza is particularly noted for its environmental studies program and commitment to sustainability.""",
        "notable_features": [
            "High transfer rates",
            "Silicon Valley location",
            "Strong STEM programs",
            "Sustainability initiatives",
            "Diverse student population"
        ],
        "median_sat_score": None,
        "median_act_score": None,
        "ranking_national": None
    },
    {
        "name": "Massachusetts Institute of Technology",
        "location": "Cambridge",
        "state": "Massachusetts",
        "type": "Private",
        "total_enrollment": 11376,
        "acceptance_rate": 7.3,
        "tuition_in_state": 53790,
        "tuition_out_state": 53790,
        "programs": [
            "Engineering",
            "Computer Science",
            "Physics",
            "Mathematics",
            "Architecture",
            "Business",
            "Biology"
        ],
        "student_faculty_ratio": 3.0,
        "graduation_rate": 95.0,
        "campus_setting": "Urban",
        "athletics_division": "NCAA Division III",
        "housing_available": True,
        "description": """MIT is a world-renowned institution focused on science, technology, and innovation. Located along the Charles River in Cambridge, it offers a rigorous education with an emphasis on practical problem-solving and hands-on learning. The institute is known for its cutting-edge research, entrepreneurial ecosystem, and collaborative atmosphere. MIT's culture combines intense academics with a playful spirit, evident in its famous hacks and traditions.""",
        "notable_features": [
            "World-leading STEM programs",
            "Innovation and entrepreneurship focus",
            "Extensive research opportunities",
            "Strong maker culture",
            "Proximity to Boston's tech hub"
        ],
        "median_sat_score": 1535,
        "median_act_score": 35,
        "ranking_national": 2
    },
    {
        "name": "Foothill College",
        "location": "Los Altos Hills",
        "state": "California",
        "type": "Community College",
        "total_enrollment": 15000,
        "acceptance_rate": 100.0,
        "tuition_in_state": 1561,
        "tuition_out_state": 9853,
        "programs": [
            "Computer Science",
            "Biology",
            "Business",
            "Psychology",
            "Dental Hygiene",
            "Music Technology"
        ],
        "student_faculty_ratio": 23.0,
        "graduation_rate": 63.0,
        "campus_setting": "Suburban",
        "athletics_division": "CCCAA",
        "housing_available": False,
        "description": """Foothill College, nestled in the hills above Silicon Valley, is known for its beautiful campus and strong academic programs. The college offers excellent preparation for transfer to four-year universities and innovative career training programs. Foothill is particularly noted for its STEM programs, dental hygiene program, and music technology facilities. The college emphasizes student success through comprehensive support services and a commitment to equity.""",
        "notable_features": [
            "Beautiful hillside campus",
            "Strong transfer rates",
            "Innovative career programs",
            "Modern facilities",
            "Close to tech companies"
        ],
        "median_sat_score": None,
        "median_act_score": None,
        "ranking_national": None
    },
    {
        "name": "University of Michigan",
        "location": "Ann Arbor",
        "state": "Michigan",
        "type": "Public",
        "total_enrollment": 47000,
        "acceptance_rate": 20.2,
        "tuition_in_state": 15558,
        "tuition_out_state": 52266,
        "programs": [
            "Engineering",
            "Business",
            "Medicine",
            "Law",
            "Liberal Arts",
            "Public Policy",
            "Education"
        ],
        "student_faculty_ratio": 15.0,
        "graduation_rate": 93.0,
        "campus_setting": "College Town",
        "athletics_division": "NCAA Division I",
        "housing_available": True,
        "description": """The University of Michigan is a top-ranked public research university known for its academic excellence and vibrant campus life. Located in Ann Arbor, it offers a comprehensive range of undergraduate and graduate programs. The university is particularly renowned for its engineering, business, and medical schools, while maintaining strong liberal arts programs. Michigan's research expenditures are among the highest of any public university.""",
        "notable_features": [
            "Top-ranked public university",
            "Strong research programs",
            "Vibrant college town",
            "Historic Big Ten school",
            "Excellence across disciplines"
        ],
        "median_sat_score": 1400,
        "median_act_score": 32,
        "ranking_national": 25
    },
    {
        "name": "Rice University",
        "location": "Houston",
        "state": "Texas",
        "type": "Private",
        "total_enrollment": 7500,
        "acceptance_rate": 9.0,
        "tuition_in_state": 52895,
        "tuition_out_state": 52895,
        "programs": [
            "Engineering",
            "Architecture",
            "Natural Sciences",
            "Social Sciences",
            "Music",
            "Business"
        ],
        "student_faculty_ratio": 6.0,
        "graduation_rate": 95.0,
        "campus_setting": "Urban",
        "athletics_division": "NCAA Division I",
        "housing_available": True,
        "description": """Rice University is a private research university with a strong focus on undergraduate education. Known for its small class sizes and collaborative atmosphere, Rice offers an intimate academic environment in the heart of Houston's Museum District. The university is particularly strong in engineering, architecture, and natural sciences, while maintaining excellence across all disciplines.""",
        "notable_features": [
            "Small class sizes",
            "Strong research opportunities",
            "Residential college system",
            "Urban location",
            "Cross-disciplinary programs"
        ],
        "median_sat_score": 1505,
        "median_act_score": 34,
        "ranking_national": 17
    },
    {
        "name": "University of Washington",
        "location": "Seattle",
        "state": "Washington",
        "type": "Public",
        "total_enrollment": 47400,
        "acceptance_rate": 52.0,
        "tuition_in_state": 11745,
        "tuition_out_state": 39114,
        "programs": [
            "Computer Science",
            "Engineering",
            "Medicine",
            "Business",
            "Environmental Science",
            "Public Health",
            "Marine Biology"
        ],
        "student_faculty_ratio": 19.0,
        "graduation_rate": 84.0,
        "campus_setting": "Urban",
        "athletics_division": "NCAA Division I",
        "housing_available": True,
        "description": """The University of Washington is a public research university in Seattle, known for its strong STEM programs and medical center. Its location in the Pacific Northwest tech hub provides unique opportunities for internships and research. The university is particularly renowned for its computer science, engineering, and medical programs.""",
        "notable_features": [
            "Strong tech industry connections",
            "World-class medical center",
            "Beautiful campus",
            "Environmental research focus",
            "Pacific Northwest location"
        ],
        "median_sat_score": 1340,
        "median_act_score": 30,
        "ranking_national": 55
    },
    {
        "name": "Vanderbilt University",
        "location": "Nashville",
        "state": "Tennessee",
        "type": "Private",
        "total_enrollment": 13131,
        "acceptance_rate": 7.1,
        "tuition_in_state": 57118,
        "tuition_out_state": 57118,
        "programs": [
            "Economics",
            "Education",
            "Engineering",
            "Medicine",
            "Music",
            "Law",
            "Humanities"
        ],
        "student_faculty_ratio": 7.0,
        "graduation_rate": 95.0,
        "campus_setting": "Urban",
        "athletics_division": "NCAA Division I",
        "housing_available": True,
        "description": """Vanderbilt University combines strong academics with a vibrant campus life in the heart of Nashville. Known for its beautiful campus and strong undergraduate teaching, Vanderbilt offers excellent programs across multiple disciplines. The university is particularly known for its education, music, and medical programs.""",
        "notable_features": [
            "Beautiful campus",
            "Strong research funding",
            "Music city location",
            "Collaborative atmosphere",
            "Residential college system"
        ],
        "median_sat_score": 1505,
        "median_act_score": 34,
        "ranking_national": 13
    },
    {
        "name": "University of Wisconsin-Madison",
        "location": "Madison",
        "state": "Wisconsin",
        "type": "Public",
        "total_enrollment": 45540,
        "acceptance_rate": 54.0,
        "tuition_in_state": 10725,
        "tuition_out_state": 37785,
        "programs": [
            "Engineering",
            "Business",
            "Agriculture",
            "Environmental Studies",
            "Education",
            "Life Sciences",
            "Social Sciences"
        ],
        "student_faculty_ratio": 17.0,
        "graduation_rate": 88.0,
        "campus_setting": "Urban",
        "athletics_division": "NCAA Division I",
        "housing_available": True,
        "description": """The University of Wisconsin-Madison is a public land-grant university known for its research programs and vibrant campus life. Located between two lakes, the campus offers a unique blend of natural beauty and urban amenities. The university is particularly strong in research, with programs ranging from agriculture to engineering.""",
        "notable_features": [
            "Research excellence",
            "Lakeside location",
            "Strong athletic tradition",
            "Active student life",
            "Environmental focus"
        ],
        "median_sat_score": 1390,
        "median_act_score": 29,
        "ranking_national": 38
    },
    {
        "name": "Boston College",
        "location": "Chestnut Hill",
        "state": "Massachusetts",
        "type": "Private",
        "total_enrollment": 14890,
        "acceptance_rate": 27.0,
        "tuition_in_state": 60202,
        "tuition_out_state": 60202,
        "programs": [
            "Business",
            "Education",
            "Nursing",
            "Law",
            "Social Work",
            "Arts and Sciences",
            "Theology"
        ],
        "student_faculty_ratio": 11.0,
        "graduation_rate": 94.0,
        "campus_setting": "Suburban",
        "athletics_division": "NCAA Division I",
        "housing_available": True,
        "description": """Boston College is a private Jesuit research university that combines intellectual excellence with a commitment to personal formation and social justice. Known for its gothic architecture and beautiful campus, BC offers strong programs in business, education, and the liberal arts.""",
        "notable_features": [
            "Jesuit education tradition",
            "Gothic architecture",
            "Strong liberal arts focus",
            "Boston area location",
            "Service-learning emphasis"
        ],
        "median_sat_score": 1420,
        "median_act_score": 33,
        "ranking_national": 35
    },
    {
        "name": "Georgia Institute of Technology",
        "location": "Atlanta",
        "state": "Georgia",
        "type": "Public",
        "total_enrollment": 39771,
        "acceptance_rate": 21.0,
        "tuition_in_state": 12682,
        "tuition_out_state": 33794,
        "programs": [
            "Engineering",
            "Computing",
            "Business",
            "Architecture",
            "Sciences",
            "Design",
            "Liberal Arts"
        ],
        "student_faculty_ratio": 19.0,
        "graduation_rate": 90.0,
        "campus_setting": "Urban",
        "athletics_division": "NCAA Division I",
        "housing_available": True,
        "description": """Georgia Tech is a leading technology-focused public university known for its engineering and computing programs. Located in the heart of Atlanta, it offers students access to numerous tech companies and startups. The university is particularly renowned for its innovative research and strong industry connections.""",
        "notable_features": [
            "Top engineering programs",
            "Innovation ecosystem",
            "Urban tech hub",
            "Research excellence",
            "Strong industry partnerships"
        ],
        "median_sat_score": 1465,
        "median_act_score": 33,
        "ranking_national": 15
    },
    {
        "name": "University of Virginia",
        "location": "Charlottesville",
        "state": "Virginia",
        "type": "Public",
        "total_enrollment": 25018,
        "acceptance_rate": 23.0,
        "tuition_in_state": 14188,
        "tuition_out_state": 48036,
        "programs": [
            "Liberal Arts",
            "Engineering",
            "Business",
            "Architecture",
            "Education",
            "Law",
            "Medicine"
        ],
        "student_faculty_ratio": 15.0,
        "graduation_rate": 95.0,
        "campus_setting": "College Town",
        "athletics_division": "NCAA Division I",
        "housing_available": True,
        "description": """The University of Virginia, founded by Thomas Jefferson, is a public university that combines historical significance with modern excellence. Known for its distinctive architecture and honor code, UVA offers strong programs across various disciplines while maintaining a focus on undergraduate education.""",
        "notable_features": [
            "Historic campus",
            "Honor system",
            "Jefferson's academic village",
            "Strong public ivy",
            "Research opportunities"
        ],
        "median_sat_score": 1430,
        "median_act_score": 32,
        "ranking_national": 25
    },
    {
        "name": "University of Texas at Austin",
        "location": "Austin",
        "state": "Texas",
        "type": "Public",
        "total_enrollment": 51525,
        "acceptance_rate": 32.0,
        "tuition_in_state": 11448,
        "tuition_out_state": 40032,
        "programs": [
            "Business",
            "Engineering",
            "Computer Science",
            "Communications",
            "Liberal Arts",
            "Fine Arts",
            "Natural Sciences"
        ],
        "student_faculty_ratio": 19.0,
        "graduation_rate": 87.0,
        "campus_setting": "Urban",
        "athletics_division": "NCAA Division I",
        "housing_available": True,
        "description": """The University of Texas at Austin is one of the largest public research universities in the United States, known for its diverse academic offerings and vibrant campus life. Located in the dynamic city of Austin, it offers students access to a thriving tech scene and cultural environment.""",
        "notable_features": [
            "Large research institution",
            "Vibrant Austin culture",
            "Strong tech connections",
            "Diverse student body",
            "Rich athletic tradition"
        ],
        "median_sat_score": 1355,
        "median_act_score": 30,
        "ranking_national": 38
    },
    {
        "name": "University of North Carolina at Chapel Hill",
        "location": "Chapel Hill",
        "state": "North Carolina",
        "type": "Public",
        "total_enrollment": 30092,
        "acceptance_rate": 25.0,
        "tuition_in_state": 8980,
        "tuition_out_state": 36159,
        "programs": [
            "Business",
            "Journalism",
            "Public Health",
            "Medicine",
            "Liberal Arts",
            "Education",
            "Information Science"
        ],
        "student_faculty_ratio": 13.0,
        "graduation_rate": 91.0,
        "campus_setting": "College Town",
        "athletics_division": "NCAA Division I",
        "housing_available": True,
        "description": """UNC-Chapel Hill, the nation's first public university, combines academic excellence with strong athletic traditions. Known for its beautiful campus and collaborative atmosphere, UNC offers top programs in various fields, particularly in healthcare, journalism, and business.""",
        "notable_features": [
            "First public university",
            "Research triangle location",
            "Healthcare excellence",
            "Strong public education",
            "Championship athletics"
        ],
        "median_sat_score": 1395,
        "median_act_score": 31,
        "ranking_national": 29
    }
]

def populate_vector_store():
    """Populate the vector store with sample colleges."""
    vector_store = CollegeVectorStore()
    
    for college_data in SAMPLE_COLLEGES:
        # Create a unique ID for each college
        college = College(
            id=str(uuid.uuid4()),
            **college_data
        )
        
        try:
            vector_store.add_college(college)
            print(f"Added college: {college.name}")
        except Exception as e:
            print(f"Error adding college {college.name}: {str(e)}")

    print("\nTesting retrieval...")
    # Test retrieval with sample queries
    queries = [
        "technical institute with strong engineering and computer science programs",
        "affordable community college in Silicon Valley with good transfer rates",
        "prestigious university with strong research programs and entrepreneurial spirit"
    ]
    
    for query in queries:
        print(f"\nSimilar colleges to '{query}':")
        similar_colleges = vector_store.find_similar_colleges(query, n_results=2)
        for college in similar_colleges:
            print(f"- {college['metadata']['name']} ({college['metadata']['type']})")

    # Test criteria-based search
    print("\nTesting criteria-based search...")
    print("Colleges in California with tuition under $2000:")
    affordable_colleges = vector_store.find_colleges_by_criteria(
        state="California",
        max_tuition=2000
    )
    for college in affordable_colleges:
        print(f"- {college['metadata']['name']} (Tuition: ${college['metadata']['tuition_in_state']})")

if __name__ == "__main__":
    populate_vector_store()
