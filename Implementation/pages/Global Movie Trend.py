import streamlit as st # type: ignore
import pandas as pd # type: ignore
import numpy as np # type: ignore
import seaborn as sns # type: ignore
import matplotlib.pyplot as plt # type: ignore
import plotly.express as px # type: ignore
from datetime import datetime

import warnings

warnings.filterwarnings('ignore')
st.set_page_config(layout="wide")

# Title and Netflix image
color = ["#C00000", "#000000"]
st.title(":round_pushpin: Global Movies Trend")
st.markdown(
    """
    <style>
    h1 {
    font-size: 40px !important;
    color: #DD0000 !important;
    }
    </style>
    """, unsafe_allow_html=True)
netflix_image = "https://entrevue.fr/wp-content/uploads/2025/01/netflix-decouvrez-les-nouveautes-de-la-semaine-y-compris-la-tant-attendue-suite-dun-immense-succes-750x410-1.jpg"
st.image(netflix_image, use_column_width="always")

# Load the data
df = pd.read_csv("netflix_titles.csv", decimal=',')

# Filling null values
df = df.dropna(subset=["date_added", "duration"]) # Drop rows where date_added and duration is missing
df['rating'] = df['rating'].fillna(df['rating'].mode()[0])
df['duration'] = df['duration'].fillna(df['duration'].mode()[0])
df['country'] = df['country'].fillna(df['country'].mode()[0])
df['cast'] = df['cast'].fillna('Unknown')
df['director'] = df['director'].fillna("Unknown")

# Change the date_added column into datetime datatype
df['date_added'] = df['date_added'].str.strip()
df['date_added'] = pd.to_datetime(df['date_added'], format='%B %d, %Y', errors='coerce')
df['date_added'].head()

# Change duration column into float
df["duration"] = df["duration"].str.extract('(\d+)').astype(float) # ? How about 1 season


# Create date picker
col1, col2 = st.columns((2))
startDate = pd.to_datetime(df['date_added']).min()
endDate = pd.to_datetime(df['date_added']).max()

with col1:
    date1 = pd.to_datetime(st.date_input("Start Date", startDate))
with col2:
    date2 = pd.to_datetime(st.date_input("End Date", endDate))

df = df[(df['date_added'] >= date1) & (df['date_added'] <= date2)].copy()

# Create side bar
st.sidebar.header("Choose your filter: ")

# Create for content type
type = st.sidebar.multiselect("Pick your content type: ", df.type.unique())
if not type:
    df2 = df.copy()
else:
    df2 = df[df.type.isin(type)]
# Create for rating
rating = st.sidebar.multiselect("Pick your rating: ", df2.rating.unique())
if not rating:
    df3 = df2.copy()
else:
    df3 = df2[df2.rating.isin(rating)]
# Create for year
year = st.sidebar.multiselect("Pick release year: ", sorted(df3['release_year'].unique(), reverse=True))

# Create for country
country_content = df.assign(country=df['country'].str.split(',')).explode('country')
country_content['country'] = country_content['country'].str.strip()
country = st.sidebar.multiselect("Pick your country: ", sorted(country_content['country'].unique()))

# Apply filters
if not type and not rating and not year:
    filtered_df = df
elif not rating and not year:
    filtered_df = df[df.type.isin(type)]
elif not type and not year:
    filtered_df = df[df.rating.isin(rating)]
elif type and year:
    filtered_df = df3[df.type.isin(type) & df3['release_year'].isin(year)]
elif rating and year:
    filtered_df = df3[df.rating.isin(rating) & df3['release_year'].isin(year)]
elif type and rating:
    filtered_df = df3[df.type.isin(type) & df3.rating.isin(rating)]
elif year:
    filtered_df = df3[df3['release_year'].isin(year)]
else:
    filtered_df = df3[df3.type.isin(type) & df3.rating.isin(rating) & df3['release_year'].isin(year)]

# 1. Bar chart for Countries 
# Filter the data based on country
if country:
    country_filtered_df = country_content[country_content['country'].isin(country)]
else:
    country_filtered_df = country_content.copy()
# Group by country and sum the durations
country_df = country_filtered_df.groupby(by=["country"], as_index=False)["duration"].sum()

# Select the top 10 countries with the highest total duration
top_10_countries = country_df.nlargest(10, 'duration')
st.subheader("Countries by Duration")
fig1 = px.bar(top_10_countries, x="country", y="duration", text=['${:,.2f}'.format(x) for x in top_10_countries["duration"]],
              color="duration",  
                color_continuous_scale="Reds", 
             template="seaborn")
fig1.update_layout(
    width=1000,  
    height=400,  
    xaxis_title="Country",
    yaxis_title="Total Duration",
    xaxis_tickangle=-45  
)
st.plotly_chart(fig1)

# 2. Filled Map: Number of titles by countries
st.subheader("Number of Movies Added by Country")
country_counts = country_filtered_df.groupby('country')['title'].nunique().reset_index(name='count')

# Create the filled map
fig2 = px.choropleth(
    country_counts,
    locations="country",  
    locationmode="country names",  
    color="count",  
    hover_name="country",  
    color_continuous_scale="Reds"
)
st.plotly_chart(fig2)

# 3. Recommendation based on countries
st.header("Content Recommendations")
selected_country = st.selectbox("Select a country you like watching:", country_filtered_df['country'].unique())

# Filter data for the selected country
country_filtered = filtered_df[filtered_df['country'].str.contains(selected_country, na=False, case=False)]
if not country_filtered.empty:
    # Get the most common genre from the selected country
    common_genre = country_filtered['listed_in'].mode()[0]
    # Recommend movies based on the common genre
    recommendations = filtered_df[filtered_df['listed_in'].str.contains(common_genre, na=False, case=False)].sample(5)
    st.write(f"Recommended titles based on popular genre in {selected_country}:")
    # Columns custom
    # Rename columns
    recommendations = recommendations.rename(columns={
    'title': 'Title',
    'type': 'Type',
    'rating': 'Rating',
    'release_year': 'Release Year'
    })
    # Display a well-formatted table
    st.dataframe(
        recommendations[['Title', 'Type', 'Rating', 'Release Year']], 
        hide_index=True, 
        use_container_width=True
    )
else:
    st.write("No recommendations available for the selected country.")
