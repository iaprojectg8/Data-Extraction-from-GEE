# import os
# import sys
# print("\nfirst",sys.path)
# current_dir = os.path.dirname(os.path.abspath(__file__))
# sys.path.append(os.path.join(current_dir, '..'))
# print("\nsecond",sys.path)

from extraction.helpers import *
from utils.imports import *
from utils.variables import *
from drive.drive import get_files_from_drive

# Authentication to a goole earth engine account and chose a project on which you are
ee.Authenticate()

# Maybe need to create one if you don't have any
with open(GEE_PROJECT, 'r') as f:
    config = json.load(f)

ee.Initialize(project=config["project"])

# Session variable to know if the user clicked on the button. If so the variable will be 1 else 0
if "button" not in st.session_state:
    st.session_state.button = 0

# Session variable to know if the task manager is finished. If so the variable will be 1 else 0, it means the task manager currently working
if "end" not in st.session_state:
    st.session_state.end = 1

# Session variable to know the task status continuously
if "status" not in st.session_state:
    st.session_state.status = ""

# Session variable that contains the task list made during the extract data. It will then be used to give information about the progress of the export
if "task_list" not in st.session_state :
    st.session_state.task_list = []

# Session variable to know when the launch button has been clicked to hide the first map which cuts the export when being modified
if "expanded" not in st.session_state :
    st.session_state.expanded = 1

# Session variable to know if the export data function has been successful and have got data in it
if "data" not in st.session_state:
    st.session_state.data = 0

# Session variable to know what is the place of the selected area. Need to be change by the user typing in the right field, name area
if "epsg_location" not in st.session_state:
    st.session_state.epsg_location = "No data"

# Session variable to know when the download button has been clicked and then enter an if statement to launch the downloading from the drive
if "download" not in st.session_state:
    st.session_state.download = 0

# Session varialbe to display information if the export has been completed
if "export_done" not in st.session_state:
    st.session_state.export_done = 0

# Session variable to store the first map
if "first_map" not in st.session_state:
    st.session_state.first_map = None

# Session variable to store the second map
if "second_map" not in st.session_state:
    st.session_state.second_map = None

# Session variable to show the user information in case the download has been done
if "download_done" not in st.session_state:
    st.session_state.download_done = 0

# Session variable to show information about the list of features exported in real time and after it has been done
if "task_text_list" not in st.session_state:
    st.session_state.task_text_list = ""

# Session variable to show information about the list of features downloaded in real time and after it has been done
if "task_text_list_downloaded" not in st.session_state:
    st.session_state.task_text_list_downloaded = ""

# Session variable to show information about the download, even after some modification when the stop button has not been clicked
if "downoloaded_but_not_reset" not in st.session_state:
    st.session_state.downoloaded_but_not_reset = 0

# Session variable to track the folder path for the download
if "folder_path" not in st.session_state:
    st.session_state.folder_path = PATH

# Session variable update the folder path when it is changed in the text input
if 'input_path' not in st.session_state:
    st.session_state.input_path = PATH

# Session variable that allows to gray all the parameters on the left side
if "gray" not in st.session_state:
    st.session_state.gray = 0

if "extracted_but_not_downloaded" not in st.session_state:
    st.session_state.extracted_but_not_downloaded = 0




# variable init
default_start_date = datetime(2022, 1, 1)
default_end_date = datetime(2022, 8, 31)
min_date = datetime(2012,2,13)
folder = None
st.title("Data Extraction")

############################################### Everything that is on the left side ######################################
options = list(geemap.basemaps.keys())
index = options.index("HYBRID")


st.sidebar.title("Extraction of LST for a given study area",)
basemap = st.sidebar.selectbox("Select a basemap:", options, index,disabled=st.session_state.gray)

