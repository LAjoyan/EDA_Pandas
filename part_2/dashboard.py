import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Excel Dashboard", layout="wide")

# ---------------- STYLE ----------------
school_bg = "https://images.unsplash.com/photo-1611162617210-c0c33732b6a0?auto=format&fit=crop&w=1950&q=80"
st.markdown(f"""
<style>
.stApp {{
    background: url("{school_bg}") no-repeat center center fixed;
    background-size: cover;
}}
.stSidebar {{
    background-color: rgba(40,40,40,0.9);
    padding: 1rem;
    border-radius: 10px;
    color: #ffffff;
}}
.stDataFrame th {{
    background-color: rgba(60,60,60,0.8) !important;
    color: #ffffff !important;
}}
.stDataFrame td {{
    background-color: rgba(50,50,50,0.8) !important;
    color: #ffffff !important;
}}
input[type=range]::-webkit-slider-thumb {{
    background: #a3c9f1 !important;
}}
input[type=range] {{
    accent-color: #a3c9f1 !important;
}}
div[role="combobox"] {{
    background-color: rgba(163,201,241,0.3) !important;
}}
.stSlider > div > div > div {{
    background-color: #a3c9f1 !important;
}}
.stSlider label {{
    color: #a3c9f1 !important;
}}
/* Hover zoom effect for image */
.zoom-on-hover img {{
    transition: transform 0.3s ease;
}}
.zoom-on-hover img:hover {{
    transform: scale(1.2);
}}
</style>
""", unsafe_allow_html=True)

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    return pd.read_excel("all_years_merged_done_copy.xlsx")

df = load_data()

# ---------------- SIDEBAR PAGE SELECTION ----------------
page = st.sidebar.radio("Navigera", ["Home", "Dashboard"])

# ---------------- HOME PAGE ----------------
if page == "Home":
    st.title("🏠 Välkommen till Yrkeshögskoleportalen")
    st.markdown("""
    Denna webbplats presenterar information om **Yrkeshögskolan (YH)** i Sverige, inklusive resultat från ansökningsomgångar och en översikt över utbildningar per län och kommun.
    """)

    st.subheader("📌 Om Yrkeshögskolan")
    st.markdown("""
    **Yrkeshögskolan** är en svensk eftergymnasial utbildningsform som kombinerar teoretiska studier med praktisk yrkesträning. Utbildningarna är nära kopplade till arbetsmarknadens behov och erbjuds inom olika branscher över hela landet.
    
    - **Längd**: Vanligtvis 1–2 år  
    - **Poäng**: Från 100 poäng (program) upp till 99 poäng (kurser)  
    - **Studieform**: Heltid, deltid eller flexibelt  
    - **Start**: Höst eller vår  
    - **Finansiering**: Statsbidrag via Myndigheten för yrkeshögskolan (MYH)  
    """)

    st.subheader("📊 Resultat från ansökningsomgångar")
    st.markdown("""
    Här kan du ta del av resultaten från tidigare ansökningsomgångar för program och kurser inom Yrkeshögskolan:
    - [Resultat för program](https://www.myh.se/yrkeshogskolan/resultat-ansokningsomgangar/resultat-for-program)  
    - [Resultat för kurser](https://www.myh.se/yrkeshogskolan/resultat-ansokningsomgangar/resultat-for-kurser)  
    """)

    st.subheader("🗺️ Sveriges län")
    
    # Two columns: left for text, right for image
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Län and Område lists
        st.subheader("Län i färgkartan")
        lan_list = sorted(df["Län"].dropna().unique())
        st.write(", ".join(lan_list))

        if "Område" in df.columns:
            st.subheader("Områden")
            omrade_list = sorted(df["Område"].dropna().unique())
            st.write(", ".join(omrade_list))

    with col2:
        # Display the smaller map image on the right with zoom effect
        st.subheader("Kartbild")
        st.markdown('<div class="zoom-on-hover">', unsafe_allow_html=True)
        st.image("sweden-map-counties.jpg", width=400)
        st.markdown('</div>', unsafe_allow_html=True)

# ---------------- DASHBOARD PAGE ----------------
else:
    st.sidebar.header("🎛️ Filter")
    filtered_df = df.copy()

    # Län filter
    lan_options = sorted(df["Län"].dropna().unique())
    selected_lan = st.sidebar.selectbox("Välj Län", ["Alla"] + lan_options)
    if selected_lan != "Alla":
        filtered_df = filtered_df[filtered_df["Län"] == selected_lan]

    # Kommun filter (dependent on Län)
    if "Kommun" in df.columns:
        kommun_options = sorted(filtered_df["Kommun"].dropna().unique())
        selected_kommun = st.sidebar.selectbox("Välj Kommun", ["Alla"] + kommun_options)
        if selected_kommun != "Alla":
            filtered_df = filtered_df[filtered_df["Kommun"] == selected_kommun]

    # Year filter
    if "År" in df.columns:
        year_unique = sorted(filtered_df["År"].dropna().unique())
        if len(year_unique) > 0:
            min_year = int(min(year_unique))
            max_year = int(max(year_unique))
            if min_year < max_year:
                selected_year_range = st.sidebar.select_slider(
                    "År",
                    options=list(range(min_year, max_year + 1)),
                    value=(min_year, max_year)
                )
                filtered_df = filtered_df[
                    (filtered_df["År"] >= selected_year_range[0]) &
                    (filtered_df["År"] <= selected_year_range[1])
                ]

    st.sidebar.write(f"Filtered rows: {len(filtered_df)}")

    # ---------------- DATA PREVIEW ----------------
    st.subheader("🎓 Studieresultat")
    if filtered_df.empty:
        st.warning("Ingen data hittades för de valda filtren.")
    else:
        st.dataframe(filtered_df)

    # ---------------- DOWNLOAD ----------------
    csv = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Ladda ner filtrerad data (CSV)", csv, "filtered_data.csv", "text/csv")
