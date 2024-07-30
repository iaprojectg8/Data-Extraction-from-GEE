import os
import sys

# We need this to be able to access the entire repo
path_to_add = os.getcwd()
if path_to_add not in sys.path:
    sys.path.append(path_to_add)

from extraction.helpers import *
from utils.imports import *
from utils.variables import *
from drive.drive import get_files_from_drive
from extraction.session_variables import *

# Authentication to a goole earth engine account and chose a project on which you are
initialize_earth_engine()

# Init date interval and minimum
current_year = date.today().year
default_end_date = datetime(current_year - 1, 12, 31)
default_start_date = datetime(current_year - 2 , 1, 1)
min_date = datetime(2012,2,13)

folder = None

# In case the software is opened on a browser, the tab will have this title and the Groupe Huit logo
with open(LOGO_PATH, "rb") as file:
    svg_content = file.read()
st.set_page_config(page_title="Data Extraction",page_icon=svg_content)
st.title("Data Extraction")


############################################### Everything that is on the left side ######################################
options = list(geemap.basemaps.keys())
index = options.index("HYBRID")


st.sidebar.title("Extraction of LST for a given study area",)
basemap = st.sidebar.selectbox("Select a basemap:", options, index,disabled=st.session_state.gray)

# Define placeholders and default values
name_of_area = st.sidebar.text_input('Enter the name of the area', st.session_state.name_area,disabled=st.session_state.gray)
max_cloud_percentage = st.sidebar.slider('Select the maximum cloud percentage on land for LandSat extraction', 0, 100, 5,disabled=st.session_state.gray)
coverage_threshold = st.sidebar.slider("Select the coverage threshold",0, 100, 90,disabled=st.session_state.gray )
epsg_loation = st.sidebar.text_input("Enter EPSG location", st.session_state.epsg_location, disabled=True)
start_date = st.sidebar.date_input('Select the start date for LST extraction', value=default_start_date, min_value=min_date,disabled=st.session_state.gray)
end_date = st.sidebar.date_input('Select the end date for LST extraction', value=default_end_date, min_value=start_date,disabled=st.session_state.gray)
start_hour = st.sidebar.slider('Select start hour of time slot', 0, 23, 6,disabled=st.session_state.gray)
end_hour = st.sidebar.slider('Select end hour of time slot', 0, 24, 20,disabled=st.session_state.gray)
time_difference_gmt = st.sidebar.slider('Enter the time difference when compared to GMT, in hours', -12, 12, 1,disabled=st.session_state.gray)



########################################### Main program ########################################################################

# Set the size of the expander, otherwise it takes the whole page 
iframe_style = """
<style>
    iframe{  
        width:670px;
        height:720px;
    }
<style>
"""

# Use st.markdown to display the iframe, and to restrict the expander size as said before
st.markdown(iframe_style, unsafe_allow_html=True)

# Create a map 
m = folium.Map(location=(1,20), zoom_start=3) 
Draw().add_to(m)
st.session_state.first_map = m


########################################## File uploader #######################################################################
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

# This allow to hide the map when some button is pressed
with st.expander("Draw a zone", st.session_state.expanded,icon=":material/draw:"):
    output = st_folium(st.session_state.first_map, use_container_width=True)

    if uploaded_files:
        output["shape"] = json_gdf
    


