# https://docs.streamlit.io/library/api-reference/layout/st.sidebar

# https://docs.streamlit.io/library/api-reference/layout/st.sidebar

import streamlit as st

# Add buttons to sidebar
st.sidebar.button("New chat")

# Using object notation
add_selectbox = st.sidebar.selectbox(
    "How would you like to be contacted?",
    ("Email", "Home phone", "Mobile phone")
)

# Using "with" notation
with st.sidebar:
    add_radio = st.radio(
        "Choose a shipping method",
        ("Standard (5-15 days)", "Express (2-5 days)")
    )