import streamlit as st
import pandas as pd
from openai import OpenAI
import json

# --- AUTH ---
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# --- LAST INN DATA ---
df = pd.read_excel("discer data.xlsx")

# --- SIDEBAR FILTERE ---
st.sidebar.header("Filter Discs")
wind = st.sidebar.selectbox("Wind conditions", ["Any", "Calm", "Moderate", "Strong headwind"])
flight_path = st.sidebar.selectbox("Preferred Flight Path", ["Any", "Straight", "Hyzer", "Turnover", "Hyzer Flip", "Flex Shot", "Roller", "Skip Finish"])
skill = st.sidebar.selectbox("Skill level", ["Any", "Beginner", "Intermediate", "Advanced"])
category = st.sidebar.selectbox("Disc category", ["Any", "Drivers", "Midrange", "Putters"])

# --- HOVEDTITTEL ---
st.title("Disc Golf Disc Recommender 🌀")

# --- AI INPUT ---
st.header("🧠 Beskriv Kastet du Ønsker (Norsk eller Engelsk)")
user_input = st.text_input("Eksempel: 'Jeg trenger en disc som svinger mye mot slutten' eller 'I want a straight driver for beginners'")

# --- PARSE AI ---
@st.cache_data(show_spinner=False)
def parse_flight_numbers(user_text):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": (
                    "Du er en disc golf-assistent som analyserer tekst og gir forslag til flight numbers. "
                    "Svar alltid i JSON-format som dette: {\"recommended_flight_numbers\": {\"speed\": 9, \"glide\": 4, \"turn\": -2, \"fade\": 2}} "
                    "Svar kun flight-tallene, ikke gi disk-navn eller annen info."
                )},
                {"role": "user", "content": user_text}
            ]
        )
        parsed = json.loads(response.choices[0].message.content)
        return parsed.get("recommended_flight_numbers", {})
    except Exception as e:
        st.warning(f"Feil i AI-tolkning: {e}")
        return {}

# --- FILTRERING BASERT PÅ AI OG BRUKERVALG ---
def filter_discs(df, filters):
    filtered = df.copy()
    if wind != "Any":
        if wind == "Strong headwind":
            filtered = filtered[filtered["Stability"] == "Overstable"]
    if flight_path != "Any":
        filtered = filtered[filtered["Main Flight Tag"] == flight_path]
    if skill != "Any":
        if skill == "Beginner":
            filtered = filtered[filtered["Speed"] <= 7]
        elif skill == "Intermediate":
            filtered = filtered[(filtered["Speed"] > 7) & (filtered["Speed"] <= 10)]
        else:
            filtered = filtered[filtered["Speed"] > 10]
    if category != "Any":
        filtered = filtered[filtered["CATEGORY"].str.contains(category)]
    if filters:
        for key, val in filters.items():
            filtered = filtered[filtered[key.capitalize()] == val]
    return filtered

# --- VISNING ---
flight_numbers = {}
if user_input:
    with st.spinner("Tolker beskrivelse med AI..."):
        flight_numbers = parse_flight_numbers(user_input)
        if flight_numbers:
            st.subheader("💡 AI tolket dette som:")
            st.json(flight_numbers)

            results = filter_discs(df, flight_numbers)
            if results.empty:
                st.warning("Ingen perfekte treff. Viser nybegynnervennlige alternativer:")
                results = df[(df["Speed"] <= 7) & (df["CATEGORY"].str.contains("Putters|Midrange"))]
            st.subheader("📌 Anbefalte disker fra AI:")
            st.dataframe(results[["ITEM NUMBER", "NAME", "CATEGORY", "QTY IN STOCK", "PRICE", "Speed", "Glide", "Turn", "Fade", "Stability", "Main Flight Tag"]])
        else:
            st.warning("Klarte ikke å tolke forespørselen til flight numbers.")


