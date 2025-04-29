import streamlit as st
import pandas as pd
import os
from openai import OpenAI

st.set_page_config(page_title="Disc Golf AI Recommender", layout="wide")

st.title("Disc Golf Disc Recommender 🥏")

# Load Excel
df = pd.read_excel("discer data.xlsx")

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"] if "OPENAI_API_KEY" in st.secrets else os.getenv("OPENAI_API_KEY"))

# --- FILTREDE DELER ---
st.sidebar.header("🎯 Filter Discer")
wind = st.sidebar.selectbox("Vindforhold", ["Any", "Calm", "Headwind"])
flight_path = st.sidebar.selectbox("Ønsket Flybane", ["Any", "Straight", "Hyzer", "Turnover", "Hyzer Flip", "Flex Shot", "Skip Finish"])
skill = st.sidebar.selectbox("Ferdighetsnivå", ["Any", "Beginner", "Intermediate", "Advanced"])
disc_category = st.sidebar.selectbox("Disctype", ["Any"] + sorted(df["CATEGORY"].unique()))

# --- AI INNGANG ---
st.header("🧠 Beskriv Kastet du Ønsker (Norsk eller Engelsk)")
user_input = st.text_input("Eksempel: 'Jeg trenger en disc som svinger mye mot slutten' eller 'I want a straight driver for beginners'")

@st.cache_data(show_spinner=False)
def parse_flight_numbers(user_text):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Du er en disc golf-assistent som analyserer tekst og gir forslag til flight numbers. "
                        "Svar alltid i JSON-format som dette: {\"recommended_flight_numbers\": {\"speed\": 9, \"glide\": 4, \"turn\": -1, \"fade\": 2}, \"type\": \"Driver\", \"skill\": \"Beginner\", \"flight_path\": \"Straight\", \"wind\": \"Calm\", \"explanation\": \"Hyzer betyr overstabilitet...\"}. "
                        "Ikke gi disknavn, kun flight-tall og forklaring."
                    )
                },
                {"role": "user", "content": user_text}
            ]
        )
        raw = response.choices[0].message.content
        parsed = eval(raw) if "{" in raw else {}
        return parsed
    except Exception as e:
        st.warning(f"Feil i AI-tolkning: {e}")
        return {}

# --- FILTRER DATAFRAME ---
def filter_dataframe(df, wind, flight_path, skill, category):
    df_filtered = df.copy()
    if wind != "Any":
        df_filtered = df_filtered[df_filtered["Wind"].fillna("") == wind]
    if flight_path != "Any":
        df_filtered = df_filtered[df_filtered["Main Flight Tag"].fillna("").str.contains(flight_path, case=False)]
    if skill != "Any":
        df_filtered = df_filtered[df_filtered["Skill"].fillna("") == skill]
    if category != "Any":
        df_filtered = df_filtered[df_filtered["CATEGORY"] == category]
    return df_filtered

# --- VIS FILTRERTE DISKER ---
st.subheader("📦 Discer som Matcher Filterene dine:")
filtered_df = filter_dataframe(df, wind, flight_path, skill, disc_category)
st.dataframe(filtered_df[["NAME", "Speed", "Glide", "Turn", "Fade", "CATEGORY", "Main Flight Tag"]])

# --- GPT DELEN ---
if user_input:
    result = parse_flight_numbers(user_input)

    if result and "recommended_flight_numbers" in result:
        st.success("🔎 Basert på det du skrev, let etter en disc med følgende egenskaper:")
        fn = result["recommended_flight_numbers"]
        st.markdown(f"- **Speed**: {fn.get('speed', '?')}")
        st.markdown(f"- **Glide**: {fn.get('glide', '?')}")
        st.markdown(f"- **Turn**: {fn.get('turn', '?')}")
        st.markdown(f"- **Fade**: {fn.get('fade', '?')}")

        if "explanation" in result:
            st.info(f"💬 Forklaring fra AI: {result['explanation']}")

        # Eksakt treff
        matches = df[
            (df["Speed"] == fn.get("speed")) &
            (df["Glide"] == fn.get("glide")) &
            (df["Turn"] == fn.get("turn")) &
            (df["Fade"] == fn.get("fade"))
        ]

        # Nære treff
        nearby = df[
            (df["Speed"].between(fn.get("speed") - 1, fn.get("speed") + 1)) &
            (df["Glide"].between(fn.get("glide") - 1, fn.get("glide") + 1)) &
            (df["Turn"].between(fn.get("turn") - 1, fn.get("turn") + 1)) &
            (df["Fade"].between(fn.get("fade") - 1, fn.get("fade") + 1))
        ]

        if not matches.empty:
            st.subheader("🎯 Eksakte Discer i din Samling:")
            st.dataframe(matches[["NAME", "CATEGORY", "Speed", "Glide", "Turn", "Fade", "Stability", "Main Flight Tag"]])
        elif not nearby.empty:
            st.subheader("📍 Nærliggende Alternativer i Samlingen:")
            st.dataframe(nearby[["NAME", "CATEGORY", "Speed", "Glide", "Turn", "Fade", "Stability", "Main Flight Tag"]])
        else:
            st.info("Ingen passende treff i databasen. Bruk tallene over som guide i butikk/nettbutikk.")
    else:
        st.warning("Klarte ikke å tolke forespørselen til flight numbers.")


