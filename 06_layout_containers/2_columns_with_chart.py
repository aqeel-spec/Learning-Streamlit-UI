import streamlit as st
import numpy as np


col1, col2 = st.columns([3,1])

data = np.random.randn(10, 1)

col1.subheader("A wide column with a Chat")
col1.line_chart(data)

col2.subheader("A narrow column with a Map")
col2.write(data)