import streamlit as st
import pandas as pd

# 📁 Load your Excel file
df = pd.read_excel("discer data.xlsx")

# 🏷️ Title
st.title("Disc Golf Disc Recommender")

# -------------------------------
# 🔧 SECTION 1: Filter-Based Picker
# -------------------------------

st.header("🎯 Filter by Conditions")

# Dropdown filters
wind = st.selectbox("Wind conditions", ["Calm", "Headwind", "Tailwind"])
shot_shape = st.selectbox("Shot shape", ["Straight", "Hyzer", "Anhyzer", "Turnover", "Skip Finish"])
skill = st.selectbox("Skill level", ["Beginner", "Intermediate", "Advanced"])

# Start with all discs
filtered = df.copy()

# Skill level filter
if skill == "Beginner":
    filtered = filtered[filtered["Speed"] <= 9]
elif skill == "Intermediate":
    filtered = filtered[filtered["Speed"] <= 11]

# Shot shape logic
if shot_shape == "Straight":
    filtered = filtered[(filtered["Turn"] >= -1) & (filtered["Turn"] <= 0) & (filtered["Fade"] <= 2)]
elif shot_shape == "Hyzer":
    filtered = filtered[(filtered["Turn"] >= 0) & (filtered["Fade"] >= 2)]
elif shot_shape == "Anhyzer":
    filtered = filtered[(filtered["Turn"] <= -2) & (filtered["Fade"] <= 1)]
elif shot_shape == "Turnover":
    filtered = filtered[(filtered["Turn"] <= -2)]
elif shot_shape == "Skip Finish":
    filtered = filtered[(filtered["Fade"] >= 3)]

# Wind logic
if wind == "Headwind":
    filtered = filtered[(filtered["Turn"] >= 0) & (filtered["Fade"] >= 3)]
elif wind == "Tailwind":
    filtered = filtered[(filtered["Turn"] <= -2) & (filtered["Fade"] <= 2)]

# Show results
st.subheader("✅ Discs from your collection that match:")
st.dataframe(filtered[["NAME", "Speed", "Glide", "Turn", "Fade"]])

# -------------------------------
# 🧠 SECTION 2: Smart Language Input
# -------------------------------

st.header("💬 Describe What You're Looking For")

user_input = st.text_input("Say something like: 'I want a driver that goes straight'")

if user_input:
    user_input_lower = user_input.lower()

    # Default guess
    estimated = {
        "speed": 7,
        "glide": 5,
        "turn": 0,
        "fade": 2
    }

    # Phrase interpretation
    if "straight" in user_input_lower:
        estimated["turn"] = -1
        estimated["fade"] = 1
    if "understable" in user_input_lower or "hyzer flip" in user_input_lower:
        estimated["turn"] = -2
        estimated["fade"] = 1
    if "overstable" in user_input_lower or "headwind" in user_input_lower:
        estimated["turn"] = 0
        estimated["fade"] = 3
    if "forehand" in user_input_lower:
        estimated["speed"] = 9
        estimated["fade"] += 1
    if "beginner" in user_input_lower:
        estimated["speed"] = 6

    # Output the results
    st.subheader("📊 Based on what you typed, you're looking for:")
    st.markdown(f"- **Speed**: {estimated['speed']}")
    st.markdown(f"- **Glide**: {estimated['glide']}")
    st.markdown(f"- **Turn**: {estimated['turn']}")
    st.markdown(f"- **Fade**: {estimated['fade']}")

