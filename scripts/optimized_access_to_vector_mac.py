import subprocess
import csv
import io
import chromadb
from chromadb.utils import embedding_functions
import pandas as pd
from tqdm import tqdm
import os
import sys
import time
import concurrent.futures
from functools import partial
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
        df = pd.read_csv(io.StringIO(result.stdout))
        print(f"Successfully loaded {table_name} with {len(df)} rows")
        return df
    except subprocess.CalledProcessError as e:
        print(f"Error executing mdb-export for {table_name}: {e}")
        return None
    except pd.errors.EmptyDataError:
        print(f"No data in table {table_name}")
        return None

def create_text_chunks(institution_data):
    """Create a comprehensive text chunk for the institution from its data"""
    
    text_parts = []
    
    # Basic information
    if 'HD2023' in institution_data:
        hd = institution_data['HD2023']
        
        # Institution name and location
        if 'INSTNM' in hd:
            text_parts.append(f"Institution: {hd['INSTNM']}")
        
        # Address
        address_parts = []
        for field in ['ADDR', 'CITY', 'STABBR', 'ZIP']:
            if field in hd and pd.notnull(hd.get(field)):
                address_parts.append(str(hd[field]))
        
        if address_parts:
            text_parts.append(f"Address: {', '.join(address_parts)}")
        
        # Type of institution
        if 'CONTROL' in hd:
            control_map = {1: "Public", 2: "Private non-profit", 3: "Private for-profit"}
            control = control_map.get(hd['CONTROL'], f"Other (code: {hd['CONTROL']})")
            text_parts.append(f"Control: {control}")
        
        if 'ICLEVEL' in hd:
            level_map = {1: "Four or more years", 2: "At least 2 but less than 4 years", 3: "Less than 2 years"}
            level = level_map.get(hd['ICLEVEL'], f"Other (code: {hd['ICLEVEL']})")
            text_parts.append(f"Level: {level}")
        
        # Website
        if 'WEBADDR' in hd and pd.notnull(hd.get('WEBADDR')):
            text_parts.append(f"Website: {hd['WEBADDR']}")
    
    # Mission statement
    if 'IC2023Mission' in institution_data:
        mission = institution_data['IC2023Mission']
        if 'MISSION' in mission and pd.notnull(mission.get('MISSION')):
            text_parts.append(f"Mission Statement: {mission['MISSION']}")
        elif 'missionURL' in mission and pd.notnull(mission.get('missionURL')):
            text_parts.append(f"Mission Statement URL: {mission['missionURL']}")
    
    # Cost information
    if 'IC2023_AY' in institution_data:
        cost = institution_data['IC2023_AY']
        cost_info = []
        
        # Tuition and fees for in-state, out-of-state, and other
        tuition_fields = {
            'TUITION1': "In-state tuition",
            'TUITION2': "Out-of-state tuition",
            'TUITION3': "Other tuition",
            'FEES1': "In-state fees",
            'FEES2': "Out-of-state fees"
        }
        
        for field, label in tuition_fields.items():
            if field in cost and pd.notnull(cost.get(field)):
                cost_info.append(f"{label}: ${cost[field]:,}")
        
        if cost_info:
            text_parts.append("Costs:")
            text_parts.extend([f"  - {item}" for item in cost_info])
    
    # Admissions data
    if 'ADM2023' in institution_data:
        adm = institution_data['ADM2023']
        adm_info = []
        
        adm_fields = {
            'APPLCN': "Applications received",
            'ADMSSN': "Admissions offers",
            'ENRLT': "Enrolled students"
        }
        
        for field, label in adm_fields.items():
            if field in adm and pd.notnull(adm.get(field)):
                adm_info.append(f"{label}: {adm[field]:,}")
        
        # Calculate admission rate if both fields are available
        if 'APPLCN' in adm and 'ADMSSN' in adm and pd.notnull(adm.get('APPLCN')) and pd.notnull(adm.get('ADMSSN')) and adm['APPLCN'] > 0:
            adm_rate = (adm['ADMSSN'] / adm['APPLCN']) * 100
            adm_info.append(f"Admission rate: {adm_rate:.1f}%")
        
        if adm_info:
            text_parts.append("Admissions:")
            text_parts.extend([f"  - {item}" for item in adm_info])
    
    # Enrollment data
    if 'EF2023' in institution_data:
        ef = institution_data['EF2023']
        enroll_info = []
        
        enroll_fields = {
            'EFUG': "Undergraduate enrollment",
            'EFGRAD': "Graduate enrollment",
            'EFTOTLT': "Total enrollment"
        }
        
        for field, label in enroll_fields.items():
            if field in ef and pd.notnull(ef.get(field)):
                enroll_info.append(f"{label}: {ef[field]:,}")
        
        if enroll_info:
            text_parts.append("Enrollment:")
            text_parts.extend([f"  - {item}" for item in enroll_info])
    
    # Demographics
    if 'EF2023A' in institution_data:
        efa = institution_data['EF2023A']
        demo_info = []
        
        # Gender breakdown
        if 'EFTOTLM' in efa and 'EFTOTLW' in efa and pd.notnull(efa.get('EFTOTLM')) and pd.notnull(efa.get('EFTOTLW')):
            total = efa['EFTOTLM'] + efa['EFTOTLW']
            if total > 0:
                male_pct = (efa['EFTOTLM'] / total) * 100
                female_pct = (efa['EFTOTLW'] / total) * 100
                demo_info.append(f"Gender: {male_pct:.1f}% male, {female_pct:.1f}% female")
        
        # Race/ethnicity
        race_fields = {
            'EFAIANT': "American Indian/Alaska Native",
            'EFASIAT': "Asian",
            'EFBKAAT': "Black/African American",
            'EFHISPT': "Hispanic/Latino",
            'EFNHPIT': "Native Hawaiian/Pacific Islander",
            'EFWHITT': "White",
            'EF2MORT': "Two or more races",
            'EFNRALT': "Race/ethnicity unknown"
        }
        
        race_data = []
        for field, label in race_fields.items():
            if field in efa and pd.notnull(efa.get(field)) and efa[field] > 0:
                race_data.append((label, efa[field]))
        
        # Calculate percentages
        total_race = sum(count for _, count in race_data)
        if total_race > 0:
            race_pcts = []
            for label, count in race_data:
                pct = (count / total_race) * 100
                if pct >= 1.0:  # Only include if at least 1%
                    race_pcts.append(f"{label}: {pct:.1f}%")
            
            if race_pcts:
                demo_info.append("Race/Ethnicity:")
                demo_info.extend([f"  - {item}" for item in race_pcts])
        
        if demo_info:
            text_parts.append("Demographics:")
            text_parts.extend([f"  - {item}" for item in demo_info])
    
    # Graduation rates
    if 'GR2023' in institution_data:
        gr = institution_data['GR2023']
        grad_info = []
        
        # Overall graduation rate
        if 'GRTOTLT' in gr and pd.notnull(gr.get('GRTOTLT')):
            # Graduation rates are stored as whole numbers (e.g., 6004 for 60.04%)
            # Divide by 100 to get the proper percentage
            grad_rate = gr['GRTOTLT'] / 100 if gr['GRTOTLT'] > 100 else gr['GRTOTLT']
            grad_info.append(f"Overall graduation rate: {grad_rate:.1f}%")
        
        if grad_info:
            text_parts.append("Graduation Rates:")
            text_parts.extend([f"  - {item}" for item in grad_info])
    
    # Financial data - F1A for public institutions
    if 'F2223_F1A' in institution_data:
        f1a = institution_data['F2223_F1A']
        fin_info = []
        
        # Selected financial indicators
        fin_fields = {
            'F1A18': "Total revenues and other additions",
            'F1A181': "Tuition and fees",
            'F1A43': "Total expenses and other deductions",
            'F1A06': "Instruction expenses",
            'F1A11': "Research expenses",
            'F1A121': "Public service expenses",
            'F1A02': "Total assets"
        }
        
        for field, label in fin_fields.items():
            if field in f1a and pd.notnull(f1a.get(field)):
                fin_info.append(f"{label}: ${f1a[field]:,}")
        
        if fin_info:
            text_parts.append("Financial Data (Public Institution):")
            text_parts.extend([f"  - {item}" for item in fin_info])
    
    # Financial data - F2 for private for-profit institutions
    if 'F2223_F2' in institution_data:
        f2 = institution_data['F2223_F2']
        fin_info = []
        
        # Selected financial indicators
        fin_fields = {
            'F2D01': "Total revenues and investment return",
            'F2D0111': "Tuition and fees",
            'F2D02': "Total expenses",
            'F2C19': "Total assets",
            'F2C08A': "Total liabilities"
        }
        
        for field, label in fin_fields.items():
            if field in f2 and pd.notnull(f2.get(field)):
                fin_info.append(f"{label}: ${f2[field]:,}")
        
        if fin_info:
            text_parts.append("Financial Data (Private For-Profit Institution):")
            text_parts.extend([f"  - {item}" for item in fin_info])
    
    # Financial data - F3 for private not-for-profit institutions
    if 'F2223_F3' in institution_data:
        f3 = institution_data['F2223_F3']
        fin_info = []
        
        # Selected financial indicators
        fin_fields = {
            'F3D01': "Total revenues and investment return",
            'F3D0111': "Tuition and fees",
            'F3D02': "Total expenses",
            'F3D06': "Instruction expenses",
            'F3D07': "Research expenses",
            'F3D08': "Public service expenses",
            'F3C19': "Total assets",
            'F3C08A': "Total liabilities",
            'F3H01': "Value of endowment assets"
        }
        
        for field, label in fin_fields.items():
            if field in f3 and pd.notnull(f3.get(field)):
                fin_info.append(f"{label}: ${f3[field]:,}")
        
        if fin_info:
            text_parts.append("Financial Data (Private Non-Profit Institution):")
            text_parts.extend([f"  - {item}" for item in fin_info])
        
    return " ".join(text_parts)

