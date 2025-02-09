import subprocess
import csv
import io
from langchain_openai import OpenAIEmbeddings
import chromadb
from chromadb.utils import embedding_functions
import pandas as pd
from tqdm import tqdm
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_tables_mdb(mdb_path):
    """Get list of tables in Access database using mdb-tables"""
    try:
        result = subprocess.run(['mdb-tables', mdb_path], 
                              capture_output=True, 
                              text=True)
        return result.stdout.strip().split(' ')
    except FileNotFoundError:
        print("Error: mdb-tools not found. Install with: brew install mdbtools")
        return []

def get_table_data_mdb(mdb_path, table_name):
    """Get data from specified table using mdb-export"""
    try:
        result = subprocess.run(['mdb-export', mdb_path, table_name],
                              capture_output=True,
                              text=True)
        # Convert the CSV output to DataFrame
        return pd.read_csv(io.StringIO(result.stdout))
    except subprocess.CalledProcessError as e:
        print(f"Error executing mdb-export: {e}")
        return None

def create_text_chunks(hd_row, ic_row=None, mission_row=None, ay_row=None):
    """Create a text chunk from IPEDS institutional data"""
    chunks = []
    
    # Basic institution information from HD2023
    if hd_row['INSTNM'] and hd_row['CITY'] and hd_row['STABBR']:
        chunks.append(f"{hd_row['INSTNM']} is located in {hd_row['CITY']}, {hd_row['STABBR']}.")
    
    # Institution type and control
    sector_map = {
        1: "public 4-year or above",
        2: "private nonprofit 4-year or above",
        3: "private for-profit 4-year or above",
        4: "public 2-year",
        5: "private nonprofit 2-year",
        6: "private for-profit 2-year",
        7: "public less-than-2-year",
        8: "private nonprofit less-than-2-year",
        9: "private for-profit less-than-2-year"
    }
    
    if hd_row['SECTOR'] in sector_map:
        chunks.append(f"It is a {sector_map[hd_row['SECTOR']]} institution.")
    
    # Website
    if hd_row['WEBADDR']:
        chunks.append(f"The institution's website is {hd_row['WEBADDR']}")
    
    # Additional characteristics from HD2023
    if hd_row['HBCU'] == 1:
        chunks.append("This is a Historically Black College or University (HBCU).")
    if hd_row['TRIBAL'] == 1:
        chunks.append("This is a Tribal College.")
    if hd_row['HOSPITAL'] == 1:
        chunks.append("The institution has a hospital.")
    if hd_row['MEDICAL'] == 1:
        chunks.append("The institution grants medical degrees.")
    
    # Add information from IC2023 if available
    if ic_row is not None:
        # Programs offered
        programs = []
        if ic_row['LEVEL3'] == 1:
            programs.append("Bachelor's degrees")
        if ic_row['LEVEL7'] == 1:
            programs.append("Master's degrees")
        if ic_row['LEVEL8'] == 1:
            programs.append("Doctoral degrees")
        if ic_row['LEVEL2'] == 1:
            programs.append("Associate degrees")
        if programs:
            chunks.append(f"The institution offers: {', '.join(programs)}.")
        
        # Student services
        services = []
        if ic_row['STUSRV2'] == 1:
            services.append("remedial services")
        if ic_row['STUSRV3'] == 1:
            services.append("academic/career counseling")
        if ic_row['STUSRV4'] == 1:
            services.append("employment services for students")
        if services:
            chunks.append(f"Student services include: {', '.join(services)}.")
        
        # Distance education
        if ic_row['DISTCRS'] == 1:
            chunks.append("The institution offers distance education courses.")
            
        # Add academic year information if available
        if ay_row is not None:
            tuition_info = []
            if not pd.isna(ay_row['TUITION1']):
                tuition_info.append(f"In-state tuition: ${ay_row['TUITION1']:,.2f}")
            if not pd.isna(ay_row['TUITION2']):
                tuition_info.append(f"Out-of-state tuition: ${ay_row['TUITION2']:,.2f}")
            if not pd.isna(ay_row['TUITION3']):
                tuition_info.append(f"Books and supplies cost: ${ay_row['TUITION3']:,.2f}")
            if tuition_info:
                chunks.append(f"Academic year costs: {'; '.join(tuition_info)}.")
    
    # Add mission statement if available
    if mission_row is not None and mission_row['mission']:
        chunks.append(f"Mission statement: {mission_row['mission']}")
    
    # Combine all chunks
    return " ".join(chunks)

