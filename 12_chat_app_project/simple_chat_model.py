import streamlit as st
import numpy as np

message = st.chat_message("assistant")
message.write("Hello human")
message.bar_chart(np.random.randn(30, 3))

prompt = st.chat_input("Say something")
if prompt:
    message.write(f"You said: {prompt}")