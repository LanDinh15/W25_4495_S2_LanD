import streamlit as st # type: ignore
import warnings
import pandas as pd # type: ignore

warnings.filterwarnings('ignore')

st.set_page_config(page_title="Movies Trends", layout = "wide")
st.title(":round_pushpin: Interactive Dashboard for Analyzing Movie Trends")
st.markdown(
    """
    <style>
    h1 {
    font-size: 32px !important;
    color: #DD0000 !important;
    }
    </style>
    """, unsafe_allow_html=True)
netflix_image = "https://entrevue.fr/wp-content/uploads/2025/01/netflix-decouvrez-les-nouveautes-de-la-semaine-y-compris-la-tant-attendue-suite-dun-immense-succes-750x410-1.jpg"
st.image(netflix_image, use_column_width="always")