def main():
    # Configuration
    ACCESS_DB_PATH = "/Users/anthonytiburcio/Documents/GitHub/schoolmatch_v1/db/ipeds_data/IPEDS202324.accdb"
    CHROMA_PERSIST_DIR = "chroma_db"
    
    # Initialize OpenAI embedding function
    openai_ef = embedding_functions.OpenAIEmbeddingFunction(
        api_key=os.getenv("OPENAI_API_KEY"),
        model_name="text-embedding-ada-002"
    )
    
    # Initialize Chroma client
    chroma_client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
    
    try:
        # Delete existing collection if it exists
        try:
            chroma_client.delete_collection(name="ipeds_colleges")
            print("Deleted existing collection")
        except ValueError:
            pass  # Collection didn't exist
        
        # Get data from all tables
        print("Loading data from tables...")
        hd_df = get_table_data_mdb(ACCESS_DB_PATH, "HD2023")
        ic_df = get_table_data_mdb(ACCESS_DB_PATH, "IC2023")
        mission_df = get_table_data_mdb(ACCESS_DB_PATH, "IC2023Mission")
        ay_df = get_table_data_mdb(ACCESS_DB_PATH, "IC2023_AY")
        
        if hd_df is None:
            return
            
        print(f"Retrieved {len(hd_df)} institutions from HD2023")
        
        # Set index for easier joining
        if ic_df is not None:
            ic_df.set_index('UNITID', inplace=True)
        if mission_df is not None:
            mission_df.set_index('unitid', inplace=True)
        if ay_df is not None:
            ay_df.set_index('UNITID', inplace=True)
        
        # Create collection
        collection = chroma_client.create_collection(
            name="ipeds_colleges",
            embedding_function=openai_ef
        )
        
        # Process each row and add to Chroma
        batch_size = 100
        for i in range(0, len(hd_df), batch_size):
            batch_df = hd_df.iloc[i:i + batch_size]
            
            # Create text chunks and metadata for the batch
            texts = []
            ids = []
            metadatas = []
            
            for _, hd_row in batch_df.iterrows():
                # Get corresponding rows from other tables
                ic_row = ic_df.loc[hd_row['UNITID']] if ic_df is not None and hd_row['UNITID'] in ic_df.index else None
                mission_row = mission_df.loc[hd_row['UNITID']] if mission_df is not None and hd_row['UNITID'] in mission_df.index else None
                ay_row = ay_df.loc[hd_row['UNITID']] if ay_df is not None and hd_row['UNITID'] in ay_df.index else None
                
                # Create text chunk
                text = create_text_chunks(hd_row, ic_row, mission_row, ay_row)
                texts.append(text)
                ids.append(f"doc_{hd_row['UNITID']}")
                
                # Combine metadata from all tables
                metadata = hd_row.to_dict()
                if ic_row is not None:
                    metadata.update(ic_row.to_dict())
                if mission_row is not None:
                    metadata.update(mission_row.to_dict())
                if ay_row is not None:
                    metadata.update(ay_row.to_dict())
                metadatas.append(metadata)
            
            # Add batch to collection
            collection.add(
                documents=texts,
                ids=ids,
                metadatas=metadatas
            )
            
            # Print progress
            print(f"Processed {min(i + batch_size, len(hd_df))} out of {len(hd_df)} institutions")
        
        print("Data successfully converted and stored in vector database")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
