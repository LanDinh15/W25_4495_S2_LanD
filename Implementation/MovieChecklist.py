import streamlit as st  # type: ignore
import requests  # type: ignore

def show_movie_checklist():
    # TMDb API configuration
    API_KEY = "e206cf8b0ba47f28233d0a28ff83c414"
    BASE_URL = "https://api.themoviedb.org/3"
    IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w200"

    # Styling
    st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        margin-top: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

    def get_popular_movies():
        url = f"{BASE_URL}/movie/popular?api_key={API_KEY}&language=en-US&page=1"
        response = requests.get(url)
        return response.json()['results'] if response.status_code == 200 else []

    def search_movies(query):
        url = f"{BASE_URL}/search/movie?api_key={API_KEY}&query={query}"
        response = requests.get(url)
        return response.json()['results'] if response.status_code == 200 else []

    def get_movie_details(movie_id):
        url = f"{BASE_URL}/movie/{movie_id}?api_key={API_KEY}&language=en-US"
        response = requests.get(url)
        return response.json() if response.status_code == 200 else {}

    def get_keyword_suggestions(query, movies):
        query = query.lower()
        suggestions = set()
        for movie in movies:
            title = movie['title'].lower()
            if query in title and title != query:
                suggestions.add(movie['title'])
            if len(suggestions) >= 3:  # Limit to 3 suggestions
                break
        return list(suggestions)

    # Main logic
    st.title("🎬 Movie Checklist")

    # Initialize session state for checklist
    if 'movie_checklist' not in st.session_state:
        st.session_state.movie_checklist = {}

    # Searching movies
    st.subheader("Search Movies")
    search_query = st.text_input("Enter movie title")
    
    # Initialize suggestions with a default value
    suggestions = []
    search_results = []  # Also initialize search_results to avoid similar issues later
    
    if search_query:
        search_results = search_movies(search_query)
        popular_movies = get_popular_movies()
        suggestions = get_keyword_suggestions(search_query, popular_movies + search_results)

    # Display keyword suggestions
    if suggestions:
        st.write("Did you mean:")
        cols = st.columns(len(suggestions))
        for i, suggestion in enumerate(suggestions):
            with cols[i]:
                if st.button(suggestion, key=f"suggest_{i}"):
                    search_query = suggestion
                    search_results = search_movies(suggestion)
                    st.rerun()

    # Display search results with details
    for movie in search_results[:5]:
        movie_id = movie['id']
        movie_details = get_movie_details(movie_id)
        
        with st.expander(f"{movie['title']} ({movie.get('release_date', 'N/A')[:4]})"):
            col1, col2 = st.columns([1, 3])
            with col1:
                if movie.get('poster_path'):
                    st.image(f"{IMAGE_BASE_URL}{movie.get('poster_path')}", width=150)
            with col2:
                st.write(f"**Release Date:** {movie.get('release_date', 'N/A')}")
                st.write(f"**Rating:** {movie.get('vote_average', 'N/A')}/10")
                st.write(f"**Overview:** {movie.get('overview', 'No description available')}")
                if st.button("Add to Checklist", key=f"add_{movie_id}"):
                    st.session_state.movie_checklist[movie_id] = {
                        'title': movie['title'],
                        'watched': False,
                        'poster': movie.get('poster_path'),
                        'rating': movie.get('vote_average')
                    }

    # Main content
    with st.container():
        st.subheader("My Movie Checklist")

        tab1, tab2 = st.tabs(["To Watch", "Watched"])

        unwatched_movies = {k: v for k, v in st.session_state.movie_checklist.items() if not v['watched']}
        watched_movies = {k: v for k, v in st.session_state.movie_checklist.items() if v['watched']}

        with tab1:
            if unwatched_movies:
                for movie_id, movie_info in unwatched_movies.items():
                    col1, col2, col3 = st.columns([1, 3, 1])
                    with col1:
                        if movie_info.get('poster'):
                            st.image(f"{IMAGE_BASE_URL}{movie_info['poster']}", width=50)
                    with col2:
                        st.write(f"{movie_info['title']} ({movie_info.get('rating', 'N/A')}/10)")
                    with col3:
                        if st.button("Watched", key=f"watch_{movie_id}"):
                            st.session_state.movie_checklist[movie_id]['watched'] = True
                            st.rerun()
            else:
                st.write("No movies in your watchlist yet!")

        with tab2:
            if watched_movies:
                for movie_id, movie_info in watched_movies.items():
                    col1, col2, col3 = st.columns([1, 3, 1])
                    with col1:
                        if movie_info.get('poster'):
                            st.image(f"{IMAGE_BASE_URL}{movie_info['poster']}", width=50)
                    with col2:
                        st.write(f"{movie_info['title']} ({movie_info.get('rating', 'N/A')}/10)")
                    with col3:
                        if st.button("Remove", key=f"remove_{movie_id}"):
                            del st.session_state.movie_checklist[movie_id]
                            st.rerun()
            else:
                st.write("No movies watched yet!")

        # Popular movies section
        st.subheader("Popular Movies")
        popular_movies = get_popular_movies()
        cols = st.columns(3)
        for idx, movie in enumerate(popular_movies[:6]):
            movie_id = movie['id']
            if movie_id not in st.session_state.movie_checklist:
                with cols[idx % 3]:
                    st.markdown(
                        f"""
                        <div style='border: 1px solid #e0e0e0; border-radius: 5px; padding: 10px; margin: 5px; height: 300px; overflow: auto;'>
                            <img src='{IMAGE_BASE_URL}{movie.get('poster_path', '')}' width='100%' style='border-radius: 5px;'>
                            <h4 style='margin: 5px 0;'>{movie['title']}</h4>
                            <p style='font-size: 12px; margin: 2px 0;'>Rating: {movie.get('vote_average', 'N/A')}/10</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    if st.button("Add", key=f"popular_{movie_id}"):
                        st.session_state.movie_checklist[movie_id] = {
                            'title': movie['title'],
                            'watched': False,
                            'poster': movie.get('poster_path'),
                            'rating': movie.get('vote_average')
                        }