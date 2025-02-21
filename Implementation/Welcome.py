import streamlit as st  # type: ignore
import pandas as pd  # type: ignore
import numpy as np  # type: ignore
import seaborn as sns  # type: ignore
import matplotlib.pyplot as plt  # type: ignore
import plotly.express as px  # type: ignore
from datetime import datetime

import warnings

warnings.filterwarnings('ignore')

# Title 
st.set_page_config(page_title="Movie Trends Dashboard", layout="wide")
st.title(":clapper: Welcome to the Movie Trends Dashboard")
st.markdown(
    """
    <style>
    h1 {
    font-size: 40px !important;
    color: #0073e6 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Custom CSS to set a background image
def set_background_image(image_url):
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("{image_url}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-blend-mode: overlay;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Set the background image (replace with your image URL)
set_background_image("https://wallpapers.com/images/featured/movie-9pvmdtvz4cb0xl37.jpg")

# Current Date
st.write(f"Today's Date: {datetime.now().strftime('%B %d, %Y')}")

# Introduction
st.markdown("""
Welcome to the **Movie Trends Dashboard**!  
Dive into the world of movies—track trending films, analyze box office data, explore genre popularity, and more.  
Use the sidebar to navigate through different dashboards and uncover key insights into the film industry.

:star: **Key Features:**
- Top trending movies
- Box office analytics
- Genre & rating breakdown
- Global movie trends

Enjoy exploring and let the data tell the story! 🍿
""")

# Call to Action
st.info("👉 Use the sidebar to get started and explore movie trends!")


# Sidebar for additional information or navigation
st.sidebar.title("Navigation")
st.sidebar.markdown("""
    - **Home**: Welcome page
    - **Trending Movies**: Analyze current movie trends
    - **Genre Analysis**: Explore genre-specific insights
    - **Audience Preferences**: Understand audience behavior over time
""")