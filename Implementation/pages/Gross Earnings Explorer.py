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
st.title(":round_pushpin: IMDB Gross Earnings Explorer")
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
df = df.rename(columns={'Runtime':'Runtime (min)','Gross':'Gross (M)'}) 

# Split for genres
df['Genre'] = df['Genre'].astype(str)
genre_content = df.assign(genre=df['Genre'].str.split(',')).explode('genre')
genre_content['genre'] = genre_content['genre'].str.strip()


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
# Slider for Released year
year_min, year_max = df['Released_Year'].min(), df['Released_Year'].max()
year_range = st.sidebar.slider(
    "Select Released Year Range:",
    min_value=int(year_min),
    max_value=int(year_max),
    value=(int(year_min), int(year_max)),
    step = 1,
    format = "%d",
)  
# Selection for Genres
genre = st.sidebar.multiselect("Pick genre: ", sorted(genre_content['genre'].unique(),reverse=False))

# Filter the dataset based on selected ranges
filtered_df = df[
    (df['IMDB_Rating'] >= imdb_range[0]) &
    (df['IMDB_Rating'] <= imdb_range[1]) &
    (df['Meta_score'] >= meta_range[0]) &
    (df['Meta_score'] <= meta_range[1]) &
    (df['Released_Year'] >= year_range[0]) &
    (df['Released_Year'] <= year_range[1])
]
if genre:
    filtered_df = filtered_df[filtered_df['Genre'].apply(lambda x: any(g in x for g in genre))]

st.markdown(
    """
    <style>
    .header-box {
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 20px;
    }
    </style>
    <div class="header-box">
    """, unsafe_allow_html=True)
st.subheader("Dataset Snapshot")
c1, c2, c3, c4 = st.columns([1,2,1,1])
with c1:
    st.metric("Total Movies", len(filtered_df))
with c2:
    st.metric("Total Gross (M)", f"${filtered_df['Gross (M)'].sum() * 1e6:,.0f}")
with c3:
    st.metric("Avg IMDb Rating", f"{filtered_df['IMDB_Rating'].mean():.1f}")
with c4:
    st.metric("Avg Meta Score", f"{filtered_df['Meta_score'].mean():.1f}")
st.markdown("</div>", unsafe_allow_html=True)

# Main content
tab1, tab2, tab3 = st.tabs(["Gross Trends", "Directors & Actors", "Gross Impacter"])
with tab1:
    # 1. Gross Earnings Over Time
    st.subheader("Total Gross Earnings (M) Over Time: Peak Performers")
    gross_trends = filtered_df.groupby('Released_Year')['Gross (M)'].sum().reset_index()
    fig1 = px.line(gross_trends, 
                x='Released_Year', 
                y='Gross (M)',
                labels={'Released_Year':'Year','Gross (M)': 'Total Gross Earnings (M)'},
    )
    highest_gross = filtered_df.loc[filtered_df.groupby('Released_Year')['Gross (M)'].idxmax()]
    fig1.add_scatter(x=highest_gross['Released_Year'], 
                    y=highest_gross['Gross (M)'],
                    mode='markers', 
                    hoverinfo='text', 
                    text=[f"{title} ({year}) - ${gross:.1f}M" for title, year, gross in zip(highest_gross['Series_Title'], highest_gross['Released_Year'], highest_gross['Gross (M)'])],  # Include title, year, and gross                 
                    marker=dict(opacity=0),  # Invisible points
                    showlegend=False)
    fig1.update_layout(
                    xaxis_title='Released Year',
                    yaxis_title='Total Gross Earnings (M)',
                    template='plotly_white',
                    hovermode='x unified',
    )
    st.plotly_chart(fig1, use_container_width=True)

