import streamlit as st
import pandas as pd

# Load disc data from Excel
st.title("Disc Golf Disc Recommender")

# Load file
uploaded_file = "discer data.xlsx"
df = pd.read_excel(uploaded_file)

# Filters
st.sidebar.header("Filter Discs")
wind = st.sidebar.selectbox("Wind conditions", ["Any", "Calm", "Headwind", "Tailwind"])
flight_path = st.sidebar.selectbox("Preferred Flight Path", [
    "Any", "Straight", "Hyzer", "Hyzer Flip", "Turnover", "Flex Shot", "Roller", "Skip Finish"])
skill = st.sidebar.selectbox("Skill level", ["Any", "Beginner", "Intermediate"])
disc_category = st.sidebar.selectbox("Disc category", ["All", "Drivers", "Midrange", "Putters"])

# Apply filters
filtered = df.copy()

# Skill-based filter (based on Speed)
if skill == "Beginner":
    filtered = filtered[filtered["Speed"] <= 9]
elif skill == "Intermediate":
    filtered = filtered[filtered["Speed"] <= 11]

# Wind filter
if wind == "Headwind":
    filtered = filtered[(filtered["Turn"] >= 0) & (filtered["Fade"] >= 3)]
elif wind == "Tailwind":
    filtered = filtered[(filtered["Turn"] <= -2) & (filtered["Fade"] <= 2)]

# Category filter
if disc_category != "All":
    keyword = f"disc golf - {disc_category.lower()}"
    filtered = filtered[filtered["CATEGORY"].str.lower().str.strip().str.contains(keyword)]

# Flight path filter
if flight_path != "Any":
    filtered = filtered[filtered["Main Flight Tag"].str.contains(flight_path, case=False, na=False)]

# Show filtered results
st.subheader("Matching Discs from Your Collection:")
if filtered.empty:
    st.warning("No discs matched your filters. Try adjusting skill level, category, or flight path.")
else:
    st.dataframe(filtered[["NAME", "Speed", "Glide", "Turn", "Fade", "CATEGORY", "Main Flight Tag"]])

# Smart text input
st.header("Describe the Shot You Want")
user_input = st.text_input("Example: 'I want a hyzer flip driver for calm wind'")

if user_input:
    ui = user_input.lower()

    # Initial defaults
    estimated = {
        "type": "Any",
        "speed": 7,
        "glide": 5,
        "turn": 0,
        "fade": 2,
        "flight_tag": "Any"
    }

    if "putter" in ui:
        estimated["type"] = "Putters"
        estimated["speed"] = 2
    elif "midrange" in ui or "approach" in ui:
        estimated["type"] = "Midrange"
        estimated["speed"] = 5
    elif "driver" in ui:
        estimated["type"] = "Drivers"
        estimated["speed"] = 9

    if "hyzer flip" in ui:
        estimated["flight_tag"] = "Hyzer Flip"
        estimated["turn"] = -3
        estimated["fade"] = 1
    elif "turnover" in ui or "anhyzer" in ui:
        estimated["flight_tag"] = "Turnover"
        estimated["turn"] = -3
        estimated["fade"] = 0
    elif "flex" in ui:
        estimated["flight_tag"] = "Flex Shot"
        estimated["turn"] = -2
        estimated["fade"] = 3
    elif "roller" in ui:
        estimated["flight_tag"] = "Roller"
        estimated["turn"] = -4
        estimated["fade"] = 1
    elif "straight" in ui:
        estimated["flight_tag"] = "Straight"
        estimated["turn"] = -1
        estimated["fade"] = 1
    elif "hyzer" in ui:
        estimated["flight_tag"] = "Hyzer"
        estimated["turn"] = 0
        estimated["fade"] = 3
    elif "skip" in ui:
        estimated["flight_tag"] = "Skip Finish"
        estimated["fade"] = 4

    if "headwind" in ui:
        estimated["turn"] = max(estimated["turn"], 0)
        estimated["fade"] = max(estimated["fade"], 3)
    elif "tailwind" in ui:
        estimated["turn"] = min(estimated["turn"], -2)
        estimated["fade"] = min(estimated["fade"], 2)

    # Show estimation
    st.subheader("Estimated Flight Numbers")
    st.markdown(f"- Type: **{estimated['type']}**")
    st.markdown(f"- Speed: **{estimated['speed']}**")
    st.markdown(f"- Turn: **{estimated['turn']}**, Fade: **{estimated['fade']}**")

    # Filter using estimation
    result = df[
        (df["Speed"] >= estimated["speed"] - 1) & (df["Speed"] <= estimated["speed"] + 1) &
        (df["Turn"] >= estimated["turn"] - 1) & (df["Turn"] <= estimated["turn"] + 1) &
        (df["Fade"] >= estimated["fade"] - 1) & (df["Fade"] <= estimated["fade"] + 1)
    ]

    if estimated["type"] != "Any":
        result = result[result["CATEGORY"].str.lower().str.contains(estimated["type"].lower())]

    if estimated["flight_tag"] != "Any":
        result = result[result["Main Flight Tag"].str.contains(estimated['flight_tag'], case=False, na=False)]

    st.subheader("Recommended Discs:")
    if not result.empty:
        st.dataframe(result[["NAME", "Speed", "Glide", "Turn", "Fade", "CATEGORY", "Main Flight Tag"]])
    else:
        st.warning("No discs matched your description. Try changing your input or adding more discs to the database.")


