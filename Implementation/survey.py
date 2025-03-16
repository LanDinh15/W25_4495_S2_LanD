import streamlit as st # type: ignore
import warnings

warnings.filterwarnings('ignore')

# Title of the dashboard
st.title("Movie Trend Dashboard")

# Survey Section
st.header("Tell Us Your Preferences")

# Question 1: Mood
mood = st.selectbox(
    "What’s your mood today?",
    ["Happy", "Sad", "Excited", "Relaxed", "Stressed"]
)

# Question 2: Movie Genre
genre = st.radio(
    "What movie genre are you in the mood for today?",
    ["Action", "Comedy", "Drama", "Horror", "Sci-Fi", "Romance"]
)

# Question 3: Duration
duration = st.slider(
    "How long should the movie be? (in minutes)",
    min_value=30,  
    max_value=240,  
    value=120,      
    step=10         
)

# Display the collected responses
st.write("### Your Preferences:")
st.write(f"Mood: {mood}")
st.write(f"Genre: {genre}")
st.write(f"Duration: {duration} minutes")

# Optional: Button to submit
if st.button("Submit"):
    st.success("Thanks for sharing your preferences!")
