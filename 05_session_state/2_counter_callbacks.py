
import streamlit as st

st.title("COunter Example using Callback")

if 'count' not in st.session_state:
    st.session_state.count = 0


def increament_counter():
    st.session_state.count += 1

st.button("Increment", on_click=increament_counter)
st.write('Count = ', st.session_state.count)
