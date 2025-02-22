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
df['Gross'] = df['Gross'].str.replace(',', '').fillna(0).astype(float)

# Change release year to numeric
df['Released_Year'] = pd.to_numeric(df['Released_Year'], errors='coerce')
df = df.dropna(subset=['Released_Year'])
df['Released_Year'] = df['Released_Year'].astype(int)
# Change runtime to numeric
df['Runtime'] = df['Runtime'].str.extract(r'(\d+)').astype(float)
# Change gross to numeric
df['Gross'] = pd.to_numeric(df['Gross'], errors='coerce')/1e6
df = df.rename(columns={'Runtime':'Runtime (min)','Gross':'Gross (M)'}) # rename columns to include metric

# Split genres
df['Genre'] = df['Genre'].astype(str)
genre_content = df.assign(genre=df.Genre.str.split(',')).explode('Genre')
genre_content['Genre'] =  genre_content['Genre'].str.strip()

# Add navigation filters for IMDB_Rating and Meta_score
st.sidebar.header("Choose your filter: ")

# Slider for IMDB_Rating
imdb_min, imdb_max = df['IMDB_Rating'].min(), df['IMDB_Rating'].max()
imdb_range = st.sidebar.slider(
    "Select IMDB Rating Range:",
    min_value=float(imdb_min),
    max_value=float(imdb_max),
    value=(float(imdb_min), float(imdb_max)),
    step = 0.1,
    format = "%.1f")

# Slider for Meta_score
meta_min, meta_max = df['Meta_score'].min(), df['Meta_score'].max()
meta_range = st.sidebar.slider(
    "Select Meta Score Range:",
    min_value=float(meta_min),
    max_value=float(meta_max),
    value=(float(meta_min), float(meta_max)),
    step = 10.0,
    format = "%f",
)  

# Filter the dataset based on selected ranges
filtered_df = df[
    (df['IMDB_Rating'] >= imdb_range[0]) &
    (df['IMDB_Rating'] <= imdb_range[1]) &
    (df['Meta_score'] >= meta_range[0]) &
    (df['Meta_score'] <= meta_range[1])
]

# Display filtered dataset (optional)
st.write(f"Filtered Dataset ({len(filtered_df)} rows):")
st.dataframe(filtered_df.head())

# 1. Top 10 Directors by Gross (M)
directors = filtered_df.groupby('Director')['Gross (M)'].sum().reset_index()
directors_sorted = directors.sort_values(by='Gross (M)', ascending=False)
top_10_directors = directors_sorted.head(10)
# Create an interactive bar chart
fig = px.bar(
    top_10_directors,
    x='Director',
    y='Gross (M)',
    text=[f"${gross:.2f}M" for gross in top_10_directors['Gross (M)']], 
    title='Top 10 Directors by Gross Earnings (M)',
    labels={'Gross(M)': 'Total Gross Earnings (M)', 'Director': 'Director'},
    color='Gross (M)',  # Color bars by gross earnings
    color_continuous_scale='Viridis'  # Use a color scale
)
# Customize the layout
fig.update_layout(
    xaxis_title='Director',
    yaxis_title='Total Gross Earnings (M)',
    xaxis_tickangle=-45,  # Rotate director names for better readability
    template='plotly_white',  # Use a clean template
    showlegend=False
)
# Display the plot
st.plotly_chart(fig, use_container_width=True)

# 2. Top 10 Actors by Gross (M)
actors_1 = filtered_df.groupby('Star1')['Gross (M)'].sum().reset_index().rename(columns={'Star1': 'Actor', 'Gross (M)': 'Gross_1'})
actors_2 = filtered_df.groupby('Star2')['Gross (M)'].sum().reset_index().rename(columns={'Star2': 'Actor', 'Gross (M)': 'Gross_2'})
actors_3 = filtered_df.groupby('Star3')['Gross (M)'].sum().reset_index().rename(columns={'Star3': 'Actor', 'Gross (M)': 'Gross_3'})
actors_4 = filtered_df.groupby('Star4')['Gross (M)'].sum().reset_index().rename(columns={'Star4': 'Actor', 'Gross (M)': 'Gross_4'})

# Merge all datasets on 'Actor' and use 'outer' join to keep all actors
actors_merged = actors_1
for df_actor in [actors_2, actors_3, actors_4]:
    actors_merged = pd.merge(actors_merged, df_actor, on='Actor', how='outer')

actors_merged['Gross (M)'] = actors_merged[['Gross_1', 'Gross_2', 'Gross_3', 'Gross_4']].sum(axis=1)
actors_merged = actors_merged.drop(columns=['Gross_1', 'Gross_2', 'Gross_3', 'Gross_4'])
actors_sorted = actors_merged.sort_values(by='Gross (M)', ascending=False)
top_10_actors = actors_sorted.head(10)

# Create an interactive bar chart
fig = px.bar(
    top_10_actors,
    x='Actor',
    y='Gross (M)',
    text=[f"${gross:.2f}M" for gross in top_10_actors['Gross (M)']],
    title='Top 10 Actors by Gross Earnings (M)',
    labels={'Gross (M)': 'Total Gross Earnings (M)', 'Actor': 'Actor'},
    color='Gross (M)',  # Color bars by gross earnings
    color_continuous_scale='Viridis'  # Use a color scale
)

# Customize the layout
fig.update_layout(
    xaxis_title='Actor',
    yaxis_title='Total Gross Earnings (M)',
    xaxis_tickangle=-45,  # Rotate actor names for better readability
    template='plotly_white',  # Use a clean template
    showlegend=False  # Hide the legend
)

# Display the interactive plot in Streamlit
st.plotly_chart(fig, use_container_width=True)