with tab2:
    col1, col2 = st.columns([1,1])
    with col1:
        # 2. Top 10 Directors by Gross (M)
        directors = filtered_df.groupby('Director').agg({'Gross (M)': 'sum', 'IMDB_Rating': 'mean', 'Series_Title': 'count'}).reset_index()
        directors_sorted = directors.sort_values(by='Gross (M)', ascending=False)
        top_10_directors = directors_sorted.head(10)
        # Create an interactive bar chart
        st.subheader("Directors of Blockbusters: Top 10 by Gross (M)")
        fig2 = px.bar(
            top_10_directors,
            x='Director',
            y='Gross (M)',
            text=[f"${gross:.2f}M" for gross in top_10_directors['Gross (M)']],
            hover_data={'IMDB_Rating': ':.1f', 'Series_Title': True},  
            labels={'Gross(M)': 'Total Gross Earnings (M)', 'Director': 'Director','Series_Title':'Movie Count','IMDB_Rating':'Avg IMDb'},
            color='Gross (M)', 
            color_continuous_scale='Viridis'  
        )
        # Customize the layout
        fig2.update_layout(
            xaxis_title='Director',
            yaxis_title='Total Gross Earnings (M)',
            xaxis_tickangle=-45,  # Rotate director names for better readability
            template='plotly_white',  # Use a clean template
            showlegend=False
        )
        # Display the plot
        st.plotly_chart(fig2, use_container_width=True)
        # Show metrics
        c1, c2 = st.columns(2)
        with c1:
            st.header("Mean")
            st.metric(label="Mean", value=round(top_10_directors['Gross (M)'].mean(), 1))
        with c2:
            st.header("Median")
            st.metric(label="Median", 
                    value=round(top_10_directors['Gross (M)'].median(), 1),
                    delta=round(top_10_directors['Gross (M)'].mean() - top_10_directors['Gross (M)'].median(), 1))
    with col2:
        # 3. Top 10 Actors by Gross (M)
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
        st.subheader("Stars of the Box Office: Top 10 by Gross (M)")
        fig3 = px.bar(
            top_10_actors,
            x='Actor',
            y='Gross (M)',
            text=[f"${gross:.2f}M" for gross in top_10_actors['Gross (M)']],
            labels={'Gross (M)': 'Total Gross Earnings (M)', 'Actor': 'Actor'},
            color='Gross (M)',  
            color_continuous_scale='Viridis'  
        )

        # Customize the layout
        fig3.update_layout(
            xaxis_title='Actor',
            yaxis_title='Total Gross Earnings (M)',
            xaxis_tickangle=-45,  
            template='plotly_white',  
            showlegend=False  
        )

        # Display the interactive plot in Streamlit
        st.plotly_chart(fig3, use_container_width=True)

        # Show metrics
        c1, c2 = st.columns(2)
        with c1:
            st.header("Mean")
            st.metric(label="Mean", value=round(top_10_actors['Gross (M)'].mean(), 1))
        with c2:
            st.header("Median")
            st.metric(label="Median", 
                    value=round(top_10_actors['Gross (M)'].median(), 1),
                    delta=round(top_10_actors['Gross (M)'].mean() - top_10_actors['Gross (M)'].median(), 1))

with tab3:
    # 4. Gross Impact Explorer
    st.subheader("Gross Impact Explorer")
    allowed_columns = [
        'IMDB_Rating', 
        'Meta_score', 
        'Runtime (min)', 
        'Released_Year'
    ]
    cols = [col for col in allowed_columns 
                            if pd.api.types.is_numeric_dtype(df[col])]
    chosen_col = st.selectbox(label="Please select a column", options=cols)
    # Plot
    fig4 = px.scatter(df,x=chosen_col,y="Gross (M)",
                    color="Gross (M)",
                    log_x=True)
    st.plotly_chart(fig4,use_container_width=True)
    # 4. Interactive Scatter in an Expander
    with st.expander("Explore Gross vs. Other Metrics"):
        chosen_col = st.selectbox("Select a column to compare with Gross (M):", options=cols)
        fig4 = px.scatter(filtered_df, x=chosen_col, y='Gross (M)', color='Gross (M)', log_x=True, 
                        hover_data=['Series_Title', chosen_col], template='plotly_white')
        st.plotly_chart(fig4, use_container_width=True)