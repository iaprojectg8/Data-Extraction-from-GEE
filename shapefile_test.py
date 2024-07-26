import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import st_folium
import tempfile
import os

# Streamlit app title
st.title('Shapefile Renderer')

# File uploader
uploaded_files = st.file_uploader("Upload a shapefile (shp, dbf, shx)", type=["shp", "dbf", "shx","prj"], accept_multiple_files=True)

if uploaded_files:
    # Create a temporary directory to store the uploaded files
    with tempfile.TemporaryDirectory() as tmpdirname:
        for uploaded_file in uploaded_files:
            with open(os.path.join(tmpdirname, uploaded_file.name), "wb") as f:
                f.write(uploaded_file.getbuffer())

        # Locate the .shp file
        shp_path = [os.path.join(tmpdirname, file.name) for file in uploaded_files if file.name.endswith('.shp')][0]

        # Read the shapefile
        gdf = gpd.read_file(shp_path)
        print("crs", gdf.crs)

        # Ensure CRS is set to EPSG:4326 for Folium compatibility
        
        # gdf projection
        print(type(gdf))
        gdf = gdf.to_crs(epsg=4326)
        centroids = gdf.centroid[0]
        gdf = gdf.to_crs(epsg=3857)

        # Create a Folium map centered around the centroid
        m = folium.Map(location=[centroids.y,centroids.x], zoom_start=8)

        # Add the shapefile data to the map
        folium.GeoJson(gdf).add_to(m)
        # Display the map
        st_folium(m, width=700, height=500)
else:
    st.write("Please upload the necessary shapefile files (.shp, .dbf, .shx).")
