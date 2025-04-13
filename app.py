import streamlit as st
import pandas as pd

# 📁 Load your Excel file
df = pd.read_excel("discer data.xlsx")

st.title("Disc Golf Disc Recommender")

# -------------------------------
# 🎯 SECTION 1: Filter-Based Picker
# -------------------------------

st.header("🎯 Filter by Conditions")

# Dropdown filters
wind = st.selectbox("Wind conditions", ["Calm", "Headwind", "Tailwind"])
shot_shape = st.selectbox("Shot shape", ["Straight", "Hyzer", "Anhyzer", "Turnover", "Skip Finish"])
skill = st.selectbox("Skill level", ["Beginner", "Intermediate", "Advanced"])
disc_category = st.selectbox("Disc category", ["All", "Drivers", "Midrange", "Putters"])

# Start with full list
filtered = df.copy()

# Filter by category (using the CATEGORY column)
if disc_category != "All":
    keyword = f"disc golf - {disc_category.lower()}"
    filtered = filtered[filtered["CATEGORY"].str.lower().str.contains(keyword)]

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
st.subheader("✅ Matching Discs from Your Collection:")
st.dataframe(filtered[["NAME", "Speed", "Glide", "Turn", "Fade", "CATEGORY"]])

# -------------------------------
# 💬 SECTION 2: Smart Language Input
# -------------------------------

st.header("💬 Describe What You're Looking For")

user_input = st.text_input("Say something like: 'I want a straight midrange'")

if user_input:
    user_input_lower = user_input.lower()

    # Default estimates
    estimated = {
        "speed": 7,
        "glide": 5,
        "turn": 0,
        "fade": 2,
        "type": "Any"
    }

    # Shot shape keywords
    if "straight" in user_input_lower:
        estimated["turn"] = -1
        estimated["fade"] = 1
    if "understable" in user_input_lower or "hyzer flip" in user_input_lower:
        estimated["turn"] = -2
        estimated["fade"] = 1
    if "overstable" in user_input_lower or "headwind" in user_input_lower:
        estimated["turn"] = 0
        estimated["fade"] = 3

    # Throw type keywords
    if "forehand" in user_input_lower:
        estimated["speed"] = 9
        estimated["fade"] += 1
    if "beginner" in user_input_lower:
        estimated["speed"] = 6

    # Disc type detection
    if "putter" in user_input_lower:
        estimated["speed"] = 3
        estimated["type"] = "Putters"
    elif "midrange" in user_input_lower or "approach" in user_input_lower:
        estimated["speed"] = 5
        estimated["type"] = "Midrange"
    elif "driver" in user_input_lower:
        estimated["speed"] = 9
        estimated["type"] = "Drivers"

    # Show result
    st.subheader("📊 Estimated Flight Numbers Based on Your Description:")
    st.markdown(f"- **Disc Type**: {estimated['type']}")
    st.markdown(f"- **Speed**: {estimated['speed']}")
    st.markdown(f"- **Glide**
