# https://docs.streamlit.io/library/api-reference/layout/st.tabs

import streamlit as st

tab1, tab2, tab3 = st.tabs(["Cat","Dog","Owl"])

with tab1:
    st.header("A cat")
    st.image("https://static.streamlit.io/examples/cat.jpg")

with tab2:
    st.header("A dog")
    st.image("https://static.streamlit.io/examples/dog.jpg")

with tab3:
    st.header("An owl")
    st.image("https://static.streamlit.io/examples/owl.jpg")