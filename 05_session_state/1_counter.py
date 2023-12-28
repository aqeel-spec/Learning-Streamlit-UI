import streamlit as st

st.title("Counter Example")
st.header("Couter with session state")

if 'count' not in st.session_state:
    st.session_state.count = 0

increament : int = st.button("Increament")
if increament:
    st.session_state.count += 1

st.write("Count = ", st.session_state.count)