import streamlit as st
import pandas as pd

# Load your Excel file
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

# Filter by disc category
if disc_category != "All":
    keyword = f"disc golf - {disc_category.lower()}"
    filtered = filtered[filtered["CATEGORY"].str.lower().str.contains(keyword)]

# Skill level
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

# Display matching discs
st.subheader("✅ Matching Discs from Your Collection:")
st.dataframe(filtered[["NAME", "Speed", "Glide", "Turn", "Fade", "CATEGORY"]])

# -------------------------------
# 🧠 SECTION 2: Smart Language Input
# -------------------------------

st.header("💬 Describe What You're Looking For")

user_input = st.text_input("Say something like: 'I want a stable midrange for hyzer flips in headwind'")

if user_input:
    user_input_lower = user_input.lower()

    # Base defaults
    estimated = {
        "speed": 7,
        "glide": 5,
        "turn": 0,
        "fade": 2,
        "type": "Any"
    }

    # 🥏 Detect disc type
    if "putter" in user_input_lower:
        estimated.update({"type": "Putters", "speed": 2, "glide": 3, "turn": 0, "fade": 1})
    elif "midrange" in user_input_lower or "approach" in user_input_lower:
        estimated.update({"type": "Midrange", "speed": 5, "glide": 4, "turn": 0, "fade": 2})
    elif "driver" in user_input_lower:
        estimated.update({"type": "Drivers", "speed": 9, "glide": 5, "turn": -1, "fade": 2})

    # 🎯 Detect shot style
    if "straight" in user_input_lower:
        estimated["turn"] = -1
        estimated["fade"] = 1
    if "understable" in user_input_lower or "hyzer flip" in user_input_lower or "turnover" in user_input_lower:
        estimated["turn"] = -2
        estimated["fade"] = 1
    if "overstable" in user_input_lower:
        estimated["turn"] = 0
        estimated["fade"] = 3
    if "hyzer" in user_input_lower:
        estimated["turn"] = 0
        estimated["fade"] = max(estimated["fade"], 3)
    if "anhyzer" in user_input_lower:
        estimated["turn"] = -3
        estimated["fade"] = 0
    if "skip" in user_input_lower:
        estimated["fade"] = 4

    # 💨 Wind & throw type
    if "headwind" in user_input_lower:
        estimated["turn"] = max(estimated["turn"], 0)
        estimated["fade"] = max(estimated["fade"], 3)
    if "tailwind" in user_input_lower:
        estimated["turn"] = min(estimated["turn"], -2)
        estimated["fade"] = min(estimated["fade"], 2)
    if "forehand" in user_input_lower:
        estimated["fade"] += 1
        estimated["turn"] += 1
    if "beginner" in user_input_lower:
        estimated["speed"] = min(estimated["speed"], 7)

    # 📊 Show estimated numbers
    st.subheader("📊 Estimated Flight Numbers Based on Your Description:")
    st.markdown(f"- **Disc Type**: {estimated['type']}")
    st.markdown(f"- **Speed**: {estimated['speed']}")
    st.markdown(f"- **Glide**: {estimated['glide']}")
    st.markdown(f"- **Turn**: {estimated['turn']}")
    st.markdown(f"- **Fade**: {estimated['fade']}")

    # 🔎 Try to match from user’s database
    match_df = df[
        (df["Speed"] >= estimated["speed"] - 1) & (df["Speed"] <= estimated["speed"] + 1) &
        (df["Glide"] >= estimated["glide"] - 1) & (df["Glide"] <= estimated["glide"] + 1) &
        (df["Turn"] >= estimated["turn"] - 1) & (df["Turn"] <= estimated["turn"] + 1) &
        (df["Fade"] >= estimated["fade"] - 1) & (df["Fade"] <= estimated["fade"] + 1)
    ]

    if estimated["type"] != "Any":
        match_df = match_df[match_df["CATEGORY"].str.lower().str.contains(estimated["type"].lower())]

    st.subheader("🔍 Matching Discs in Your Collection:")
    if not match_df.empty:
        st.dataframe(match_df[["NAME", "Speed", "Glide", "Turn", "Fade", "CATEGORY"]])
    else:
        st.write("⚠️ No matching discs found — try describing it slightly differently.")


