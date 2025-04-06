# Movie Trends Dashboard
Developing a Python-Based Interactive Dashboard for Analyzing Movie Trends and Insights

This dashboard is built using **Streamlit** for the front-end interface and **Plotly** for interactive visualizations. It is designed to be accessible to individuals of all backgrounds, offering a fresh, engaging way to uncover film industry patterns and personalize movie experiences


## 📌 Description
The **Movie Trends and Insights Dashboard** is a Python-based interactive web application designed to analyze and visualize movie-related data. The dashboard integrates multiple datasets, including **IMDB Top 1000 Movies** and **Netflix Movies and TV Shows**, offering dynamic insights into box office performance, global content trends, and personalized recommendations. The dashboard also includes user authentication and profile management for a tailored experience.


## 🚀 Features
- **Gross Earnings Explore:**:
  - Analyze total gross earnings over time with interactive line charts.
  - View top 10 directors and actors by gross earnings with bar charts.
  - Explore factors impacting gross earnings (e.g., IMDB ratings, runtime) via scatter plots.
  - Filters: IMDB rating, Meta score, release year, and genre.
- **Global Trends**:
  - Bar charts of total duration by country and content type (Movies vs. TV Shows).
  - Interactive choropleth map for title counts by country with genre breakdowns.
  - Filters: release year, content type, rating category, country, and date added.
- **Movie Checklist & Profile**:
  - Personal movie watchlist with search functionality using the TMDb API.
  - Track watched movies, rate them, and share recommendations with friends.
  - User profile management with avatar uploads and editable details.
  - Notification system for shared movie recommendations.

## 🔎 Installation Instructions

To run the Movie Trends and Insights Dashboard locally, follow these steps:

### Prerequisites
- **Python 3.8 or higher** installed on your system.
- **Git** installed (optional, for cloning the repository).
- An internet connection (for TMDb API calls).

### Step 1: Clone the Repository
1. Open a terminal in VS Code Studio.
2. Run the following command to clone the repository:
   ```bash
    git clone https://github.com/LanDinh15/W25_4495_S2_LanD.git
3. Navigate to the project directory:
   ```bash
   cd W25_4495_S2_LanD/Implementation

### Step 2: Install Required Packages
    pip install streamlit pandas numpy seaborn matplotlib plotly requests streamlit-plotly-events
    
### Step 3: Run the Dashboard
  Start the Streamlit application by running the following command:
    pip streamlit run Welcome.py

## 📋 Usage Notes
- **Authentication**: Register or log in via the sidebar to access the Profile and Movie Checklist features.
- **TMDb API**: The Movie Checklist uses a hardcoded API key (e206cf8b0ba47f28233d0a28ff83c414). For production use, consider securing this key (e.g., via environment variables).
- **Filters**: Adjust sidebar filters to refine visualizations and explore specific trends.

## 📞 Contact
- **Author**: Lan Dinh
- **Email**: landinh.515@gmail.com
- **GitHub**: 


