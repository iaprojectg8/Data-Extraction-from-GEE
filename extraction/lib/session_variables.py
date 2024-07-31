from utils.imports import *
from utils.variables import *


########################################## Manage maps ########################################################################

# Session variable to store the first map
if "first_map" not in st.session_state:
    st.session_state.first_map = None

# Session variable to store the second map
if "second_map" not in st.session_state:
    st.session_state.second_map = None


################################################ Manage export #################################################################

# Session variable to know if the user clicked on the button. If so the variable will be 1 else 0
if "button" not in st.session_state:
    st.session_state.button = 0

# Session variable to know if the task manager is finished. If so the variable will be 1 else 0, it means the task manager currently working
if "end" not in st.session_state:
    st.session_state.end = 1

# Session varialbe to display information if the export has been completed
if "export_done" not in st.session_state:
    st.session_state.export_done = 0

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
    st.session_state.epsg_location = 0

if "name_area" not in st.session_state:
    st.session_state.name_area = "No data"


################################################ Manage download  #################################################################

# Session variable to know when the download button has been clicked and then enter an if statement to launch the downloading from the drive
if "download" not in st.session_state:
    st.session_state.download = 0

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
if "downloaded_but_not_reset" not in st.session_state:
    st.session_state.downloaded_but_not_reset = 0

# Session variable to track the folder path for the download
if "folder_path" not in st.session_state:
    st.session_state.folder_path = PATH

# Session variable update the folder path when it is changed in the text input
if 'input_path' not in st.session_state:
    st.session_state.input_path = PATH

# Session variable that allows to gray all the parameters on the left side
if "gray" not in st.session_state:
    st.session_state.gray = 0

# Session variable that keep in mind the export, and so it shows the button to download them
if "extracted_but_not_downloaded" not in st.session_state:
    st.session_state.extracted_but_not_downloaded = 0


########################################### Manage conversion ##################################################################

# Session variable to store the progress in the last step, the CSV conversion
if "progress" not in st.session_state:
    st.session_state.progress = 0

# Session variable to store the current entire downloaded folder
if "complete_folder_path" not in st.session_state:
    st.session_state.complete_folder_path = ""

# Session variable to know if the CSV conversion has stated
if "launched" not in st.session_state:
    st.session_state.launched = 0

# Session variable to know if the CSV conversion has been killed    
if "kill" not in st.session_state:
    st.session_state.kill = 0

# Session variable to know if the user clicked on the converter button. If so the variable will be 1 else 0
if "button_converter" not in st.session_state:
    st.session_state.button_converter = 0