def process_institution_batch(batch_df, table_data):
    """Process a batch of institutions and return their text, ids, and metadata"""
    texts = []
    ids = []
    metadatas = []
    
    for _, hd_row in batch_df.iterrows():
        try:
            # Convert UNITID to int to ensure it matches the DataFrame index type
            if pd.isna(hd_row['UNITID']):
                continue
                
            unit_id = int(hd_row['UNITID'])
            
            # Aggregate data from all tables for this institution
            institution_data = {}
            
            # First check if the unit_id exists in each dataframe's index
            for table_name, df in table_data.items():
                try:
                    # Skip tables that aren't DataFrames
                    if not isinstance(df, pd.DataFrame):
                        continue
                        
                    # Check if the unit_id is in the DataFrame's index
                    if unit_id not in df.index:
                        continue
                        
                    # Get the row(s) for this unit_id
                    row_data = df.loc[unit_id]
                    
                    if isinstance(row_data, pd.Series):
                        institution_data[table_name] = row_data.to_dict()
                    else:  # DataFrame with multiple rows
                        # For EF2023A, filter to specific rows
                        if table_name == "EF2023A":
                            filtered_rows = row_data[(row_data['EFALEVEL'] == 1) & (row_data['LINE'] == 29)]
                            if not filtered_rows.empty:
                                institution_data[table_name] = filtered_rows.iloc[0].to_dict()
                        else:
                            # Just use the first row for simplicity
                            institution_data[table_name] = row_data.iloc[0].to_dict()
                except Exception:
                    # Skip silently
                    continue
            
            # Create text chunk
            text = create_text_chunks(institution_data)
            texts.append(text)
            ids.append(f"doc_{unit_id}")
            
            # Create metadata from selected fields
            metadata = {"UNITID": unit_id}
            
            # Add basic name from HD2023
            if 'HD2023' in institution_data and isinstance(institution_data['HD2023'], dict):
                if 'INSTNM' in institution_data['HD2023']:
                    metadata["INSTNM"] = institution_data['HD2023']['INSTNM']
            
            # Add important metadata from each table
            metadata_field_map = {
                "HD2023": ["CITY", "STABBR", "ZIP", "SECTOR", "ICLEVEL", "CONTROL", "WEBADDR"],
                "IC2023_AY": ["TUITION1", "TUITION2", "TUITION3", "FEES1", "FEES2"],
                "ADM2023": ["APPLCN", "ADMSSN", "ENRLT"],
                "EF2023": ["EFUG", "EFGRAD", "EFTOTLT"],
                "EF2023A": ["EFTOTLM", "EFTOTLW", "EFAIANT", "EFASIAT", "EFBKAAT", "EFHISPT", "EFNHPIT", "EFWHITT", "EF2MORT", "EFNRALT"],
                "GR2023": ["GRTOTLT", "GRCODEP"],
                "IC2023Mission": ["MISSION", "missionURL"],
                "F2223_F1A": ["F1A18", "F1A43", "F1A02"],
                "F2223_F2": ["F2D01", "F2D02", "F2C19"],
                "F2223_F3": ["F3D01", "F3D02", "F3C19", "F3H01"]
            }
            
            for table_name, table_data_dict in institution_data.items():
                # Skip if not a dict or table not in our field map
                if not isinstance(table_data_dict, dict) or table_name not in metadata_field_map:
                    continue
                    
                # Add selected metadata fields
                for field in metadata_field_map[table_name]:
                    if field in table_data_dict and pd.notnull(table_data_dict.get(field, None)):
                        value = table_data_dict[field]
                        metadata[field] = value
            
            metadatas.append(metadata)
            
        except Exception as e:
            # Silently continue on error
            continue
            
    return texts, ids, metadatas

