from utils.imports import *
from drive.drive import  get_files_from_drive
from lib.callbacks import *
from utils.variables import DOWNLOAD_PATH


######################################### Export widget

def display_export_progress():
    """
    Function to display the export process done. It is just useful in case the user touch the first map, 
    when the export is done but the download is not. In that way the user does not have to export the 
    same data again.
    """
    if st.session_state.extracted_but_not_downloaded:
        progress_text=f"The export is done - {100}%"
        st.progress(100, text=progress_text)
        st.write(st.session_state.task_text_list)
    st.success('All the tasks exported')


def organize_export_button():
    """
    Function that organizes the display of the export buttons and manages them as well
    """
    col1, col2, col3, col4= st.columns(4)
    
    # Two buttons to launch or stop the export
    with col2:
        st.button("Launch exports",on_click=callback_launch)

    with col3:
        st.button("Stop", on_click=callback_stop_export)
    
    # Launch the export under cetain conditions
    st.session_state.exported_but_not_downloaded = 0


######################################### Download widget

def organize_download_button():
    """
    Function that organizes the display of the download buttons and manages them as well
    """
    # Widget for the download
    col1, col2 = st.columns([1.2,0.20],gap="small", vertical_alignment="bottom")  # Adjust the column widths as needed
    with col1:
        st.text_input("Folder path", key='input_path',value=st.session_state.input_path, on_change=update_file_path)
        
    with col2:
        st.button("Save path", on_click=save_download_path)

    st.button("Download folder", on_click=callback_download)
    st.session_state.extracted_but_not_downloaded = 1

def save_download_path():
    """
    Open the download_path.txt file to change the path if requested (button clicked)
    """
    with open(DOWNLOAD_PATH, "w") as f:
        f.write(st.session_state.input_path)


def download(folder):
    """
    Function to download all the files that has been exported, from the drive.
    
    Args:
        folder (str): Folder name on which we need to go to get the data
    """
    print("All the files are going to be downloaded")
    get_files_from_drive(path=st.session_state.folder_path,folder_name=folder)
    print("Everyting done")
    st.session_state.download = 0
    st.session_state.downloaded_but_not_reset = 1
    st.success("Everything has been downloaded")


def display_download():
    """
    Function to display the download process done. It is just useful in case the user touch the first map, 
    when the donwload is done but the conversion is not
    """
    progress_text=f"The download is done - {100}%"
    st.progress(100, text=progress_text)
    st.write(st.session_state.task_text_list_downloaded)
    st.success("Everything has been downloaded")


######################################### Conversion widget


def organize_conversion_button():
    """
    Function which manages everything that happens when clicking on the buttons
    """
    # Create a Streamlit progress bar
    if st.session_state.kill :
        progress = st.session_state.progress
        progress_text =f"The conversion has been stopped: {progress}%"
        progress_bar = st.progress(progress, progress_text)
    
    # Manage the button and the corresponding callback
    col1, col2, col3, col4= st.columns(4)
    with col2:
        st.button("Convert to CSV", on_click=callback_click)
    with col3:
        st.button("Stop CSV conversion", on_click=callback_kill)

    # Initialize the progress bar
    if st.session_state.launched:
        progress = 0
        progress_text =f"The conversion is not started: {0}%"
        progress_bar = st.progress(progress, progress_text)

        # Read progress updates from the subprocess
        while st.session_state.process.poll() is None:
            text_step = ""
            
            # Get the printed output of the subprocess and select the interesting ones to give informations to the user
            for line in st.session_state.process.stdout:
                
                if line.startswith("PROGRESS:"):
                    progress=round(float(line.split(":")[-1])*100)
                    st.session_state.progress = progress
                    

                elif line.startswith("INFO:"):
                    text_step = line.split(":")[-1]

                # Allows to have the information text on a good timing
                progress_text =f"The conversion is ongoing: {progress}% - {text_step}"
                progress_bar.progress(progress,text=progress_text)
        
                print(line)
             
    # Display the result of the conversion as success or error if the user killed the process
    if st.session_state.launched == 1 and st.session_state.process.poll() == 0:
        st.session_state.launched = 0
        st.success("The CSV file is ready")
    elif st.session_state.kill == 1 and st.session_state.process.poll() == 1:
        st.session_state.kill = 0
        st.error("You stopped the conversion process")