import streamlit as st
import pandas as pd
import faiss
import time
import numpy as np
import pickle
from sqlalchemy import create_engine

# 1. Page Config
st.set_page_config(page_title="VibeStream Intelligence", page_icon="🎵", layout="wide")
st.title("🎵 VibeStream")
st.markdown("### *Your Personal Soundscape, Perfectly Synchronized.*")

# 2. Load the High-Speed Index, Metadata, and Database Engine
@st.cache_resource 
def load_resources():
    # Load High-Performance Vector Index
    index = faiss.read_index("models/vibe_index.faiss")
    with open("models/metadata.pkl", "rb") as f:
        metadata = pickle.load(f)
    # Database Engine for real-time DNA lookups
    engine = create_engine("postgresql://admin:password@localhost:5432/vibestream")
    return index, metadata, engine

index, metadata, engine = load_resources()

# 3. Session State Management (Vibe History)
if 'history' not in st.session_state:
    st.session_state['history'] = []

# 4. Sidebar: Vibe Tuning & Mood Presets
st.sidebar.header("🎚️ Vibe Tuning")
diversity_slider = st.sidebar.slider("Discovery Level (Randomness)", 0.0, 0.2, 0.05, 
                                     help="Higher values discover 'riskier' song matches.")

st.sidebar.markdown("---")
st.sidebar.subheader("Quick Moods")
mood = st.sidebar.radio("Select a Vibe:", ["Custom", "High Energy 🔥", "Chill Study 📚", "Dark & Moody 🌙"])

# Mood Logic
if mood == "High Energy 🔥":
    diversity = 0.15
elif mood == "Chill Study 📚":
    diversity = 0.02
elif mood == "Dark & Moody 🌙":
    diversity = 0.01
else:
    diversity = diversity_slider

# History Sidebar
if st.session_state['history']:
    st.sidebar.markdown("---")
    st.sidebar.subheader("🕒 Recent Vibes")
    for h_song in st.session_state['history']:
        st.sidebar.caption(f"🎵 {h_song}")

# 5. Search UI
target_song_input = st.text_input("What song are you feeling right now?", "Guerrilla Radio")

if st.button("Generate Vibe"):
    start_time = time.time() # Start Performance Profiling
    target_song = target_song_input.strip()
    
    # SQL Lookup: Fetching specific track DNA
    query = "SELECT * FROM processed_tracks WHERE name ILIKE %s LIMIT 1"
    song_dna_row = pd.read_sql(query, engine, params=(f"%{target_song}%",))
    
    if not song_dna_row.empty:
        # Update Session History
        song_name = song_dna_row['name'].values[0]
        if song_name not in st.session_state['history']:
            st.session_state['history'].insert(0, song_name)
            st.session_state['history'] = st.session_state['history'][:5]

        # Extract Musical DNA
        vibe_dna = ['danceability', 'energy', 'speechiness', 'acousticness', 
                    'instrumentalness', 'liveness', 'valence', 'tempo_scaled', 'loudness_scaled']
        
        # Prepare Vector for FAISS Search
        query_vector = song_dna_row[vibe_dna].values.astype('float32')
        
        if diversity > 0:
            query_vector += np.random.normal(0, diversity, query_vector.shape).astype('float32')

        # FAISS SEARCH: Nearest Neighbor Retrieval across 1.2M songs
        distances, indices = index.search(query_vector, 6) 
        
        latency = round((time.time() - start_time) * 1000, 2)
        st.caption(f"🚀 AI Engine searched 1,204,022 tracks in {latency}ms")

        st.write(f"### ✨ Recommendations based on *{song_name}*")
        
        # Display Results in expandable cards
        for i in range(1, len(indices[0])): 
            idx = indices[0][i]
            result_song = metadata.iloc[idx]
            
            # Convert L2 distance to intuitive Similarity %
            raw_distance = distances[0][i]
            match_percent = max(0, round(100 - raw_distance, 2))

            with st.container():
                with st.expander(f"🎵 {result_song['name']} — {result_song['artists']}"):
                    st.write(f"**Vibe Match:** {match_percent:.2f}%")
                    
                    # Safe URL Formatting for Spotify Search
                    search_query = f"{result_song['name']} {result_song['artists']}".replace(" ", "%20")
                    spotify_link = f"https://open.spotify.com/search/{search_query}"
                    st.link_button("Listen on Spotify", spotify_link)
        
    else:
        st.error("Song DNA not found in the 1.2M track library. Try a different track!")