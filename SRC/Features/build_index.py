import pandas as pd
import faiss
import numpy as np
from sqlalchemy import create_engine
import joblib

# 1. Load the processed data
engine = create_engine("postgresql://admin:password@localhost:5432/vibestream")
df = pd.read_sql("SELECT * FROM processed_tracks", engine)

# 2. Prepare the Vectors (The Musical DNA)
vibe_dna = ['danceability', 'energy', 'speechiness', 'acousticness', 
            'instrumentalness', 'liveness', 'valence', 'tempo_scaled', 'loudness_scaled']
data_vectors = df[vibe_dna].values.astype('float32')

# 3. Create the FAISS Index
dimension = data_vectors.shape[1]
# 'IndexFlatL2' is excellent for accurate similarity search
index = faiss.IndexFlatL2(dimension)
index.add(data_vectors)

# 4. Save the Index and the DataFrame for the UI to use
faiss.write_index(index, "Models/vibe_index.faiss")
# We save the metadata (names/artists) separately
df[['name', 'artists']].to_pickle("Models/metadata.pkl")

print(f"✨ Successfully indexed {len(df)} songs into the Vibe Index!")