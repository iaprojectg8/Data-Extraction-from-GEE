import streamlit as st
from utils.imports import *





st.write("This is the content inside the expander.")
m = folium.Map(location=(1,20), zoom_start=3) 
st_folium(m,use_container_width=True)
    