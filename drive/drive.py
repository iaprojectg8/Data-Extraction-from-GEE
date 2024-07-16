from utils.imports import *
from utils.variables import *

def get_credentials():
    """
    Get user credentials for Google Drive API. Then put the file resulting content in the json file token.json

    Returns:
        Credentials: Authenticated user credentials.
    """
    creds = None
    # If the token.json exists, then we reuse it
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPE)
    
    if not creds or not creds.valid:
        # In case credentials exist in token.json but are not valid, the token is refreshed
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())       
            print("Token refreshed")     
        else:
            # Otherwise we need to reconnect to the google account, with the file credentials.json provided when we create a OAuth client on the cloud
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPE)
            creds = flow.run_local_server(port=0)
            print("Token recreated")
        # If the creds are not valid it updates them in token.json
        with open(TOKEN_PATH, "w") as token:
            token.write(creds.to_json())
    print("Token still valid")
    
    return creds

def handling_creds():
  """
    It can happen that whatever how the creds can be loaded from the token.json, even with the condition that we put. 
    So we decided to create a function that deletes the token.json in case there is a weird exception, and then 
    call again the get_credentials method to recreate it.

    Returns:
        Credentials: Authenticated user credentials.
    """
  creds_ok = 0
  while not creds_ok:
    try:
      # Try to laod or create the credentials
      creds = get_credentials()
      creds_ok = 1

    # In case of error it removes the file token.json that contains the token 
    except RefreshError as e:
        print(f"Error in main program: {e}")
        print("We will try to reconnect you to your google account to recreate the credentials")
        try:
            os.remove(TOKEN_PATH)
            print(f"File '{TOKEN_PATH}' successfully deleted.")
            creds = get_credentials()
            creds_ok = 1
        except OSError as e:
            print(f"Error deleting file '{TOKEN_PATH}': {e}")
  return creds


def list_folders(service):
    """
    List all folders in Google Drive.

    Args:
        service: Authorized Drive API service instance.

    Returns:
        list: List of folder items.
    """
    # Make the request to get the folders name and their id 
    try:
        results = service.files().list(
            q="mimeType = 'application/vnd.google-apps.folder'",
            spaces="drive",
            fields="nextPageToken, files(id, name)"
        ).execute()

        # Take only the field files, where lies the folders name and id
        items = results.get("files", [])
        return items
    except HttpError as error:
        print(f"An error occurred: {error}")
        return []
    

def list_files(service, folder_id):
    """
    List all files in a specific folder in Google Drive.

    Args:
        service: Authorized Drive API service instance.
        folder_id (str): ID of the folder to list files from.

    Returns:
        list: List of file items.
    """
    try:
        # Here the request is made
        results = service.files().list(
            q=f"'{folder_id}' in parents",
            spaces="drive",
            fields="nextPageToken, files(id , name)"
        ).execute()

        # Only the file fields is taken from the request
        items = results.get("files", [])
        return items
    except HttpError as error:
        print(f"An error occurred: {error}")
        return []
    
def get_folder_id(items, UHI_name):
    """
    Get the ID of a folder with the specified name from a list of items.

    Args:
        items (list): List containing dictionaries of folder name and id.
        UHI_name (str): Name of the folder to find.

    Returns:
        str: ID of the folder if found, None if not found.
    """
    for item in items:
        if item["name"] == UHI_name:
            return item["id"]
    return None

def download_files(service, files, download_path):
    """Download files from Google Drive.

    Args:
        service: Authorized Drive API service instance.
        files: List of files to download, each file should be a dict with 'id' and 'name'.
        download_path: Path to the directory where files will be downloaded.
    """

    # Create the destination folder if it does not exist
    if not os.path.exists(download_path):
        os.makedirs(download_path)

    with st.spinner("Downloading files"):
        progress_text=f"The export is ongoing - {0}%"
        progress_bar = st.progress(0, text=progress_text)
        task_description_list = []
        writer = st.empty()
        for i,file in enumerate(files):
            
            # Initialize the request and the local file path
            file_id = file['id']
            file_name = file['name']
            name = "_".join(file_name.split("_")[:-1])
            print(name)
            task_description_list.append(name)
            print(task_description_list)
            st.session_state.task_text_list_downloaded = " - ".join(task_description_list)
            writer.write(st.session_state.task_text_list_downloaded)
            request = service.files().get_media(fileId=file_id)
            file_path = os.path.join(download_path, file_name)
            
            # Open the local file to write the drive file into it
            with open(file_path, 'wb') as f:
                downloader = MediaIoBaseDownload(f, request)
                done = False
                while done is False:
                    status, done = downloader.next_chunk()
                    # Display the status of the download to the user
                    print(f"Downloading {file_name}: {int(status.progress() * 100)}%")
            print(f"Downloaded {file_name} to {file_path}")
            percent = (i+1) / len(files)
            progress_text=f"The export is ongoing - {round(percent*100,1)}%"
            progress_bar.progress(percent, text=progress_text)




def get_files_from_drive(path,folder_name):
    """Main function to print the names and ids of folders in Google Drive."""
    
    # Handling credentials
    print("Handling creds")
    creds = handling_creds()

    # Path init to save the downloaded file
    folder_name = folder_name  # Then this should not be hard coded because it will be the name of the folder created when exported during the extraction
    folder_path = os.path.join(path, folder_name)
    print(folder_path)
    
    # Create the receiving data folder if it does not exist
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # Create a sevice object that allows the client to communicate with the google platform
    print("Create the service")
    service = build("drive", "v3", credentials=creds)
    
    # Get all the folders on the drive account provided by the credentials
    print("Get the whole folder list")
    folders = list_folders(service)
    if not folders:
        print("No folders found.")
        return
    
    # Get the files in the folder
    print("Get the speceific folder and download the files")
    folder_id = get_folder_id(folders, folder_name)
    files_list = list_files(service=service, folder_id=folder_id)
    service = build("drive", "v3", credentials=creds)

    # Finally download the file in the requested drive folder
    download_files(service=service, files=files_list, download_path=folder_path)
    print("All the file downloaded")