# Define placeholders and default values
name_of_area = st.sidebar.text_input('Enter the name of the area', "No data",disabled=st.session_state.gray)
max_cloud_percentage = st.sidebar.slider('Select the maximum cloud percentage on land for LandSat extraction', 0, 100, 5,disabled=st.session_state.gray)
coverage_threshold = st.sidebar.slider("Select the coverage threshold",0, 100, 90,disabled=st.session_state.gray )
epsg_loation = st.sidebar.text_input("Enter EPSG location", st.session_state.gray, disabled=True)
start_date = st.sidebar.date_input('Select the start date for LST extraction', value=default_start_date, min_value=min_date,disabled=st.session_state.gray)
end_date = st.sidebar.date_input('Select the end date for LST extraction', value=default_end_date, min_value=start_date,disabled=st.session_state.gray)
start_hour = st.sidebar.slider('Select start hour of time slot', 0, 23, 6,disabled=st.session_state.gray)
end_hour = st.sidebar.slider('Select end hour of time slot', 0, 24, 20,disabled=st.session_state.gray)
time_difference_gmt = st.sidebar.slider('Enter the time difference when compared to GMT, in hours', -12, 12, 1,disabled=st.session_state.gray)



########################################### Main program ########################################################################

# Set the size of the expander, otherwise it takes the whole page
st.markdown("""
    <style>
        iframe {
            height: 500px !important;
        }
    </style>
    """, unsafe_allow_html=True)

# Create the map
m = folium.Map(location=(1,20), zoom_start=3,width=800,height=500) 
Draw().add_to(m)

st.session_state.first_map = m


# This allow to hide the map when some button is pressed
with st.expander("Draw a zone", st.session_state.expanded,icon=":material/draw:"):
    output = st_folium(st.session_state.first_map, width=800, height=500)

# To know what has been selected by the user and the drawing tool
if 'last_active_drawing' in output and output['last_active_drawing'] is not None:
    last_drawing = output['last_active_drawing']
    if 'geometry' in last_drawing:
        geometry_type = last_drawing['geometry']['type']
        if geometry_type == 'Polygon':
            # Extract coordinates of the drawn polygon
            coordinates = last_drawing['geometry']['coordinates']
          
            epsg_code = get_epsg_from_rectangle(coordinates[0])
            # city = update_location_info(coordinates=coordinates[0])
            
            st.session_state.epsg_location = epsg_code
            # st.session_state.city = city 
            

            # Convert the coordinates to ee.Geometry
            ee_geometry = ee.Geometry.Polygon(coordinates)
            if "geometry" not in st.session_state:
                st.session_state.geometry = ee_geometry
            if ee_geometry != st.session_state.geometry:
                print("i am here")
                st.session_state.geometry = ee_geometry
                callback_stop_export() 
        
            # Get the center and zoom of the map for the second one to be focus on the good area
            center, zoom = get_geometry_center_and_zoom(ee_geometry)

            m_geemap = geemap.Map(center=center, zoom=zoom)
            m_geemap.add_basemap(basemap=basemap)

            # Extract the data and return the map with LST visualisation
            m_geemap, folder = extract_data(    
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
            st.session_state.second_map = m_geemap
            # Display the map in case data has been extracted
            if st.session_state.data:
                print(folder)
                st.session_state.second_map.to_streamlit()
                col1, col2, col3, col4= st.columns(4)
                
                # Two buttons to launch or stop the export
                with col2:
                    st.button("Launch exports",on_click=callback_map)

                with col3:
                    st.button("Stop", on_click=callback_stop_export)
                
                # Launch the export under cetain conditions
                st.session_state.exported_but_not_downloaded = 0
                if st.session_state.button and st.session_state.end:
                    # The task manager function is responsible for the export
                    task_manager()
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
                    st.text_input("Folder path", key='input_path',value=st.session_state.input_path, on_change=update_file_path)
                    st.button("Download folder",on_click = callback_download)
                    st.session_state.extracted_but_not_downloaded = 1     
                    
                    # If the button has been clicked, then the get_file_from_drive function is running, so the download is processed
                    if st.session_state.download:
                        
                        print("All the files are going to be downloaded")
                        get_files_from_drive(path=st.session_state.folder_path,folder_name=folder)
                        print("Everyting done")
                        st.session_state.download = 0
                        st.session_state.downoloaded_but_not_reset = 1
                        st.success("Everything has been downloaded")

                    # Keep in mind the download informations even if the page is reload because of whatever move done by the user on it
                    elif st.session_state.downoloaded_but_not_reset:
                        progress_text=f"The download is done - {100}%"
                        st.progress(100, text=progress_text)
                        st.write(st.session_state.task_text_list_downloaded)
                        st.success("Everything has been downloaded")
                    
                    
                        
