from utils.imports import *
from utils.variables import GEE_PROJECT, CREDENTIALS_PATH


def initialize_earth_engine():
    """
    Initializes the Earth Engine API.

    Attempts to authenticate with Earth Engine using `ee.Authenticate()`.
    Reads the Earth Engine project configuration from file defined by `GEE_PROJECT`.
    Initializes Earth Engine with the project configuration.

    If an `ee.ee_exception.EEException` occurs during any of these steps,
    attempts to re-authenticate and re-initialize.

    Raises:
        ee.ee_exception.EEException: If initialization or re-initialization fails.

    """
    try:
        # Attempt to authenticate and initialize Earth Engine
        ee.Authenticate()

        # Read the Earth Engine project configuration from file again
        project_name = get_project_name()
        ee.Initialize(project=project_name)
        
    except ee.ee_exception.EEException as e:
        print("An Earth Engine exception occurred during initialization:", e)
        # Handle the exception and attempt re-authentication and re-initialization
        reinitialize_earth_engine()


def reinitialize_earth_engine():
    """
    Re-initializes the Earth Engine API.

    Forces re-authentication with Earth Engine using `ee.Authenticate(force=True)`.
    Reads the Earth Engine project configuration from file defined by `GEE_PROJECT` again.
    Initializes Earth Engine with the project configuration.

    If an `ee.ee_exception.EEException` occurs during any of these steps,
    logs the error message and does not retry.

    Raises:
        ee.ee_exception.EEException: If re-initialization fails.

    """
    try:
        # Force re-authentication
        ee.Authenticate(force=True)
        
        
        # Read the Earth Engine project configuration from file again
        project_name = get_project_name()

        ee.Initialize(project=project_name)
        
    except ee.ee_exception.EEException as e:
        print("An Earth Engine exception occurred during re-initialization:", e)
        # Handle the exception as needed, such as logging or retrying

def get_project_name():
    with open(CREDENTIALS_PATH, 'r') as f:
            config = json.load(f)

    return config["installed"]['project_id']
    
