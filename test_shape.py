import streamlit as st
import geopandas as gpd
import folium
from shapely.geometry import mapping
from streamlit_folium import st_folium
import tempfile
import os
from pyproj import CRS

# Function to load the shapefile and read the CRS from the .prj file
def load_shapefile(uploaded_files):
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as tmpdirname:
        # Save the uploaded files to the temporary directory
        for uploaded_file in uploaded_files:
            file_path = os.path.join(tmpdirname, uploaded_file.name)
            with open(file_path, 'wb') as f:
                f.write(uploaded_file.getbuffer())
        
        # Find the .shp and .prj files
        shp_file = [os.path.join(tmpdirname, f.name) for f in uploaded_files if f.name.endswith('.shp')][0]
        prj_file = [os.path.join(tmpdirname, f.name) for f in uploaded_files if f.name.endswith('.prj')]

        # Read the shapefile
        gdf = gpd.read_file(shp_file)

        # Load CRS from .prj file if it exists
        if prj_file:
            try:
                with open(prj_file[0], 'r') as f:
                    crs_str = f.read().strip()
                    crs = CRS(crs_str)
                    gdf.crs = crs
            except Exception as e:
                st.error(f"Error reading CRS from .prj file: {e}")
        else:
            st.warning("No .prj file found. Defaulting CRS to EPSG:4326.")
            gdf.crs = CRS.from_epsg(4326)

        return gdf

# Function to visualize geometries on a Folium map
def visualize_geometries(gdf):
    
    gdf = gdf.to_crs(epsg=gdf.crs.to_epsg())

    geometries = gdf['geometry']
    geometries = geometries.to_crs(epsg=gdf.crs.to_epsg())
    centroid = geometries.centroid.iloc[0]
    m = folium.Map(location=[centroid.y, centroid.x], zoom_start=12)

    # Add geometries to the map
    for geom in geometries:
        geo_json = mapping(geom)
        folium.GeoJson(geo_json).add_to(m)

    return m

# Streamlit app
def main():
    st.title("Shapefile Upload and Visualization")

    uploaded_files = st.file_uploader("Choose shapefile components", type=["shp", "shx", "dbf", "prj"], accept_multiple_files=True)

    if uploaded_files:
        st.write("Files uploaded successfully!")

        # Load the shapefile
        gdf = load_shapefile(uploaded_files)

        # Display the first few rows of the GeoDataFrame
        st.write(gdf.head())

        # Visualize the geometries on a Folium map
        folium_map = visualize_geometries(gdf)

        # Display the map in Streamlit
        st_folium(folium_map, width=700, height=500)

if __name__ == "__main__":
    main()
