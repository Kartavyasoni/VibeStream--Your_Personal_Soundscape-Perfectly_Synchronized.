import pandas as pd
from sqlalchemy import create_engine
import time
import os
from dotenv import load_dotenv

# 1. Setup Environment
load_dotenv()
# Using the credentials from your docker-compose.yml
DB_URL = "postgresql://admin:password@localhost:5432/vibestream"
engine = create_engine(DB_URL)

# 2. Path to your dataset
# Make sure the filename matches exactly what is in your data/raw folder
CSV_PATH = "Data/Raw/tracks_features.csv" 

def load_vibestream_data(file_path, table_name, chunk_size=50000):
    """Loads a massive CSV into PostgreSQL in manageable chunks."""
    start_time = time.time()
    print(f"🚀Initializing VibeStream Bulk Load for: {CSV_PATH}")
    
    try:
        # Create an iterator to read the file in chunks
        reader = pd.read_csv(file_path, chunksize=chunk_size)
        
        for i, chunk in enumerate(reader):
            # 'replace' for the 1st chunk to create the table, 'append' for the rest
            mode = 'replace' if i == 0 else 'append'
            
            # Write to SQL
            chunk.to_sql(name=table_name, con=engine, if_exists=mode, index=False)
            
            elapsed = round(time.time() - start_time, 2)
            print(f"✅ Chunk {i+1} loaded... ({chunk_size * (i+1)} rows total) | Time: {elapsed}s")
            
        print(f"\n✨ SUCCESS: 1.2M+ songs are now live in the 'raw_tracks' table!")
        print(f"Total time taken: {round(time.time() - start_time, 2)} seconds.")

    except Exception as e:
        print(f"❌ Error during load: {e}")

if __name__ == "__main__":
    load_vibestream_data(CSV_PATH, 'raw_tracks')