import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Myntra AI Discovery Engine",
    layout="wide"
)

st.title("🔎 Myntra AI Discovery Engine")
st.caption(
    "AI-assisted discovery of purchase barriers, wishlist behaviour "
    "and conversion opportunities."
)

st.divider()

uploaded_file = st.file_uploader(
    "Upload customer feedback CSV",
    type=["csv"]
)

if uploaded_file:

    df = pd.read_csv(uploaded_file)

    st.success(f"Loaded {len(df):,} reviews")

    st.subheader("Dataset Preview")

    st.dataframe(
        df.head(10),
        use_container_width=True,
        hide_index=True
    )

    st.write("Columns found:")

    st.write(df.columns.tolist())
