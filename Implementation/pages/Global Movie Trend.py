import streamlit as st # type: ignore
import pandas as pd # type: ignore
import numpy as np # type: ignore
import seaborn as sns # type: ignore
import matplotlib.pyplot as plt # type: ignore
import plotly.express as px # type: ignore
from datetime import datetime
from streamlit_plotly_events import plotly_events # type: ignore

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
    color: #C00000 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)
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
set_background_image("https://thumbs.dreamstime.com/b/global-connecting-10498106.jpg")

# Load the data
df = pd.read_csv("netflix_titles.csv", decimal=',')

# Filling null values
df = df.dropna(subset=["date_added", "duration"])
df['rating'] = df['rating'].fillna(df['rating'].mode()[0])
df['duration'] = df['duration'].fillna(df['duration'].mode()[0])
df['country'] = df['country'].fillna(df['country'].mode()[0])
df['cast'] = df['cast'].fillna('Unknown')
df['director'] = df['director'].fillna('Unknown')

# Change the date_added column into datetime datatype
df['date_added'] = df['date_added'].str.strip()
df['date_added'] = pd.to_datetime(df['date_added'], format='%B %d, %Y', errors='coerce')

# Clean and preprocess duration (before filtering)
df['duration_value'] = df['duration'].str.extract('(\d+)').astype(float)
df['duration_unit'] = df['duration'].str.extract('([a-zA-Z]+)')
def convert_to_minutes(row):
    if pd.isna(row['duration_value']) or pd.isna(row['duration_unit']):
        return np.nan
    unit = row['duration_unit'].strip().lower()
    if unit == 'min':
        return row['duration_value']
    elif unit in ['season', 'seasons']:
        return row['duration_value'] * 10 * 60
    else:
        return np.nan
df['duration_minutes'] = df.apply(convert_to_minutes, axis=1)
df['duration_hours'] = df['duration_minutes'] / 60
df = df.drop(columns=['duration_value', 'duration_unit', 'duration'])  # Drop temporary columns

# Create date picker
st.subheader("Pick the date movie added")
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
# Slider for Released year
year_min, year_max = df['release_year'].min(), df['release_year'].max()
year_range = st.sidebar.slider(
    "Select Released Year Range:",
    min_value=int(year_min),
    max_value=int(year_max),
    value=(int(year_min), int(year_max)),
    step = 1,
    format = "%d",
)  
type = st.sidebar.multiselect("Pick your content type: ", df.type.unique())
#rating = st.sidebar.multiselect("Pick your rating: ", df.rating.unique())

# Apply filters
filtered_df = df.copy()
if type: filtered_df = filtered_df[filtered_df.type.isin(type)]
#if rating: filtered_df = filtered_df[filtered_df.rating.isin(rating)]
filtered_df = df[
    (df['release_year'] >= year_range[0]) &
    (df['release_year'] <= year_range[1])
]

# Create country_content from filtered_df
country_content = filtered_df.assign(country=filtered_df['country'].str.split(',')).explode('country')
country_content['country'] = country_content['country'].str.strip()
country = st.sidebar.multiselect("Pick your country: ", sorted(country_content['country'].unique()))
if country:
    country_filtered_df = country_content[country_content['country'].isin(country)]
else:
    country_filtered_df = country_content.copy()

# Main content
tab1, tab2, tab3 = st.tabs(["Durations", "Numbers of Titles", "Recommendations"])
with tab1:
    # 1. Bar chart for Countries
    type_duration_df = country_filtered_df.groupby(['country', 'type'])['duration_hours'].sum().reset_index()
    top_10_countries = type_duration_df.groupby('country')['duration_hours'].sum().nlargest(10).index
    type_duration_df = type_duration_df[type_duration_df['country'].isin(top_10_countries)]
    movie_counts = country_filtered_df[country_filtered_df['country'].isin(top_10_countries)].groupby('country').size().reindex(top_10_countries).values
    st.subheader("Countries by Duration (hours)")
    fig1 = px.bar(type_duration_df, x="country", y="duration_hours",
                  text=['{:,.2f}'.format(x) for x in type_duration_df["duration_hours"]],
                  color="type",
                  color_discrete_sequence=["#404040", "#C00000"],
                  barmode='stack')
    fig1.update_layout(
        xaxis_title="Country",
        yaxis_title="Total Duration (hours)",
        xaxis_tickangle=-45,
        legend_title="Content Type",
        autosize=True,
        margin=dict(l=50, r=50, t=50, b=100)
    )
    fig1.update_traces(
        textposition='outside',
        textfont=dict(color='white', size=12),
        insidetextanchor='middle',
        hovertemplate="<b>Country:</b> %{x}<br>"
                      "<b>Type:</b> %{customdata[0]}<br>"
                      "<b>Duration:</b> %{y:.2f} hours<br>"
                      "<b>Total Movie Count:</b> %{customdata[1]}<br>",
        customdata=list(zip(type_duration_df['type'], [movie_counts[i // 2] if i % 2 == 0 else movie_counts[i // 2] for i in range(len(type_duration_df))]))
    )
    st.plotly_chart(fig1)


with tab2:
    st.subheader("Number of Titles Added by Country")
    country_counts = country_filtered_df.groupby('country')['title'].nunique().reset_index(name='count')
    fig2 = px.choropleth(
        country_counts,
        locations="country",
        locationmode="country names",
        color="count",
        hover_name="country",
        color_continuous_scale="Reds"
    )
    fig2.update_layout(
        coloraxis_colorbar_title="Title Counts",
        autosize=True
    )
    selected_points = plotly_events(fig2, click_event=True)
    if selected_points:
        print("Selected Points:", selected_points)
        point_index = selected_points[0].get('pointIndex', 0)
        clicked_country = country_counts.iloc[point_index]['country'] if 0 <= point_index < len(country_counts) else None
        if clicked_country:
            country_filtered_df = country_content[country_content['country'] == clicked_country]
            country_df = country_filtered_df.groupby('country')['duration_minutes'].sum().reset_index()
            country_df['duration_hours'] = country_df['duration_minutes'] / 60
            fig1 = px.bar(country_df, x="country", y="duration_hours",
                          text=['{:,.2f}'.format(x) for x in country_df["duration_hours"]],
                          color="duration_hours", color_continuous_scale="Reds")
            fig1.update_traces(textposition='outside', textfont=dict(color='white'))
            fig1.update_layout(
                title=f"Duration for {clicked_country}",
                xaxis_title="Country",
                yaxis_title="Total Duration (hours)",
                xaxis_tickangle=-45,
                coloraxis_colorbar_title="Duration (hours)",
                autosize=True,
                margin=dict(l=50, r=50, t=50, b=100)
            )
            st.plotly_chart(fig1)

with tab3:
    st.header("Content Recommendations")
    selected_country = st.selectbox("Select a country you like watching:", country_filtered_df['country'].unique())
    country_filtered = filtered_df[filtered_df['country'].str.contains(selected_country, na=False, case=False)]
    if not country_filtered.empty:
        common_genre = country_filtered['listed_in'].mode()[0]
        recommendations = filtered_df[filtered_df['listed_in'].str.contains(common_genre, na=False, case=False)].sample(5)
        st.write(f"Recommended titles based on popular genre in {selected_country}:")
        recommendations = recommendations.rename(columns={
            'title': 'Title',
            'type': 'Type',
            'rating': 'Rating',
            'release_year': 'Release Year'
        })
        st.dataframe(
            recommendations[['Title', 'Type', 'Rating', 'Release Year']],
            hide_index=True,
            use_container_width=True
        )
    else:
        st.write("No recommendations available for the selected country.")