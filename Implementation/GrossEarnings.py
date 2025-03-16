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

def show_gross_earnings():
    # Title 
    st.title(":popcorn: Gross Earnings Explorer")
    st.markdown(
        """
        <style>
        h1 {
        font-size: 40px !important;
        color: #FF2400 !important;
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
    set_background_image("https://wallpapers.com/images/featured/movie-9pvmdtvz4cb0xl37.jpg")

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
    st.sidebar.markdown("---")
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
    genre = st.sidebar.multiselect("Pick your genre: ", sorted(genre_content['genre'].unique(),reverse=False))

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

        # Check if filtered_df is empty
        if filtered_df.empty:
            st.warning("No data available after applying filters. Please adjust your filter settings.")
        else:
            # Create the line chart
            fig1 = px.line(gross_trends, 
                        x='Released_Year', 
                        y='Gross (M)',
                        labels={'Released_Year': 'Year', 'Gross (M)': 'Total Gross Earnings (M)'},
                        color_discrete_sequence=['#FF2400']
            )
            highest_gross = filtered_df.loc[filtered_df.groupby('Released_Year')['Gross (M)'].idxmax()]

            # Check if highest_gross has data
            if not highest_gross.empty:
                fig1.add_scatter(x=highest_gross['Released_Year'], 
                                y=highest_gross['Gross (M)'],
                                mode='markers', 
                                hoverinfo='none', 
                                marker=dict(opacity=0),  # Visible points
                                customdata=highest_gross[['Series_Title', 'IMDB_Rating', 'Meta_score']].values,
                                showlegend=False)
                fig1.update_layout(
                                xaxis_title='Released Year',
                                yaxis_title='Total Gross Earnings (M)',
                                template='plotly_white',
                                hovermode='x unified',
                                plot_bgcolor='rgba(0,0,0, 0)',
                                paper_bgcolor='rgba(0, 0, 0, 0)',
                                font=dict(color='#FFFFFF'),
                                xaxis=dict(gridcolor='rgba(200, 200, 200, 0.3)'),
                                yaxis=dict(gridcolor='rgba(200, 200, 200, 0.3)'),
                                autosize=True,  
                                margin=dict(l=50, r=50, t=50, b=50)  
                )
                # Capture click events
                selected_points = plotly_events(fig1, click_event=True, hover_event=False, override_width="100%")
                if selected_points:
                    try:
                        click_x = selected_points[0]['x']
                        nearest_year_idx = (highest_gross['Released_Year'] - click_x).abs().idxmin()
                        # Convert index label to positional index
                        if pd.isna(nearest_year_idx):
                            st.session_state.clicked_movie = None
                            st.warning("No valid movie data found for the clicked year.")
                        else:
                            # Convert the index label to a positional index for iloc
                            positional_idx = highest_gross.index.get_loc(nearest_year_idx)
                            movie_data = highest_gross.iloc[positional_idx]
                            st.session_state.clicked_movie = {
                                'title': movie_data['Series_Title'],
                                'gross': movie_data['Gross (M)'],
                                'rating': movie_data['IMDB_Rating'],
                                'meta': movie_data['Meta_score'],
                                'time': movie_data['Runtime (min)'],
                                'genre':movie_data['Genre'],
                                'cert': movie_data['Certificate'],
                                'poster': movie_data['Poster_Link'],
                                'overview': movie_data['Overview']
                            }
                            st.session_state.selected_year = int(highest_gross.loc[nearest_year_idx, 'Released_Year'])  
                    except (IndexError, KeyError, ValueError) as e:
                        st.session_state.clicked_movie = None
                        st.session_state.selected_year = None
                        st.warning(f"Error accessing movie data: {str(e)}")
                else:
                    st.session_state.clicked_movie = None
                    st.session_state.selected_year = None
                # Show details below the chart
                if st.session_state.clicked_movie:
                    st.subheader(f"Highest Gross Earning Movie Details in {st.session_state.selected_year}")
                    st.write(f"Movie: {st.session_state.clicked_movie['title']}")
                    st.write(f"Gross Earings: ${st.session_state.clicked_movie['gross'] * 1e6:,.0f}")
                    st.write(f"Runtime: {st.session_state.clicked_movie['time']} min")
                    st.write(f"Genre: {st.session_state.clicked_movie['genre']}")
                    st.write(f"Certificate: {st.session_state.clicked_movie['cert']}")
                    st.write(f"Rating: {st.session_state.clicked_movie['rating']:.1f}")
                    st.write(f"Meta Score: {st.session_state.clicked_movie['meta']:.1f}")
                    st.write(f"Overview: {st.session_state.clicked_movie['overview']}")
                    st.image(st.session_state.clicked_movie['poster'], caption="Poster", width=300) 
                else:
                    st.write("Click a point on the chart to see details of the highest-grossing movie for that year.")
            else:
                st.warning("No highest-grossing movies available with the current filters.")

    with tab2:
        col1, col2 = st.columns([1,1])
        with col1:
            # 2. Top 10 Directors by Gross (M)
            directors = filtered_df.groupby('Director').agg({'Gross (M)': 'sum', 'Series_Title': 'count'}).reset_index()
            directors_sorted = directors.sort_values(by='Gross (M)', ascending=False)
            top_10_directors = directors_sorted.head(10)
            # Create an interactive bar chart
            st.subheader("Directors of Blockbusters: Top 10 by Gross (M)")
            fig2 = px.bar(
                top_10_directors,
                x='Director',
                y='Gross (M)',
                text=[f"${gross:.2f}M" for gross in top_10_directors['Gross (M)']],
                hover_data={'Series_Title': True},  
                labels={'Gross(M)': 'Total Gross Earnings (M)', 'Director': 'Director','Series_Title':'Movie Count'},
                color='Gross (M)', 
                color_continuous_scale=['#FFF5EB', '#FF9999', '#FF2400'] 
            )
            fig2.update_traces(
                    hovertemplate="<b>Director:</b> %{x}<br>" +
                    "<b>Total Gross:</b> $%{y:.2f}M<br>" +
                    "<b>Movie Count:</b> %{customdata[0]}<br>"
            )
            fig2.update_layout(
                xaxis_title='Director',
                yaxis_title='Gross Earnings (M)',
                xaxis_tickangle=-45,  
                template='plotly_white', 
                showlegend=False
            )
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
                labels={'Gross (M)': 'Gross (M)', 'Actor': 'Actor'},
                color='Gross (M)',  
                color_continuous_scale=['#FFF5EB', '#FF9999', '#FF2400'] 
            )
            fig3.update_traces(
                    hovertemplate="<b>Actor:</b> %{x}<br>" +
                    "<b>Total Gross:</b> $%{y:.2f}M<br>" 
            )
            fig3.update_layout(
                xaxis_title='Actor',
                yaxis_title='Gross Earnings (M)',
                xaxis_tickangle=-45,  
                template='plotly_white',  
                showlegend=False  
            )
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
        fig4 = px.scatter(filtered_df,x=chosen_col,y="Gross (M)",
                        color="Gross (M)",
                        color_continuous_scale=['#FFF5EB', '#FF9999', '#FF2400'],
                        log_x=True)
        st.plotly_chart(fig4,use_container_width=True)
        # 4. Interactive Scatter in an Expander
        with st.expander("Explore Gross vs. Other Metrics"):
            chosen_col = st.selectbox("Select a column to compare with Gross (M):", options=cols)
            fig4 = px.scatter(filtered_df, x=chosen_col, y='Gross (M)', color='Gross (M)', 
                              color_continuous_scale=['#FFF5EB', '#FF9999', '#FF2400'],log_x=True, 
                            hover_data=['Series_Title', chosen_col], template='plotly_white')
            st.plotly_chart(fig4, use_container_width=True)