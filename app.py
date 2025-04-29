import streamlit as st
import pandas as pd
import openai
import json
import os

# Load secrets (OpenAI key)
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Load disc data
df = pd.read_excel("discer data.xlsx")

# Title
st.title("Disc Golf Disc Recommender \U0001F30A")

# --- Sidebar filters ---
st.sidebar.header("Filter Discs")
wind = st.sidebar.selectbox("Wind conditions", ["Any", "Calm", "Moderate", "Strong headwind"])
flight_path = st.sidebar.selectbox("Preferred Flight Path", ["Any", "Straight", "Hyzer", "Anhyzer", "Hyzer Flip", "Turnover", "Flex Shot"])
skill = st.sidebar.selectbox("Skill level", ["Any", "Beginner", "Intermediate", "Advanced"])
category = st.sidebar.selectbox("Disc category", ["Any"] + sorted(df["CATEGORY"].unique()))

# --- AI Section ---
st.header("\U0001F9E0 Beskriv Kastet du Ønsker (Norsk eller Engelsk)")
user_input = st.text_input("Eksempel: 'Jeg trenger en disc som svinger mye mot slutten' eller 'I want a straight driver for beginners'")

# --- AI Parsing Function ---
def parse_flight_numbers(user_text):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": (
                    "Du er en disc golf-assistent som analyserer tekst og gir forslag til flight numbers. "
                    "Svar alltid i JSON-format som dette: {\"recommended_flight_numbers\": {\"speed\": 9, \"glide\": 4, \"turn\": -1, \"fade\": 2}}."
                )},
                {"role": "user", "content": user_text}
            ]
        )
        parsed = json.loads(response.choices[0].message.content)
        return parsed.get("recommended_flight_numbers")
    except Exception as e:
        st.warning(f"AI tolkning feilet: {e}")
        return None

# --- Filtering Logic ---
def filter_discs(df, filters):
    filtered = df.copy()
    if filters.get("speed") is not None:
        filtered = filtered[filtered["Speed"] == filters["speed"]]
    if filters.get("glide") is not None:
        filtered = filtered[filtered["Glide"] == filters["glide"]]
    if filters.get("turn") is not None:
        filtered = filtered[filtered["Turn"] == filters["turn"]]
    if filters.get("fade") is not None:
        filtered = filtered[filtered["Fade"] == filters["fade"]]
    return filtered

# --- Main Recommendation Logic ---
if user_input:
    ai_filters = parse_flight_numbers(user_input)
    if ai_filters:
        results = filter_discs(df, ai_filters)
        if results.empty:
            st.warning("Ingen perfekte treff. Viser nybegynnervennlige alternativer:")
            results = df[df["Speed"] <= 6]  # fallback
        st.subheader("📌 Anbefalte disker fra AI:")
        st.dataframe(results[["NAME", "Speed", "Glide", "Turn", "Fade", "CATEGORY", "Main Flight Tag"]])
else:
    filtered = df.copy()
    if wind != "Any":
        if wind == "Strong headwind":
            filtered = filtered[filtered["Stability"].str.contains("Overstable")]
        elif wind == "Calm":
            filtered = filtered[filtered["Stability"].str.contains("Understable")]
    if flight_path != "Any":
        filtered = filtered[filtered["Main Flight Tag"].str.contains(flight_path, case=False, na=False)]
    if skill != "Any":
        if skill == "Beginner":
            filtered = filtered[filtered["Speed"] <= 6]
        elif skill == "Intermediate":
            filtered = filtered[(filtered["Speed"] > 5) & (filtered["Speed"] <= 9)]
        elif skill == "Advanced":
            filtered = filtered[filtered["Speed"] >= 9]
    if category != "Any":
        filtered = filtered[filtered["CATEGORY"] == category]

    st.subheader("📊 Matching Discs from Your Collection:")
    st.dataframe(filtered[["NAME", "Speed", "Glide", "Turn", "Fade", "CATEGORY", "Main Flight Tag"]])


