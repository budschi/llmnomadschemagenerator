# Import the streamlit library
import streamlit as st

# Title of the app
st.title('My First Streamlit App')

# Add a button
if st.button('Say hello'):
   st.write('Hello, Streamlit!')