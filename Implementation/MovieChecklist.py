import streamlit as st #type:ignore
import requests #type:ignore
from auth import load_credentials, update_user_profile
from datetime import datetime

def show_movie_checklist():
    # TMDb API configuration
    API_KEY = "e206cf8b0ba47f28233d0a28ff83c414"
    BASE_URL = "https://api.themoviedb.org/3"
    IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w200"

    # Custom CSS for styling notifications and buttons
    st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        margin-top: 5px;
    }
    h1 {
        font-size: 40px !important;
        color: #FF2400 !important;
    }
    .notification-unread {
        font-weight: bold;
        color: #FF2400;
    }
    .notification-read {
        color: #888888;
    }
    .notification-container {
        max-height: 300px;
        overflow-y: auto;
        padding: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

    def get_popular_movies(page=1):
        url = f"{BASE_URL}/movie/popular?api_key={API_KEY}&language=en-US&page={page}"
        response = requests.get(url)
        return response.json()['results'] if response.status_code == 200 else []

    def search_movies(query, page=1):
        url = f"{BASE_URL}/search/movie?api_key={API_KEY}&query={query}&page={page}"
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
            if len(suggestions) >= 3:
                break
        return list(suggestions)

    # Main logic
    col1, col2 = st.columns([9, 1])  
    with col1:
        st.title("🎬 My Movielist")
    with col2:
        creds = load_credentials()
        current_user = st.session_state.username
        notifications = creds[current_user].get("notifications", [])
        unread_count = sum(1 for notif in notifications if not notif["read"])
        with st.popover(f"🔔 ({unread_count})", help="View your notifications"):
            if notifications:
                for i, notif in enumerate(notifications):
                    style_class = "notification-unread" if not notif["read"] else "notification-read"
                    st.markdown(f"<p class='{style_class}'>{notif['message']}</p>", unsafe_allow_html=True)
                if st.button("Mark All as Read", key="mark_all_read"):
                    for i in range(len(notifications)):
                        notifications[i]["read"] = True
                    update_user_profile(current_user, notifications=notifications)
                    st.rerun()
                if st.button("Clear All Notifications", key="clear_all_notifications"):
                    notifications.clear()
                    update_user_profile(current_user, notifications=notifications)
                    st.rerun()
            else:
                st.write("No notifications yet!")

    if "logged_in" not in st.session_state or not st.session_state.logged_in:
        st.error("Please log in to access your movie checklist.")
        return

    # Load user data
    if 'movie_checklist' not in st.session_state:
        st.session_state.movie_checklist = creds[current_user].get("movie_checklist", {})
    if 'popular_movies' not in st.session_state:
        st.session_state.popular_movies = get_popular_movies(page=1)
    if 'popular_page' not in st.session_state:
        st.session_state.popular_page = 1
    if 'notifications_shown' not in st.session_state:
        st.session_state.notifications_shown = False

    # Sync session state with file on each load
    st.session_state.movie_checklist = creds[current_user].get("movie_checklist", {})

    # Tabs
    tab1, tab2, tab3 = st.tabs(["Discover Movies", "To Watchlist", "History"])

    # Discover Movies Tab
    with tab1:
        st.subheader("Search Movies")
        search_query = st.text_input("Enter movie title", key="search_input")
        
        suggestions = []
        search_results = []  
        if search_query:
            if "search_page" not in st.session_state:
                st.session_state.search_page = 1
            search_results = search_movies(search_query, page=st.session_state.search_page)
            popular_movies = get_popular_movies()
            suggestions = get_keyword_suggestions(search_query, popular_movies + search_results)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Previous", disabled=st.session_state.search_page == 1, key="prev_search"):
                    st.session_state.search_page -= 1
                    st.rerun()
            with col2:
                if st.button("Next", key="next_search"):
                    st.session_state.search_page += 1
                    st.rerun()

        if suggestions:
            st.write("Did you mean:")
            cols = st.columns(len(suggestions))
            for i, suggestion in enumerate(suggestions):
                with cols[i]:
                    if st.button(suggestion, key=f"suggest_{i}"):
                        search_query = suggestion
                        st.session_state.search_page = 1
                        search_results = search_movies(suggestion, page=st.session_state.search_page)
                        st.rerun()

        for movie in search_results:
            movie_id = str(movie['id'])  
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
                    if st.button("Add to Movielist", key=f"add_{movie_id}"):
                        st.session_state.movie_checklist[movie_id] = {
                            'title': movie['title'],
                            'watched': False,
                            'poster': movie.get('poster_path'),
                            'rating': movie.get('vote_average'),
                            'watched_date': None,
                            'user_rating': None
                        }
                        update_user_profile(st.session_state.username, movie_checklist=st.session_state.movie_checklist)
                        st.rerun()

        st.subheader("Popular Movies")
        available_popular_movies = [movie for movie in st.session_state.popular_movies 
                                   if str(movie['id']) not in st.session_state.movie_checklist]
        
        DISPLAY_COUNT = 33
        while len(available_popular_movies) < DISPLAY_COUNT:
            st.session_state.popular_page += 1
            new_movies = get_popular_movies(page=st.session_state.popular_page)
            if not new_movies:
                break
            st.session_state.popular_movies.extend(new_movies)
            available_popular_movies = [movie for movie in st.session_state.popular_movies 
                                       if str(movie['id']) not in st.session_state.movie_checklist]

        seen_ids = set()
        unique_popular_movies = []
        for movie in available_popular_movies:
            movie_id = str(movie['id'])
            if movie_id not in seen_ids:
                seen_ids.add(movie_id)
                unique_popular_movies.append(movie)

        cols = st.columns(3)
        for idx, movie in enumerate(unique_popular_movies[:DISPLAY_COUNT]):
            movie_id = str(movie['id'])
            with cols[idx % 3]:
                st.markdown(
                    f"""
                    <div style='border: 1px solid #e0e0e0; border-radius: 5px; padding: 10px; margin: 5px; height: auto; overflow: auto;'>
                        <img src='{IMAGE_BASE_URL}{movie.get('poster_path', '')}' width='100%' style='border-radius: 5px;'>
                        <h4 style='margin: 5px 0;'>{movie['title']}</h4>
                        <p style='font-size: 14px; margin: 2px 0;'>Rating: {movie.get('vote_average', 'N/A')}/10</p>
                        <p style='font-size: 14px; margin: 2px 0; margin-top: 4px;'>Overview: {movie.get('overview', 'N/A')}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                if st.button("Add to Movielist", key=f"popular_{movie_id}_{idx}"):
                    st.session_state.movie_checklist[movie_id] = {
                        'title': movie['title'],
                        'watched': False,
                        'poster': movie.get('poster_path'),
                        'rating': movie.get('vote_average'),
                        'watched_date': None,
                        'user_rating': None
                    }
                    update_user_profile(st.session_state.username, movie_checklist=st.session_state.movie_checklist)
                    st.rerun()

    # To Watchlist Tab
    with tab2:
        unwatched_movies = {k: v for k, v in st.session_state.movie_checklist.items() if not v['watched']}
        if unwatched_movies:
            for movie_id, movie_info in unwatched_movies.items():
                col1, col2, col3, col4, col5 = st.columns([1, 4, 1, 1, 2])
                with col1:
                    if movie_info.get('poster'):
                        st.image(f"{IMAGE_BASE_URL}{movie_info['poster']}", width=50)
                with col2:
                    st.write(f"{movie_info['title']} ({movie_info.get('rating', 'N/A')}/10)")
                with col3:
                    if st.button("✔️", key=f"watch_{movie_id}", help="Add to history"):
                        st.session_state.movie_checklist[movie_id]['watched'] = True
                        st.session_state.movie_checklist[movie_id]['watched_date'] = datetime.now().strftime("%b %d, %Y")
                        update_user_profile(st.session_state.username, movie_checklist=st.session_state.movie_checklist)
                        st.rerun()
                with col4:
                    if st.button("✖️", key=f"remove_{movie_id}", help="Remove from list"):
                        del st.session_state.movie_checklist[movie_id]
                        update_user_profile(st.session_state.username, movie_checklist=st.session_state.movie_checklist)
                        st.rerun()
                with col5:
                    share_toggle_key = f"show_share_unwatch_{movie_id}"
                    if share_toggle_key not in st.session_state:
                        st.session_state[share_toggle_key] = False
                    if st.button("👥", key=f"share_unwatch_{movie_id}", help="Share with your friends"):
                        st.session_state[share_toggle_key] = not st.session_state[share_toggle_key]
                    if st.session_state[share_toggle_key]:
                        friends = [u for u in creds.keys() if u != current_user]
                        friend = st.selectbox(f"Share '{movie_info['title']}' with:", friends, key=f"friend_select_unwatch_{movie_id}")
                        custom_message = st.chat_input("Send a message", key=f"chat_unwatch_{movie_id}")
                        if custom_message:
                            friend_notifications = creds.get(friend, {}).get("notifications", [])
                            message_to_send = f"{current_user} shared '{movie_info['title']}' with you: {custom_message}"
                            friend_notifications.append({"message": message_to_send, "read": False})
                            update_user_profile(friend, notifications=friend_notifications)
                            st.success(f"Shared '{movie_info['title']}' with {friend}!")
                            st.session_state[share_toggle_key] = False
                            st.rerun()
    # History Tab
    with tab3:
        watched_movies = {k: v for k, v in st.session_state.movie_checklist.items() if v['watched']}
        emoji_ratings = {9: "😆", 8: "🥰", 7: "😭", 6: "🥱", 5: "🤯", 4: "😱", 3: "😵‍💫", 2: "😡", 1: "🤢"}
        if watched_movies:
            for movie_id, movie_info in watched_movies.items():
                rating_popover_key = f"rating_popover_{movie_id}"
                if rating_popover_key not in st.session_state:
                    st.session_state[rating_popover_key] = False

                col1, col2, col3, col4, col5, col6 = st.columns([1, 1, 3, 0.5, 1, 2])  
                with col1:
                    st.write(f"Watched: {movie_info.get('watched_date', 'N/A')}")
                with col2:
                    if movie_info.get('poster'):
                        st.image(f"{IMAGE_BASE_URL}{movie_info['poster']}", width=50)
                with col3:
                    st.write(f"{movie_info['title']}")
                    user_rating = movie_info.get('user_rating', None)
                    if user_rating is not None:
                        st.pills("Your Vibe:", [emoji_ratings[user_rating]], key=f"display_rating_{movie_id}")
                    else:
                        st.write("Your Vibe: Not rated")              
                with col4:
                    if st.button("✖️", key=f"remove_{movie_id}", help="Remove from list"):
                        del st.session_state.movie_checklist[movie_id]
                        update_user_profile(st.session_state.username, movie_checklist=st.session_state.movie_checklist)
                        st.rerun()
                with col6:
                    share_toggle_key = f"show_share_watch_{movie_id}"
                    if share_toggle_key not in st.session_state:
                        st.session_state[share_toggle_key] = False
                    if st.button("👥", key=f"share_unwatch_{movie_id}", help="Share with friends"):
                        st.session_state[share_toggle_key] = not st.session_state[share_toggle_key]
                    if st.session_state[share_toggle_key]:
                        friends = [u for u in creds.keys() if u != current_user]
                        friend = st.selectbox(f"Share '{movie_info['title']}' with:", friends, key=f"friend_select_watch_{movie_id}")
                        custom_message = st.chat_input("Send a message", key=f"chat_unwatch_{movie_id}")
                        if custom_message:
                            friend_notifications = creds.get(friend, {}).get("notifications", [])
                            message_to_send = f"{current_user} shared '{movie_info['title']}' with you: {custom_message}"
                            friend_notifications.append({"message": message_to_send, "read": False})
                            update_user_profile(friend, notifications=friend_notifications)
                            st.success(f"Shared '{movie_info['title']}' with {friend}!")
                            st.session_state[share_toggle_key] = False
                            st.rerun()
                with col5:
                    with st.popover("⭐ Rate"):
                        rating_options = list(emoji_ratings.values())[::-1]  
                        rating_key = f"selected_rating_{movie_id}"
                        if rating_key not in st.session_state:
                            st.session_state[rating_key] = emoji_ratings.get(user_rating, None)
                        selected_emoji = st.pills("Select rating:", rating_options, key=f"pill_select_{movie_id}")
                        if selected_emoji:
                            st.session_state[rating_key] = selected_emoji
                            new_rating = [k for k, v in emoji_ratings.items() if v == selected_emoji][0]
                            if st.button("Submit", key=f"submit_rating_{movie_id}"):
                                st.session_state.movie_checklist[movie_id]['user_rating'] = new_rating
                                update_user_profile(st.session_state.username, movie_checklist=st.session_state.movie_checklist)
                                st.session_state[rating_popover_key] = False
                                st.success(f"Rated '{movie_info['title']}' as {selected_emoji}!")
                                st.rerun()
        else:
            st.write("No movies watched yet!")
