import streamlit as st  # type: ignore
import pandas as pd  # type: ignore
import numpy as np  # type: ignore
import seaborn as sns  # type: ignore
import matplotlib.pyplot as plt  # type: ignore
import plotly.express as px  # type: ignore
from datetime import datetime
import json
import os
from GrossEarnings import show_gross_earnings
from GlobalTrend import show_global_trends 

import warnings

warnings.filterwarnings('ignore')

# Set page config as the FIRST Streamlit command
st.set_page_config(page_title="Movie Trends Dashboard", layout='wide')

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

# Authentication Functions
CREDENTIALS_FILE = "users.json"
if not os.path.exists(CREDENTIALS_FILE):
    with open(CREDENTIALS_FILE, "w") as f:
        json.dump({"admin": "123"}, f)

def load_credentials():
    with open(CREDENTIALS_FILE, "r") as f:
        return json.load(f)

def save_credentials(creds):
    with open(CREDENTIALS_FILE, "w") as f:
        json.dump(creds, f)

def check_login(username, password):
    creds = load_credentials()
    return username in creds and creds[username] == password

def register_user(username, password):
    creds = load_credentials()
    if username in creds:
        return False
    creds[username] = password
    save_credentials(creds)
    return True

# Authentication State
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = None

# Sidebar
st.sidebar.title("Movie Trends Dashboard")
if st.session_state.logged_in:
    st.sidebar.markdown(f"**Logged in as:** {st.session_state.username}")
    page = st.sidebar.selectbox("Choose a Dashboard", ["Welcome", "Global Trends", "Gross Earnings"])
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.rerun()
else:
    page = st.sidebar.selectbox("Choose a Dashboard", ["Welcome"]) 
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
                    st.success(f"Welcome, {username}!")
                else:
                    st.error("Invalid credentials")
        elif auth_option == "Register":
            new_username = st.text_input("New Username")
            new_password = st.text_input("New Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            if st.button("Register"):
                if new_password == confirm_password:
                    if register_user(new_username, new_password):
                        st.success(f"Registration successful! Please log in as {new_username}.")
                    else:
                        st.error("Username already exists!")
                else:
                    st.error("Passwords do not match!")

# Main Logic
if page == "Welcome" and not st.session_state.logged_in:
    welcome()
elif st.session_state.logged_in:
    if page == "Welcome":
        welcome()
    elif page == "Gross Earnings":
        show_gross_earnings()
    elif page == "Global Trends":
        show_global_trends()
else:
    st.title("Movie Trends Dashboard")
    st.info("Please log in or register to access the dashboards.")