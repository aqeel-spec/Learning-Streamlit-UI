import streamlit as st;
import time


# make a testing app
# Add your code here

st.title("This is a test app")

with st.status("Passing tests...", expanded=True) as status:
    time.sleep(2)
    st.write("Test 1 passed!")
    time.sleep(1)
    st.write("Test 2 passed!")
    time.sleep(1)
    st.write("Test 3 passed!")
    time.sleep(1)
    st.write("Test 4 passed!")
    time.sleep(1)
    status.update(label="All tests passed!", state="complete", expanded=False)


st.button('Rerun')

