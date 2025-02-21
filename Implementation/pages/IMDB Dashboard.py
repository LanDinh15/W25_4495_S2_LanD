import streamlit as st # type: ignore
import pandas as pd # type: ignore
import numpy as np # type: ignore
import seaborn as sns # type: ignore
import matplotlib.pyplot as plt # type: ignore
import plotly.express as px # type: ignore
from datetime import datetime

import warnings

warnings.filterwarnings('ignore')

# Title 
st.title(":round_pushpin: IMDB Movies Trends")
st.markdown(
    """
    <style>
    h1 {
    font-size: 40px !important;
    color: #FFA500 !important;
    }
    </style>
    """, unsafe_allow_html=True)
imdb_image = "https://upload.wikimedia.org/wikipedia/commons/thumb/6/69/IMDB_Logo_2016.svg/1280px-IMDB_Logo_2016.svg.png"
st.image(imdb_image, use_column_width="always")

# Load data
df = pd.read_csv('imdb_top_1000.csv')

# Handling missing values
df.Certificate = df.Certificate.fillna('Unrated')
df['Meta_score']= df['Meta_score'].fillna(df['Meta_score'].mode()[0])
df.Gross = df.Gross.fillna(df.Gross.mode()[0])

# Split genres
df['Genre'] = df['Genre'].astype(str)
genre_content = df.assign(genre=df.Genre.str.split(',')).explode('Genre')
genre_content['Genre'] =  genre_content['Genre'].str.strip()

# print the table 
df