def main():
    """Main function with optimizations for speed"""
    # Configuration
    ACCESS_DB_PATH = "/Users/anthonytiburcio/Documents/GitHub/schoolmatch_v1/db/ipeds_data/IPEDS202324.accdb"
    CHROMA_PERSIST_DIR = "/Users/anthonytiburcio/Documents/GitHub/schoolmatch_v1/chroma_db"
    
    # Tables to extract (add or remove as needed)
    TABLES = [
        "HD2023",           # Basic institutional characteristics
        "IC2023",           # Institutional characteristics
        "IC2023Mission",    # Mission statements
        "IC2023_AY",        # Academic year data
        "ADM2023",          # Admissions data
        "EF2023",           # Enrollment
        "EF2023A",          # Enrollment by race/ethnicity
        "GR2023",           # Graduation rates
        "F2223_F1A",        # Finance data - Public institutions
        "F2223_F2",         # Finance data - Private for-profit institutions
        "F2223_F3",         # Finance data - Private not-for-profit institutions
    ]
    
    start_time = time.time()
    print(f"Starting data processing at {time.strftime('%H:%M:%S')}")
    
    try:
        # Get user confirmation before recreating collection
        recreate = input("Do you want to recreate the collection? This will delete existing data. (y/n): ")
        
        # Initialize ChromaDB client with OpenAI embedding function
        # Notice: Using the embedding function directly from ChromaDB instead of langchain
        openai_ef = embedding_functions.OpenAIEmbeddingFunction(
            api_key=os.getenv("OPENAI_API_KEY"),
            model_name="text-embedding-ada-002"
        )
        
        # Initialize ChromaDB persistent client
        chroma_client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
        
        # Handle collection management
        collection_name = "ipeds_colleges"
        collection = None
        
        try:
            # Try to get existing collection
            collection = chroma_client.get_collection(
                name=collection_name,
                embedding_function=openai_ef
            )
            print("Found existing collection")
            
            # Check if we should recreate
            if recreate.lower() == 'y':
                chroma_client.delete_collection(name=collection_name)
                print("Deleted existing collection")
                # Create new collection
                collection = chroma_client.create_collection(
                    name=collection_name,
                    embedding_function=openai_ef
                )
                print("Created new collection")
        except Exception as e:
            # Collection doesn't exist, create a new one
            print(f"No existing collection found: {e}")
            collection = chroma_client.create_collection(
                name=collection_name,
                embedding_function=openai_ef
            )
            print("Created new collection")
        
        # Ask for sample mode for faster testing
        sample_mode = input("Do you want to run in sample mode with only 100 institutions? (y/n): ")
        
        # Load data from all tables
        print("Loading data from tables...")
        table_data = {}
        
        # OPTIMIZATION: Load tables concurrently
        # First create a function to load a table
        def load_table(table):
            df = get_table_data_mdb(ACCESS_DB_PATH, table)
            if df is not None:
                # Index on UNITID if present
                if 'UNITID' in df.columns:
                    df.set_index('UNITID', inplace=True)
                elif 'unitid' in df.columns:
                    df.set_index('unitid', inplace=True)
                return table, df
            return table, None
        
        # Load tables concurrently with ThreadPoolExecutor
        with concurrent.futures.ThreadPoolExecutor(max_workers=min(len(TABLES), 4)) as executor:
            results = list(executor.map(load_table, TABLES))
            
        # Process results
        for table, df in results:
            if df is not None:
                table_data[table] = df
            
        # Special handling for EF2023A
        if "EF2023A" in table_data and isinstance(table_data["EF2023A"], pd.DataFrame):
            # For EF2023A, filter to specific rows
            ef2023a_df = table_data["EF2023A"]
            ef2023a_df = ef2023a_df[(ef2023a_df['EFALEVEL'] == 1) & (ef2023a_df['LINE'] == 29)]
            table_data["EF2023A"] = ef2023a_df
            
        if "HD2023" not in table_data or table_data["HD2023"] is None:
            print("Error: HD2023 table is required but couldn't be loaded")
            return
            
        # Process the main table
        hd_df = table_data["HD2023"].reset_index()
        
        # Use a sample if requested
        if sample_mode.lower() == 'y':
            hd_df = hd_df.sample(n=min(100, len(hd_df)))
            print(f"Using a sample of {len(hd_df)} institutions")
        else:
            print(f"Processing all {len(hd_df)} institutions")
        
        # OPTIMIZATION: Use larger batch sizes for processing
        batch_size = 500  # Increased from 250 
        total_processed = 0
        num_batches = (len(hd_df) + batch_size - 1) // batch_size
        
        print(f"Using batch size of {batch_size}")
        
        # Process in batches
        for i in tqdm(range(0, len(hd_df), batch_size), desc="Processing institution batches", total=num_batches):
            batch_df = hd_df.iloc[i:i + batch_size]
            
            # Process the batch
            texts, ids, metadatas = process_institution_batch(batch_df, table_data)
            
            if not texts:  # Skip if no valid texts
                continue
                
            # OPTIMIZATION: Add to ChromaDB in larger chunks
            sub_batch_size = 200  # Increased from 50
            for j in range(0, len(texts), sub_batch_size):
                end_idx = min(j + sub_batch_size, len(texts))
                
                # Only add if we have valid data
                if end_idx > j:
                    try:
                        # Add batch directly to collection
                        collection.add(
                            documents=texts[j:end_idx],
                            metadatas=metadatas[j:end_idx],
                            ids=ids[j:end_idx]
                        )
                        total_processed += end_idx - j
                    except Exception as sub_e:
                        print(f"Error adding sub-batch: {str(sub_e)}")
                        # Continue with next sub-batch
                        continue
                
        print(f"\nProcessed {total_processed} institutions and stored them in vector database")
        elapsed_time = time.time() - start_time
        print(f"Total processing time: {elapsed_time:.2f} seconds ({elapsed_time/60:.2f} minutes)")
        
        # Display a sample query
        sample_query = input("\nEnter a school name to test search: ")
        if not sample_query:
            sample_query = "Stanford University"
        
        print(f"Testing with query: '{sample_query}'")
        
        try:
            results = collection.query(
                query_texts=[sample_query],
                n_results=3  # Get top 3 results
            )
            
            if results['documents'] and results['documents'][0]:
                print("\nTop matching results:")
                
                for i, (doc, metadata, id, distance) in enumerate(zip(
                    results['documents'][0], 
                    results['metadatas'][0], 
                    results['ids'][0],
                    results['distances'][0]
                )):
                    print(f"\n--- Result {i+1} (Distance: {distance:.4f}) ---")
                    print(f"Institution: {metadata.get('INSTNM', 'Unknown')}")
                    print(f"Location: {metadata.get('CITY', 'Unknown')}, {metadata.get('STABBR', 'Unknown')}")
                    print(f"UNITID: {metadata.get('UNITID', 'Unknown')}")
                    
                    print("\nDocument excerpt:")
                    # Show a reasonable amount of text
                    excerpt = doc[:1000] + "..." if len(doc) > 1000 else doc
                    print(excerpt)
                    
                    print("\nKey metadata fields:")
                    # Display a selection of important metadata
                    for key in ['SECTOR', 'CONTROL', 'ICLEVEL', 'TUITION1', 'EFUG', 'EFGRAD', 'GRTOTLT']:
                        if key in metadata:
                            print(f"{key}: {metadata[key]}")
            else:
                print("No results found. Try running without sample mode to include more institutions.")
        except Exception as e:
            print(f"Error performing test query: {str(e)}")
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        import traceback
        traceback.print_exc()
        return

if __name__ == "__main__":
    main()
