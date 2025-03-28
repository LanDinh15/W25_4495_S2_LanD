import streamlit as st  # type: ignore
import pandas as pd  # type: ignore
import numpy as np  # type: ignore
import seaborn as sns  # type: ignore
import matplotlib.pyplot as plt  # type: ignore
import plotly.express as px  # type: ignore
from datetime import datetime, date
import os
from GrossEarnings import show_gross_earnings
from GlobalTrend import show_global_trends 
from MovieChecklist import show_movie_checklist
from auth import load_credentials, check_login, register_user, update_user_profile

import warnings

warnings.filterwarnings('ignore')

st.set_page_config(page_title="Movie Trends Dashboard", layout='wide')

# Create avatars directory if it doesn't exist
AVATARS_DIR = "avatars"
if not os.path.exists(AVATARS_DIR):
    os.makedirs(AVATARS_DIR)

# CSS for consistent sidebar title color
st.markdown(
    """
    <style>
    .sidebar .sidebar-content .css-1d391kg {
        color: #FF2400 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Define Welcome Function
def welcome():
    st.title(":clapper: Welcome to the Movie Trends Dashboard")
    st.markdown(
        """
        <style>
        h1 {
            font-size: 40px !important;
            color: #FF2400 !important;
        }
        </style>
        """, unsafe_allow_html=True)

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

    st.write(f"Today's Date: {datetime.now().strftime('%B %d, %Y')}")
    st.markdown("""
    Welcome to the **Movie Trends Dashboard**!  
    Dive into the world of movies—track trending films, analyze box office data, explore genre popularity, and more.  
    Use the sidebar to log in or register and explore key insights into the film industry.

    :star: **Key Features:**
    - Top trending movies
    - Genre & rating breakdown
    - Explore Global Trend
    - Gross Earnings Explorer

    Enjoy exploring and let the data tell the story! 🍿
    """)
    st.info("👉 Use the sidebar to get started!")

# Define Profile Function
def show_profile():
    st.title(":dart: My Profile")
    st.markdown(
        """
        <style>
        h1 {
            font-size: 40px !important;
            color: #FF2400 !important;
        }
        .stForm {
            color: #FF2400 !important;
        }
        img {
            border-radius: 10px;
        }
        button[kind="secondaryFormSubmit"][data-testid="baseButton-secondaryFormSubmit"] {
                    width: 100%;
                    text-align: center;
                }
        </style>
        """, unsafe_allow_html=True
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

    if "logged_in" not in st.session_state or not st.session_state.logged_in:
        st.error("Please log in to view or edit your profile.")
        return

    creds = load_credentials()
    user_info = creds[st.session_state.username]

    if "show_checklist" not in st.session_state:
        st.session_state.show_checklist = False
    if "show_update" not in st.session_state:
        st.session_state.show_update = False

    st.subheader("Profile Details")
    col1, col2, col3 = st.columns([1, 2, 1])  
    with col1:
        if user_info.get("avatar_path") and os.path.exists(user_info["avatar_path"]):
            st.image(user_info["avatar_path"], caption="Your Avatar", width=200)  
        else:
            st.write("**Avatar:** No avatar uploaded yet.")
    with col2:
        st.write(f"**Username:** {st.session_state.username}")
        st.write(f"**Full Name:** {user_info['full_name']}")
        dob = user_info.get('dob', 'Not set')
        st.write(f"**Date of Birth:** {dob}")
        st.write(f"**Email:** {user_info['email']}")
    with col3:
        update_button = st.button(label="Update My Profile", type="primary")
        if update_button:
            st.session_state.show_update = not st.session_state.show_update
    
    if st.session_state.show_update:
        st.subheader("Update Profile")
        with st.form(key="profile_form"):
            new_full_name = st.text_input("Full Name", value=user_info["full_name"])
            default_dob = date.fromisoformat(user_info["dob"]) if user_info.get("dob") and user_info["dob"] != "None" else date.today()
            new_dob = st.date_input("Date of Birth", value=default_dob, min_value=date(1900, 1, 1), max_value=date.today())
            new_email = st.text_input("Email", value=user_info["email"])
            new_password = st.text_input("New Password", type="password", value="")
            confirm_password = st.text_input("Confirm New Password", type="password", value="")
            avatar_file = st.file_uploader("Upload Avatar (PNG/JPG)", type=["png", "jpg", "jpeg"])
            col_left, col_center, col_right = st.columns([3, 1, 1])
            with col_left:
                st.write("") 
            with col_center:
                submit_button = st.form_submit_button(label="Save Changes")
            with col_right:
                close_button = st.form_submit_button(label="Close")
            if submit_button:
                if new_password and new_password != confirm_password:
                    st.error("New passwords do not match!")
                else:
                    new_avatar_path = user_info.get("avatar_path", None)
                    if avatar_file is not None:
                        new_avatar_path = os.path.join(AVATARS_DIR, f"{st.session_state.username}_{avatar_file.name}")
                        with open(new_avatar_path, "wb") as f:
                            f.write(avatar_file.getbuffer())
                    new_dob_str = str(new_dob)
                    if update_user_profile(st.session_state.username, new_full_name, new_dob_str, new_email, new_password, new_avatar_path):
                        st.success("Profile updated successfully!")
                        if new_password: 
                            st.session_state.logged_in = False
                            st.session_state.username = None
                        st.rerun()  
                    else:
                        st.error("Failed to update profile.")
            elif close_button:
                st.session_state.show_update = False
                st.rerun()

# Authentication State
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.movie_checklist = {}

# Sidebar
st.sidebar.title("Movie Trends Dashboard")
if st.session_state.logged_in:
    st.sidebar.markdown(f"**Logged in as:** {st.session_state.username}")
    page = st.sidebar.selectbox("Choose a Dashboard", ["Welcome", "Global Trends", "Gross Earnings", "Profile", "Movie Checklist"])
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.session_state.movie_checklist = {}
        st.rerun()
else:
    page = st.sidebar.selectbox("Choose a Dashboard", ["Welcome", "Gross Earnings"]) 
    st.sidebar.markdown("---")
    with st.sidebar.expander("Authentication", expanded=True):
        auth_option = st.radio("Choose an option", ["Login", "Register"])
        if auth_option == "Login":
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.button("Login"):
                if check_login(username, password):
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    creds = load_credentials()
                    st.session_state.movie_checklist = creds[username]["movie_checklist"]
                    st.success(f"Welcome, {username}!")
                else:
                    st.error("Invalid credentials")
        elif auth_option == "Register":
            new_username = st.text_input("New Username")
            new_password = st.text_input("New Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            full_name = st.text_input("Full Name")
            email = st.text_input("Email")
            if st.button("Register"):
                if new_password == confirm_password:
                    if register_user(new_username, new_password, full_name, email):
                        st.success(f"Registration successful! Please log in as {new_username}.")
                    else:
                        st.error("Username already exists!")
                else:
                    st.error("Passwords do not match!")

# Main Logic
if not st.session_state.logged_in:
    if page in ["Welcome", "Gross Earnings"]: 
        if page == "Welcome":
            welcome()
        elif page == "Gross Earnings":
            show_gross_earnings()
    else:
        st.title("Movie Trends Dashboard")
        st.info("Please log in or register to access this dashboard.")
elif st.session_state.logged_in:
    if page == "Welcome":
        welcome()
    elif page == "Gross Earnings":
        show_gross_earnings()
    elif page == "Global Trends":
        show_global_trends()
    elif page == "Profile":
        show_profile()
    elif page == "Movie Checklist":
        show_movie_checklist()