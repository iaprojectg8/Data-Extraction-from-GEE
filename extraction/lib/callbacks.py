from utils.imports import *
from lib.helpers import get_python_executable_name


######################################### Export callbacks

def callback_launch():
    """
    Callback function to update session state variables when the "Launch" button is clicked.
    This is just to specify that the button is on and that the first map should not be 
    expanded anymore
    Args: 
        None
    Returns:
        None
    """

    st.session_state.expanded = 0
    st.session_state.button = 1
    st.session_state.extracted_but_not_downloaded = 0
    st.session_state.downloaded_but_not_reset = 0
    st.session_state.gray = 1


def callback_stop_export():
    """
    Callback function to reinitialize session state variables.
    """
    st.session_state.expanded = 1
    st.session_state.button = 0
    st.session_state.end =  1
    st.session_state.export_done = 0
    st.session_state.extracted_but_not_downloaded = 0
    st.session_state.downloaded_but_not_reset = 0
    st.session_state.gray = 0
    

######################################### Download callbacks

def callback_download():
    """
    Callback to reset the session variables that where used before to downlaod the files
    """
    st.session_state.download = 1
    st.session_state.gray = 0


def update_file_path():
    """
    Function to update the folder path to download the drive files, when the user update it
    Args: 
        None
    Returns:
        None
    """
    st.session_state.folder_path = st.session_state.input_path


######################################### Conversion callbacks


def callback_click():
    """
    Callback on the click of the CSV conversion button. It allows to launch the script of 
    pyqgis which makes the conversion with an algorithm through a subprocess
    """
    st.session_state.launched = 1
    st.session_state.kill=0
    
    # Assign a subprocess Popen to a session variable
    st.session_state.process = subprocess.Popen(
            [f"{get_python_executable_name()}", 'pyqgis/csv_converter.py',f"{st.session_state.complete_folder_path}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True  # This makes sure the output is read as text instead of bytes
        )


def callback_kill():
    """
    Callback on the click of the Stop CSV conversion button. It kills the subprocess and reset 
    the session variables
    """
    st.session_state.kill = 1
    st.session_state.launched = 0
    st.session_state.process.terminate()