########################################## Process the selection made by the user #########################################
# To know what has been selected by the user and the drawing tool
if 'last_active_drawing' in output and output['last_active_drawing'] is not None or "shape" in output:
    if 'last_active_drawing' in output and output['last_active_drawing'] is not None :
        last_drawing = output['last_active_drawing']
        if 'geometry' in last_drawing :
            geometry = last_drawing["geometry"]
   
    elif "shape" in output :
        shape = output["shape"]["features"][0]
        geometry = shape["geometry"]
    
    # Get the coordinates and calculate the EPSG
    coordinates = geometry['coordinates']
    epsg_code = get_epsg_from_polygon(coordinates[0])
    st.session_state.epsg_location = epsg_code
    

    # Convert the coordinates to an ee.Geometry
    ee_geometry = ee.Geometry.Polygon(coordinates)
    if "geometry" not in st.session_state:
        st.session_state.geometry = ee_geometry
    if ee_geometry != st.session_state.geometry:
        st.session_state.geometry = ee_geometry
        callback_stop_export() 

    # Get the center and zoom 
    center, zoom = get_geometry_center_and_zoom(ee_geometry)

    # Create another map and put the basemap chosen by the user
    m_geemap = geemap.Map(center=center, zoom=zoom)
    m_geemap.add_basemap(basemap=basemap)

    # Extract the data and return the map with LST visualisation
    m_geemap, folder, folder_existance = extract_data(    
        map = m_geemap,
        aoi=ee_geometry,
        EPSGloc=str(st.session_state.epsg_location),
        startdate=str(start_date),
        enddate=str(end_date),
        starthour=str(start_hour),
        endhour=str(end_hour),
        dechour=str(time_difference_gmt),
        maxcloud=max_cloud_percentage,
        coverage_threshold=coverage_threshold,
        namelbl=name_of_area
    )

    # Put the second map in a session variable
    st.session_state.second_map = m_geemap

    # Display the map in case data has been extracted
    if st.session_state.data:
        print(folder)
        st.session_state.second_map.to_streamlit()
        col1, col2, col3, col4= st.columns(4)
        
        # Two buttons to launch or stop the export
        with col2:
            st.button("Launch exports",on_click=callback_launch)

        with col3:
            st.button("Stop", on_click=callback_stop_export)
        
        # Launch the export under cetain conditions
        st.session_state.exported_but_not_downloaded = 0
        if st.session_state.button and st.session_state.end:

            # The task manager function is responsible for the export
            task_manager(folder_existance=folder_existance)
            st.session_state.export_done = 1
            st.session_state.extracted_but_not_downloaded = 0
                        

        if st.session_state.export_done:
            # It shows that the export has been done even if there is a modification on the map, or in the choice of the image
            if st.session_state.extracted_but_not_downloaded:
                progress_text=f"The export is done - {100}%"
                st.progress(100, text=progress_text)
                st.write(st.session_state.task_text_list)
            st.success('All the tasks exported')

            # Widget for the download

            
            col1, col2 = st.columns([1.2,0.20],gap="small", vertical_alignment="bottom")  # Adjust the column widths as needed
            with col1:
                st.text_input("Folder path", key='input_path',value=st.session_state.input_path, on_change=update_file_path)
                
            with col2:
                save_clicked = st.button("Save path", on_click=save_path)

            download_clicked = st.button("Download folder", on_click=callback_download)
            st.session_state.extracted_but_not_downloaded = 1     
            
            # If the button has been clicked, then the get_file_from_drive function is running, so the download is processed
            if st.session_state.download:
                
                print("All the files are going to be downloaded")
                get_files_from_drive(path=st.session_state.folder_path,folder_name=folder)
                print("Everyting done")
                st.session_state.download = 0
                st.session_state.downloaded_but_not_reset = 1
                st.success("Everything has been downloaded")

                # This prepare the entire extraction folder path to give it to the conversion function
                st.session_state.complete_folder_path = os.path.join(st.session_state.folder_path, folder)
                convert_to_csv()
        

            # Keep in mind the download informations even if the page is reload because of whatever move done by the user on it
            elif st.session_state.downloaded_but_not_reset:
                progress_text=f"The download is done - {100}%"
                st.progress(100, text=progress_text)
                st.write(st.session_state.task_text_list_downloaded)
                st.success("Everything has been downloaded")
                
                # This prepare the entire extraction folder path to give it to the conversion function
                st.session_state.complete_folder_path = os.path.join(st.session_state.folder_path, folder)
                convert_to_csv()
            
                
                
                    
