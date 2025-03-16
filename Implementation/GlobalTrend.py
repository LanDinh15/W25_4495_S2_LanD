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

def show_global_trends():
    # Title and Netflix image
    st.title(":round_pushpin: Explore Global Trends")
    st.markdown(
        """
        <style>
        h1 {
            font-size: 40px !important;
            color: #FF2400 !important;
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
    set_background_image("https://wallpapers.com/images/featured/movie-9pvmdtvz4cb0xl37.jpg")

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
    df = df.drop(columns=['duration_value', 'duration_unit', 'duration'])  

    # Rating mapping
    rating_mapping = {
        'TV-Y': 'Kids',
        'TV-Y7': 'Kids',
        'TV-Y7-FV': 'Kids',
        'TV-G': 'Kids',
        'G': 'Kids',
        'PG': 'Family',
        'TV-PG': 'Family',
        'PG-13': 'Teen',
        'TV-14': 'Teen',
        'R': 'Adult',
        'TV-MA': 'Adult',
        'NC-17': 'Adult',
        'NR': 'Adult',
        'UR': 'Adult'
    }
    df['rating_category'] = df['rating'].map(rating_mapping)


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
    st.sidebar.markdown("---")
    st.sidebar.header("Choose your filter: ")
    # Slider for Released year
    year_min, year_max = df['release_year'].min(), df['release_year'].max()
    year_range = st.sidebar.slider(
        "Select Released Year Range:",
        min_value=int(year_min),
        max_value=int(year_max),
        value=(int(year_min), int(year_max)),
        step=1,
        format="%d",
    )  
    type = st.sidebar.multiselect("Pick your content type: ", df.type.unique())
    rating_categories = sorted(df['rating_category'].unique())
    rating_category = st.sidebar.multiselect("Pick your rating category: ", rating_categories)

    # Apply filters
    filtered_df = df.copy()
    if type: filtered_df = filtered_df[filtered_df.type.isin(type)]
    if rating_category: filtered_df = filtered_df[filtered_df['rating_category'].isin(rating_category)]
    filtered_df = filtered_df[
        (filtered_df['release_year'] >= year_range[0]) &
        (filtered_df['release_year'] <= year_range[1])
    ]

    # Create country_content from filtered_df
    country_content = filtered_df.assign(country=filtered_df['country'].str.split(',')).explode('country')
    country_content['country'] = country_content['country'].str.strip()
    country = st.sidebar.multiselect("Pick your country: ", sorted(country_content['country'].unique()))
    if country:
        filtered_df_2 = country_content[country_content['country'].isin(country)].copy()
    else:
        filtered_df_2 = country_content.copy()

    # Main content
    tab1, tab2, tab3 = st.tabs(["Duration Trends", "Number of Titles", "Recommendations"])
    with tab1:
        # 1. Bar chart for Countries
        type_duration_df = filtered_df_2.groupby(['country', 'type'])['duration_hours'].sum().reset_index()
        top_10_countries = type_duration_df.groupby('country')['duration_hours'].sum().nlargest(10).index
        type_duration_df = type_duration_df[type_duration_df['country'].isin(top_10_countries)]

        # Calculate metrics
        total_duration_top_10 = type_duration_df['duration_hours'].sum()
        titles_in_top_10 = filtered_df_2[filtered_df_2['country'].isin(top_10_countries)]['title'].nunique()
        avg_duration_per_title = total_duration_top_10 / titles_in_top_10 if titles_in_top_10 > 0 else 0
        duration_by_type = type_duration_df.groupby('type')['duration_hours'].sum()
        movies_duration = duration_by_type.get('Movie', 0)
        tvshows_duration = duration_by_type.get('TV Show', 0)
        total_duration = movies_duration + tvshows_duration
        movies_percentage = (movies_duration / total_duration * 100) if total_duration > 0 else 0
        tvshows_percentage = (tvshows_duration / total_duration * 100) if total_duration > 0 else 0
        total_duration_per_country = type_duration_df.groupby('country')['duration_hours'].sum()
        top_country = total_duration_per_country.idxmax()
        top_country_duration = total_duration_per_country.max()
        total_titles_top_10 = titles_in_top_10

        # Custom CSS for styling the metrics
        st.markdown(
            """
            <style>
            .metric-container {
                background-color: #1E1E1E;
                border-radius: 10px;
                padding: 10px;
                margin: 5px;
                text-align: center;
                color: #FFFFFF;
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.3);
            }
            .metric-label {
                font-size: 14px;
                color: #FF2400;
                font-weight: bold;
            }
            .metric-value {
                font-size: 18px;
                font-weight: bold;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

        # Display metrics
        st.subheader("Key Metrics")
        # First row
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(
                f"""
                <div class="metric-container">
                    <div class="metric-label">Total Duration</div>
                    <div class="metric-value">{total_duration_top_10:,.1f} hrs</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with col2:
            st.markdown(
                f"""
                <div class="metric-container">
                    <div class="metric-label">Avg. Duration/Title</div>
                    <div class="metric-value">{avg_duration_per_title:.1f} hrs</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with col3:
            st.markdown(
                f"""
                <div class="metric-container">
                    <div class="metric-label">Total Titles</div>
                    <div class="metric-value">{total_titles_top_10:,}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        # Second row
        col4, col5, col6 = st.columns(3)
        with col4:
            st.markdown(
                f"""
                <div class="metric-container">
                    <div class="metric-label">Movies Share</div>
                    <div class="metric-value">{movies_percentage:.1f}%</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with col5:
            st.markdown(
                f"""
                <div class="metric-container">
                    <div class="metric-label">TV Shows Share</div>
                    <div class="metric-value">{tvshows_percentage:.1f}%</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with col6:
            st.markdown(
                f"""
                <div class="metric-container">
                    <div class="metric-label">Top Country ({top_country})</div>
                    <div class="metric-value">{top_country_duration:,.1f} hrs</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        # Bar chart
        st.subheader("Top Countries by Duration (hours)")
        fig1 = px.bar(type_duration_df, x="country", y="duration_hours",
                    text=['{:,.2f}'.format(x) for x in type_duration_df["duration_hours"]],
                    color="type",
                    color_discrete_sequence=["#404040", "#FF2400"],
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
                        "<b>Duration:</b> %{y:.2f} hours<br>",
            customdata=list(zip(type_duration_df['type']))
        )
        st.plotly_chart(fig1, use_container_width=True)

    with tab2:
        # 2. Filled map
        st.subheader("Global Map of Title Counts by Country")
        country_counts = filtered_df_2.groupby('country')['title'].nunique().reset_index(name='count')
        fig2 = px.choropleth(
            country_counts,
            locations="country",
            locationmode="country names",
            color="count",
            hover_name="country",
            color_continuous_scale="Reds"
        )
        fig2.update_layout(
            autosize=True, 
            margin=dict(l=20, r=20, t=80, b=20),
            coloraxis_colorbar_title="Number of Titles",
            coloraxis_colorbar_title_font=dict(size=14, color="#FF2400", weight='bold'),
            coloraxis_colorbar_tickfont=dict(size=12, color="#FF2400"),
        )
        fig2.update_coloraxes(colorbar=dict(
            len=0.7,  
            yanchor="top",
            y=1.0,
            x=1.0
        ))
        selected_points = plotly_events(fig2, click_event=True)
        if selected_points:
            print("Selected Points:", selected_points)
            point_index = selected_points[0].get('pointIndex', 0)
            clicked_country = country_counts.iloc[point_index]['country'] if 0 <= point_index < len(country_counts) else None
            if clicked_country:
                st.subheader(f"Top Genre Breakdown in {clicked_country}")
                # Filter for the clicked country before splitting and exploding
                country_specific_df = filtered_df_2[filtered_df_2['country'] == clicked_country]
                # Split the genre
                genre_df = country_specific_df.assign(genre=country_specific_df['listed_in'].str.split(',')).explode('genre')
                genre_df['genre'] = genre_df['genre'].str.strip()
                # Group by genre and count unique titles
                genre_counts = genre_df.groupby('genre')['title'].nunique().reset_index(name='count')
                # Calculate percentages
                total_titles = genre_counts['count'].sum()
                genre_counts['percentage'] = (genre_counts['count'] / total_titles * 100).round(2)
                # Select top 5 genres by percentage
                top_n = 10
                top_genres = genre_counts.nlargest(top_n, 'percentage')
                # Combine the rest into "Other"
                other_genres = genre_counts.iloc[top_n:]
                if not other_genres.empty:
                    other_percentage = other_genres['percentage'].sum()
                    top_genres = pd.concat([top_genres, pd.DataFrame({'genre': ['Other'], 'count': [other_genres['count'].sum()], 'percentage': [other_percentage]})], ignore_index=True)
                fig_donut = px.pie(top_genres, values='percentage', names='genre',
                                    hole=0.4, 
                                    color_discrete_sequence=px.colors.sequential.Reds_r)
                fig_donut.update_traces(textinfo='percent+label', 
                                        hovertemplate="<b>Genre:</b> %{label}<br><b>Percentage:</b> %{value:.2f}%")
                fig_donut.update_layout(
                    title=f"Top {top_n} Genres and Other in {clicked_country}",
                    autosize=True,
                    margin=dict(l=50, r=50, t=50, b=100)
                )
                st.plotly_chart(fig_donut, use_container_width=True)
        else:
            st.write("Click a point on the map to see genre breakdown in that country.")

    with tab3:
        # Personalized Recommendations with Genre Choice
        st.header("Personalized Recommendations")
        if not filtered_df_2.empty:
            # Split the genre
            genre_df = filtered_df_2.assign(genre=filtered_df_2['listed_in'].str.split(',')).explode('genre')
            genre_df['genre'] = genre_df['genre'].str.strip()
            available_genres = sorted(genre_df['genre'].unique())
            selected_genre = st.selectbox("Select a genre you prefer:", available_genres)
            recommendations = filtered_df[
                (filtered_df['listed_in'].str.contains(selected_genre, na=False, case=False))
            ]
            if not recommendations.empty:
                recommendations = recommendations.sample(min(5, len(recommendations)))
                selected_countries = ", ".join(country) if country else "all countries"
                st.write(f"Recommended titles for {selected_genre} in {selected_countries}:")
                recommendations = recommendations.rename(columns={
                    'title': 'Title',
                    'type': 'Type',
                    'rating': 'Rating',
                    'release_year': 'Release Year',
                    'listed_in': 'Genre'
                })
                st.dataframe(
                    recommendations[['Title', 'Type', 'Genre', 'Rating', 'Release Year']],
                    hide_index=True,
                    use_container_width=True
                )
                csv = recommendations.to_csv(index=False)
                st.download_button(
                    label="Download Recommendations as CSV",
                    data=csv,
                    file_name="netflix_recommendations.csv",
                    mime="text/csv",
                )
            else:
                st.write(f"No titles found.")
        else:
            st.write("No recommendations available for the selected country.")