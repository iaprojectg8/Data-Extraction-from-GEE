import os 

def get_python_qgis():
    """
    This function is very useful because it gets the path of the python executable
    for qgis without having to declare it into a file. The user just needs to follow
    the README and to declare the Path variable correctly and everything should be ok.
    Returns:
        path (str): The path corresponding to the python executable for QGIS
    """
    # Get the PATH variable
    path_variables = os.environ.get("PATH")
    paths = path_variables.split(os.pathsep)

    # Looking for the corresponding path
    for path in paths:
        lower_path = path.lower()
        if "osgeo4w" in lower_path and "python312" in lower_path and "pythonq" in lower_path:
            print(path)
            return path
        
        elif "osgeo4w" in lower_path and "python39" in lower_path and "pythonq":
            return path
            