import streamlit as st
import pandas as pd
import difflib

st.set_page_config(page_title="Disc Golf AI Recommender", layout="wide")

st.title("Disc Golf Disc Recommender 🥏")

# Load Excel
file = "discer data.xlsx"
df = pd.read_excel(file)

# Keyword maps for Norwegian support
norwegian_keywords = {
    "driver": ["driver"],
    "midrange": ["midrange", "mellomdistanse"],
    "putter": ["putter"],
    "straight": ["rett", "rett frem", "straight"],
    "hyzer": ["hyzer"],
    "hyzer flip": ["hyzer flip"],
    "turnover": ["anhyzer", "turnover"],
    "roller": ["roller", "rulle"],
    "flex shot": ["flex shot", "flex"],
    "skip finish": ["skip", "skip finish"],
    "headwind": ["motvind", "headwind"],
    "tailwind": ["medvind", "tailwind"]
}

# UI sidebar
st.sidebar.header("Filter Discs")
wind = st.sidebar.selectbox("Wind conditions", ["Any", "Calm", "Headwind", "Tailwind"])
flight_path = st.sidebar.selectbox("Preferred Flight Path", ["Any", "Straight", "Hyzer", "Hyzer Flip", "Turnover", "Flex Shot", "Roller", "Skip Finish"])
skill = st.sidebar.selectbox("Skill level", ["Any", "Beginner", "Intermediate"])
disc_category = st.sidebar.selectbox("Disc category", ["All", "Drivers", "Midrange", "Putters"])

filtered = df.copy()

if skill == "Beginner":
    filtered = filtered[filtered["Speed"] <= 9]
elif skill == "Intermediate":
    filtered = filtered[filtered["Speed"] <= 11]

if wind == "Headwind":
    filtered = filtered[(filtered["Turn"] >= 0) & (filtered["Fade"] >= 3)]
elif wind == "Tailwind":
    filtered = filtered[(filtered["Turn"] <= -2) & (filtered["Fade"] <= 2)]

if disc_category != "All":
    keyword = f"disc golf - {disc_category.lower()}"
    filtered = filtered[filtered["CATEGORY"].str.lower().str.strip().str.contains(keyword)]

if flight_path != "Any":
    filtered = filtered[filtered["Main Flight Tag"].str.contains(flight_path, case=False, na=False)]

st.subheader("Matching Discs from Your Collection:")
if filtered.empty:
    st.warning("No discs matched your filters. Try adjusting skill level, category, or flight path.")
else:
    st.dataframe(filtered[["NAME", "Speed", "Glide", "Turn", "Fade", "CATEGORY", "Main Flight Tag"]])

st.header("🧠 Describe the Shot You Want (works in English or Norwegian)")
user_input = st.text_input("Example: 'jeg vil ha en driver for rett kast i medvind'")

if user_input:
    input_text = user_input.lower()
    estimate = {
        "type": "Any",
        "flight_tag": "Any",
        "speed": 7,
        "turn": 0,
        "fade": 2
    }

    def match_keyword(text):
        for tag, words in norwegian_keywords.items():
            for word in words:
                if word in text:
                    return tag
        return None

    # Match disc type
    for t in ["putter", "midrange", "driver"]:
        if any(w in input_text for w in norwegian_keywords[t]):
            estimate["type"] = t.title()
            if t == "putter": estimate["speed"] = 2
            if t == "midrange": estimate["speed"] = 5
            if t == "driver": estimate["speed"] = 9
            break

    # Match flight tag
    tag_found = None
    for tag in ["hyzer flip", "turnover", "flex shot", "roller", "straight", "hyzer", "skip finish"]:
        if any(w in input_text for w in norwegian_keywords[tag]):
            estimate["flight_tag"] = tag.title()
            tag_found = tag
            break

    # Estimate numbers by flight tag
    if tag_found == "hyzer flip":
        estimate["turn"] = -3; estimate["fade"] = 1
    elif tag_found == "turnover":
        estimate["turn"] = -3; estimate["fade"] = 0
    elif tag_found == "flex shot":
        estimate["turn"] = -2; estimate["fade"] = 3
    elif tag_found == "roller":
        estimate["turn"] = -4; estimate["fade"] = 1
    elif tag_found == "straight":
        estimate["turn"] = -1; estimate["fade"] = 1
    elif tag_found == "hyzer":
        estimate["turn"] = 0; estimate["fade"] = 3
    elif tag_found == "skip finish":
        estimate["fade"] = 4

    if any(w in input_text for w in norwegian_keywords["headwind"]):
        estimate["turn"] = max(estimate["turn"], 0)
        estimate["fade"] = max(estimate["fade"], 3)
    elif any(w in input_text for w in norwegian_keywords["tailwind"]):
        estimate["turn"] = min(estimate["turn"], -2)
        estimate["fade"] = min(estimate["fade"], 2)

    st.subheader("🧩 Estimated Flight Parameters")
    st.markdown(f"- Type: **{estimate['type']}**")
    st.markdown(f"- Turn: **{estimate['turn']}**, Fade: **{estimate['fade']}**")
    st.markdown(f"- Tag: **{estimate['flight_tag']}**")

    result = df[
        (df["Speed"] >= estimate["speed"] - 1) & (df["Speed"] <= estimate["speed"] + 1) &
        (df["Turn"] >= estimate["turn"] - 1) & (df["Turn"] <= estimate["turn"] + 1) &
        (df["Fade"] >= estimate["fade"] - 1) & (df["Fade"] <= estimate["fade"] + 1)
    ]

    if estimate["type"] != "Any":
        result = result[result["CATEGORY"].str.lower().str.contains(estimate["type"].lower())]

    if estimate["flight_tag"] != "Any":
        result = result[result["Main Flight Tag"].str.contains(estimate["flight_tag"], case=False, na=False)]

    st.subheader("🎯 Recommended Discs:")
    if not result.empty:
        st.dataframe(result[["NAME", "Speed", "Glide", "Turn", "Fade", "CATEGORY", "Main Flight Tag"]])
    else:
        st.warning("Vi fant ingen helt like disker, men her er noen anbefalte alternativer.")
        fallback = df[df["Speed"] <= 9].sort_values(by=["Speed", "Fade"])
        st.dataframe(fallback[["NAME", "Speed", "Glide", "Turn", "Fade", "CATEGORY", "Main Flight Tag"]].head(5))


