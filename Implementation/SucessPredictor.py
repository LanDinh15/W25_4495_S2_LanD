import streamlit as st #type: ignore
import pandas as pd #type:ignore
import pickle

def show_success_predictor():
    st.title(":trophy: Success Predictor")
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

    # Load model and encoder
    try:
        with open("success_predictor_model.pkl", "rb") as f: 
            model = pickle.load(f)
        with open("genre_encoder.pkl", "rb") as f:  
            encoder = pickle.load(f)
    except FileNotFoundError:
        st.error("Model files not found in current directory. Please run predictor.py from this folder.")
        return

    # Input form
    st.subheader("Will Your Movie Be a Blockbuster?")
    st.markdown("""
        <div class="intro-box">
        Curious about a movie’s potential? This tool predicts whether your film idea will shine as a <strong>Blockbuster</strong>, fade as a <strong>Bust</strong>, or land as <strong>Average</strong>. 
              
        Just enter the runtime, Meta Score, release year, and genre below, then hit "Predict Success" to see the verdict!
        </div>
    """, unsafe_allow_html=True)
    st.markdown('<p class="footnote">*Blockbuster: Gross > $100M, IMDB ≥ 8 | Bust: Gross < $20M, IMDB < 7 | Average: Everything else</p>', unsafe_allow_html=True)
    st.write("")

    with st.form("prediction_form"):
        col1, col2 = st.columns(2)
        with col1:
            runtime = st.number_input("Runtime (minutes)", min_value=30.0, max_value=300.0, value=90.0, step=1.0)
            meta_score = st.number_input("Meta Score", min_value=0.0, max_value=100.0, value=60.0, step=1.0)
        with col2:
            released_year = st.number_input("Released Year", min_value=1900, max_value=2025, value=2015, step=1)
            df = pd.read_csv("imdb_top_1000.csv") 
            df["Genre"] = df["Genre"].str.split(",").str[0].str.strip()
            genre_options = sorted(df["Genre"].unique())
            genre = st.selectbox("Genre", genre_options, index=genre_options.index("Comedy") if "Comedy" in genre_options else 0)
        
        submit = st.form_submit_button("Predict Success", type="primary")

    if submit:
        # Prepare input data
        input_data = pd.DataFrame({
            "Runtime": [runtime],
            "Meta_score": [meta_score],
            "Released_Year": [released_year],
            "Genre": [genre]
        })
        genre_encoded = encoder.transform(input_data[["Genre"]])
        genre_df = pd.DataFrame(genre_encoded, columns=encoder.get_feature_names_out(["Genre"]))
        input_encoded = pd.concat([input_data[["Runtime", "Meta_score", "Released_Year"]], genre_df], axis=1)

        # Predict
        try:
            prediction = model.predict(input_encoded)[0]
            if prediction == "Hit":
                st.success(f"Predicted Success: **{prediction}** 🎉")
            elif prediction == "Flop":
                st.error(f"Predicted Success: **{prediction}** 😞")
            else:
                st.warning(f"Predicted Success: **{prediction}** 🤔")
            #st.write(f"Based on: Runtime={runtime} min, Meta Score={meta_score}, Year={released_year}, Genre={genre}")
        except Exception as e:
            st.error(f"Prediction failed: {str(e)}")
