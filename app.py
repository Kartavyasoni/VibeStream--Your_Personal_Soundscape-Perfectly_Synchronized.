import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from sklearn.metrics.pairwise import cosine_similarity

# 1. Page Config
st.set_page_config(page_title="VibeStream Intelligence", page_icon="🎵")
st.title("🎵 VibeStream")
st.markdown("### *Your Personal Soundscape, Perfectly Synchronized.*")

# 2. Connect to Database
@st.cache_resource # Keeps connection fast
def get_data():
    engine = create_engine("postgresql://admin:password@localhost:5432/vibestream")
    df = pd.read_sql("SELECT * FROM processed_tracks", engine)
    return df

df = get_data()

# 3. Search UI
# Add a 'Vibe Slider' to the sidebar
st.sidebar.header("Fine-Tune Your Vibe")
dance_filter = st.sidebar.slider("Minimum Danceability", 0.0, 1.0, 0.5)

# Update your search logic to filter by this value
target_song = st.text_input("Enter a song you love:", "Guerrilla Radio")

if st.button("Generate Vibe"):
    # Recommendation Logic
    vibe_dna = ['danceability', 'energy', 'speechiness', 'acousticness', 
                'instrumentalness', 'liveness', 'valence', 'tempo_scaled', 'loudness_scaled']
    
    input_song = df[df['name'].str.contains(target_song, case=False)].head(1)
    
    if not input_song.empty:
        input_vector = input_song[vibe_dna].values
        # Fast Search on 100k songs
        sample_df = df.sample(100000)
        similarities = cosine_similarity(input_vector, sample_df[vibe_dna].values)
        sample_df['similarity'] = similarities[0]
        
        results = sample_df[sample_df['danceability'] >= dance_filter].sort_values('similarity', ascending=False).head(6)
        
        st.write(f"Because you liked **{input_song['name'].values[0]}**...")
        for _, row in results.iloc[1:].iterrows():
            st.success(f"**{row['name']}** by {row['artists']} (Match: {round(row['similarity']*100, 1)}%)")
    else:
        st.error("Song not found. Try another one!")