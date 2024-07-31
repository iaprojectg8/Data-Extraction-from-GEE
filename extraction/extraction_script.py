import os
import sys

# We need this to be able to access the entire repo
path_to_add = os.getcwd()
if path_to_add not in sys.path:
    sys.path.append(path_to_add)

from extraction.helpers import *
from extraction.session_variables import *
from drive.drive import get_files_from_drive

# Authentication to a goole earth engine account and chose a project on which you are
initialize_earth_engine()

# Init date interval and minimum
current_year = date.today().year
default_end_date = datetime(current_year - 1, 12, 31)
default_start_date = datetime(current_year - 2 , 1, 1)
min_date = datetime(2012,2,13)

folder = None

# In case the software is opened on a browser, the tab will have this title and the Groupe Huit logo
put_logo_if_possible()


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



########################################### Map initialization  ########################################################################
restrict_iframe()
m = map_initialization()
json_gdf = file_uploader()
output = map_expander(json_gdf)

    
########################################## Process after the selection made by the user #########################################
# To know what has been selected by the user and the drawing tool
if 'last_active_drawing' in output and output['last_active_drawing'] is not None or "shape" in output:


    output, geometry = fill_geometry(output=output)
    ee_geometry = get_ee_geometry(geometry=geometry)

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
        coverage_threshold=coverage_threshold/100,
        namelbl=name_of_area
    )

    # Put the second map in a session variable
    st.session_state.second_map = m_geemap

    # Display the map in case data has been extracted
    if st.session_state.data:
        st.session_state.second_map.to_streamlit()
        organize_export_button()

        if st.session_state.button and st.session_state.end:

            # The task manager function is responsible for the export
            task_manager(folder_existance=folder_existance)
            st.session_state.export_done = 1
            st.session_state.extracted_but_not_downloaded = 0
            

        if st.session_state.export_done:
            # It shows that the export has been done even if there is a modification on the map, or in the choice of the image
            display_export_progress()
            organize_download_button()
            
            # If the button has been clicked, then the get_file_from_drive function is running, so the download is processed
            if st.session_state.download:
                

                # Download all the folder exported to the drive
                download(folder)
                # This prepare the entire extraction folder path to give it to the conversion function
                st.session_state.complete_folder_path = os.path.join(st.session_state.folder_path, folder)
                organize_conversion_button()
        

            # Keep in mind the download informations even if the page is reload because of whatever move done by the user on it
            elif st.session_state.downloaded_but_not_reset:
                
                # Display the download process that just happened, just to remind, it does 
                display_download()
                # This prepare the entire extraction folder path to give it to the conversion function
                st.session_state.complete_folder_path = os.path.join(st.session_state.folder_path, folder)
                organize_conversion_button()
            
                
                
                    
