from utils.imports import *
from lib.geometry import get_geometry_center_and_zoom_json

def load_shapefile(uploaded_files):
    """
    Function to load a shape file and all its components, it needs at least the following list of 
    file : shp, shx, prj.

    Args:
        uploaded_files (list) : List of uploaded shape files for a geometry

    Returns:
        gdf (geopandas.GeoDataFrame): Geodataframe containing the geometry of the files
    """
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as tmpdirname:
        # Save the uploaded files to the temporary directory
        for uploaded_file in uploaded_files:
            file_path = os.path.join(tmpdirname, uploaded_file.name)
            with open(file_path, 'wb') as f:
                f.write(uploaded_file.getbuffer())
        
        # Find the .shp and .prj files
        shp_file = [os.path.join(tmpdirname, f.name) for f in uploaded_files if f.name.endswith('.shp')][0]
        
        # Read the shapefile
        gdf = gpd.read_file(shp_file)
       
        return gdf

def file_uploader():
    """
    Function that initializes the expander in which the first map will be.
    Args: 
        json_gdf (dict): JSON object in which there are the coordinates of an uploaded shape file .
    Returns:
        output (dict) : It contains either the shape file coordiantes either the drawn shape ones
    """
    # Manage the file uploader
    uploaded_files = st.file_uploader("Choose shapefile components", type=["shp", "shx", "dbf", "prj"], accept_multiple_files=True)
    if uploaded_files:
        st.write("Files uploaded successfully!")

        # Load the shapefile
        gdf = load_shapefile(uploaded_files)
        gdf = gdf.to_crs(epsg=4326)
        
        # Transform the geometry into a json 
        json_string = gdf.to_json()
        json_gdf = json.loads(json_string)

        # Get the coordinates
        coordinates = json_gdf["features"][0]["geometry"]["coordinates"][0]
        centre, zoom = get_geometry_center_and_zoom_json(coordinates)

        # Create a Folium map centered and zoomed to the right place
        m = folium.Map(location=[*centre], zoom_start=zoom)
        folium.GeoJson(gdf).add_to(m)
        Draw().add_to(m)

        # Put the map into a session variable to remind it
        st.session_state.first_map = m  

        return json_gdf
