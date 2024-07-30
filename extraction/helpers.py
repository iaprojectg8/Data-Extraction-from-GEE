from utils.imports import *
from utils.variables import GEE_PROJECT, DOWNLOAD_PATH, PYTHON_EXECUTABLE_PATH, LOGO_PATH
from drive.drive import does_folder_exist_on_drive, get_files_from_drive


def display_download():
    progress_text=f"The download is done - {100}%"
    st.progress(100, text=progress_text)
    st.write(st.session_state.task_text_list_downloaded)
    st.success("Everything has been downloaded")

def download(folder):
    print("All the files are going to be downloaded")
    get_files_from_drive(path=st.session_state.folder_path,folder_name=folder)
    print("Everyting done")
    st.session_state.download = 0
    st.session_state.downloaded_but_not_reset = 1
    st.success("Everything has been downloaded")


def organize_download_button():
    # Widget for the download
    col1, col2 = st.columns([1.2,0.20],gap="small", vertical_alignment="bottom")  # Adjust the column widths as needed
    with col1:
        st.text_input("Folder path", key='input_path',value=st.session_state.input_path, on_change=update_file_path)
        
    with col2:
        st.button("Save path", on_click=save_path)

    st.button("Download folder", on_click=callback_download)
    st.session_state.extracted_but_not_downloaded = 1 

def display_export_progress():
    if st.session_state.extracted_but_not_downloaded:
        progress_text=f"The export is done - {100}%"
        st.progress(100, text=progress_text)
        st.write(st.session_state.task_text_list)
    st.success('All the tasks exported')


def organize_export_button():
    col1, col2, col3, col4= st.columns(4)
    
    # Two buttons to launch or stop the export
    with col2:
        st.button("Launch exports",on_click=callback_launch)

    with col3:
        st.button("Stop", on_click=callback_stop_export)
    
    # Launch the export under cetain conditions
    st.session_state.exported_but_not_downloaded = 0


def get_ee_geometry(geometry):
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
    return ee_geometry


def fill_geometry(output):
    # i am going to try to make a function with this part
    if 'last_active_drawing' in output and output['last_active_drawing'] is not None :
        last_drawing = output['last_active_drawing']
        if 'geometry' in last_drawing :
            geometry = last_drawing["geometry"]
   
    elif "shape" in output :
        shape = output["shape"]["features"][0]
        geometry = shape["geometry"]

    return output, geometry




def restrict_iframe():
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


def map_expander(json_gdf):
    # This allow to hide the map when some button is pressed
    with st.expander("Draw a zone", st.session_state.expanded,icon=":material/draw:"):
        output = st_folium(st.session_state.first_map, use_container_width=True)

        if json_gdf:
            output["shape"] = json_gdf
        
        return output
        


def map_initialization():
    m = folium.Map(location=(1,20), zoom_start=3) 
    Draw().add_to(m)
    st.session_state.first_map = m
    return m



def file_uploader():
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


def put_logo_if_possible():
    with open(LOGO_PATH, "rb") as file:
        svg_content = file.read()
    st.set_page_config(page_title="Data Extraction",page_icon=svg_content)
    st.title("Data Extraction")

def get_geometry_center_and_zoom_json(coordinates):
    """
    Function to estimate center and zoom level from a GeoJSON geometry.
    
    Args: 
        geojson_geometry (dict): GeoJSON geometry object.
        
    Returns:
        tuple: Tuple containing estimated center coordinates and zoom level.
    """

    # Calculate the bounds of the geometry
    lon_min = min([point[0] for point in coordinates])
    lon_max = max([point[0] for point in coordinates])
    lat_min = min([point[1] for point in coordinates])
    lat_max = max([point[1] for point in coordinates])

    # Calculate the center of the geometry
    lon_center = (lon_min + lon_max) / 2
    lat_center = (lat_min + lat_max) / 2

    # Estimate zoom level based on the extent of the geometry
    lon_extent = lon_max - lon_min
    lat_extent = lat_max - lat_min
    extent = max(lon_extent, lat_extent)

    # Convert extent to a zoom level
    if extent > 0:
        zoom = min(max(1, int(round(9 - math.log(extent, 2)))), 20)
    else:
        zoom = 8  # Default zoom level if extent is zero

    center = [lat_center, lon_center]

    return center, zoom

def get_gdf_zoom(gdf):
    """
    Function to estimate center and zoom level based on the bounding box of geometries
    in a GeoDataFrame.

    Args:
        gdf (geopandas.GeoDataFrame): GeoDataFrame containing geometries.

    Returns:
        tuple: Tuple containing estimated center coordinates and zoom level.
    """
    # Calculate the bounds of the geometries
    bounds = gdf.total_bounds
    lon_min, lat_min, lon_max, lat_max = bounds

    # Calculate the center of the bounding box
    lon_center = (lon_min + lon_max) / 2
    lat_center = (lat_min + lat_max) / 2

    # Estimate zoom level based on the extent of the bounding box
    lon_extent = lon_max - lon_min
    lat_extent = lat_max - lat_min
    extent = max(lon_extent, lat_extent)

    # Convert extent to a zoom level
    # Adjust zoom level calculation based on the extent
    if extent > 0:
        zoom = min(max(1, int(round(9 - math.log(extent, 2)))), 20)
    else:
        zoom = 8  # Default zoom level if extent is zero

    center = [lat_center, lon_center]

    return  zoom


def load_shapefile(uploaded_files):
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

def callback_click():
    st.session_state.launched = 1
    st.session_state.kill=0
    print(st.session_state.complete_folder_path)
    st.session_state.process = subprocess.Popen(
            [f"{get_python_executable_name()}", 'pyqgis/csv_converter.py',f"{st.session_state.complete_folder_path}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True  # This makes sure the output is read as text instead of bytes
        )

def callback_kill():
    st.session_state.kill = 1
    st.session_state.launched = 0
    st.session_state.process.terminate()
    

def convert_to_csv():

    # Create a Streamlit progress bar

    if st.session_state.kill :
        progress = st.session_state.progress
        progress_text =f"The conversion has been stopped: {progress}%"
        progress_bar = st.progress(progress, progress_text)
    # else  :
    #     progress = 0
    #     progress_text =f"The conversion is not started: {0}%"
    #     progress_bar = st.progress(progress, progress_text)
    
    col1, col2, col3, col4= st.columns(4)
    with col2:
        st.button("Convert to CSV", on_click=callback_click)
    with col3:
        st.button("Stop CSV convertion", on_click=callback_kill)
        # Launch subprocess with a timeout
    if st.session_state.launched:
        progress = 0
        progress_text =f"The conversion is not started: {0}%"
        progress_bar = st.progress(progress, progress_text)

        # Read progress updates from the subprocess
        while st.session_state.process.poll() is None:
            text_step = ""
            
            for line in st.session_state.process.stdout:
                

                
                if line.startswith("PROGRESS:"):
                    progress=round(float(line.split(":")[-1])*100)
                    st.session_state.progress = progress
                    progress_text =f"The conversion is ongoing: {progress}% - {text_step}"
                    progress_bar.progress(progress,text=progress_text)


                ### A tester en revenant de manger
                elif line.startswith("INFO:"):
                    text_step = line.split(":")[-1]
                    
                    
                print(line)
             

    if st.session_state.launched == 1 and st.session_state.process.poll() == 0:
        st.session_state.launched = 0
        st.success("The CSV file is ready")
    elif st.session_state.kill == 1 and st.session_state.process.poll() == 1:
        st.session_state.kill = 0
        st.error("You stopped the conversion process")
        


def callback_convert():
    st.session_state.button_converter = 1
    st.session_state.expanded = 0
    st.session_state.gray = 1


def callback_stop_converter():
    st.session_state.button_converter = 0
    st.session_state.expanded = 1
    st.session_state.gray = 0


def save_path():
    """
    Open the download_path.txt file to change the path if requested (button clicked)

    """
    with open(DOWNLOAD_PATH, "w") as f:
        f.write(st.session_state.input_path)


def get_python_executable_name():
    with open(PYTHON_EXECUTABLE_PATH, 'r') as f:
        config = json.load(f)
        python_executable_name = config["python_name"]
    return python_executable_name


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
        
        # Read the Earth Engine project configuration from file
        with open(GEE_PROJECT, 'r') as f:
            config = json.load(f)

        ee.Initialize(project=config["project"])
        
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
        with open(GEE_PROJECT, 'r') as f:
            config = json.load(f)

        ee.Initialize(project=config["project"])
        
    except ee.ee_exception.EEException as e:
        print("An Earth Engine exception occurred during re-initialization:", e)
        # Handle the exception as needed, such as logging or retrying

def update_file_path():
    """
    Function to update the folder path to download the drive files, when the user update it
    Args: 
        None
    Returns:
        None
    """
    st.session_state.folder_path = st.session_state.input_path


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
    



def callback_download():
    """
    Callback to reset the session variables that where used before to downlaod the files
    Args: 
        None
    Returns:
        None
    """
    st.session_state.download = 1
    st.session_state.gray = 0

def callback_stop_export():
    """
    Callback function to reinitialize session state variables.
    Args: 
        None
    Returns:
        None
    """
    st.session_state.expanded = 1
    st.session_state.button = 0
    st.session_state.end =  1
    st.session_state.export_done = 0
    st.session_state.extracted_but_not_downloaded = 0
    st.session_state.downloaded_but_not_reset = 0
    st.session_state.gray = 0

def update_location_info(coordinates):
    """
    Returns the name of the city based on the provided coordinates

    Args:
    rectangle_coords (list): List of tuples representing the (longitude, latitude) coordinates of the rectangle's corners.

    Returns:
    str: The name of the city, or None
    """
    polygon = Polygon(coordinates)
    centroid = polygon.centroid
    print(centroid)
    # Perform reverse geocoding
    url = f"https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat={centroid.y}&lon={centroid.x}"
    response = requests.get(url)
    data = response.json()
    print(data)
    if "address" in data:
        if "city" in data["address"]:
            city = data["address"]["city"]
            return city
        elif "county" in data["address"]:
            return data["address"]["county"]
    else:
        return None


def get_utm_epsg(lat, lon):
    """
    Returns the EPSG code for the UTM zone based on the given latitude and longitude.

    Args:
    lat (float): Latitude of the point.
    lon (float): Longitude of the point.

    Returns:
    int: EPSG code for the UTM zone.
    """
    zone_number = math.floor((lon + 180) / 6) + 1

    if lat >= 0:
        epsg_code = f"326{zone_number:02d}"  # Northern Hemisphere
    else:
        epsg_code = f"327{zone_number:02d}"  # Southern Hemisphere
    
    return int(epsg_code)

def get_epsg_from_polygon(polygon_coordinates):
    """
    Returns the EPSG code for the UTM zone based on the centroid of the given rectangle coordinates.

    Args:
    rectangle_coords (list): List of tuples representing the (longitude, latitude) coordinates of the rectangle's corners.

    Returns:
    int: EPSG code for the UTM zone.
    """
    # Create a polygon from the rectangle coordinates
    polygon = Polygon(polygon_coordinates)
    centroid = polygon.centroid
    
    # Get the EPSG code for the UTM zone of the centroid
    epsg_code = get_utm_epsg(centroid.y, centroid.x)
    
    return epsg_code



def task_manager(folder_existance):
    """
    Function to manage tasks. Everything is done with session state variable, this is why there is not 
    any parameter or return. This goes when the "Launch button is activated, the task are successively
    launched one by one. This function contains a lot of displayings for the user to know the progress 
    of the different tasks.
    Args: 
        None
    Returns:
        None
    """
    if st.session_state.task_list !=[]:
        st.session_state.end = 0
        with st.spinner("Export in process"):
            progress_text=f"The export is ongoing - {0}%"
            progress_bar = st.progress(0, text=progress_text)
            task_description_list = []
            writer = st.empty()
            task_list = st.session_state.task_list
            for i, task in enumerate(task_list):
                print("Task", task.config["description"])
                if not task.active() :
                    
                    # Launch the task
                    if not folder_existance:
                        task.start()
                    else:
                        time.sleep(0.5)
                    task_description = get_task_description(task, folder_existance)
                    task_description_list.append(task_description)
                    st.session_state.task_text_list = " - ".join(task_description_list)
                    writer.write(st.session_state.task_text_list)
                    print(f"{task_description} starts")
                    if not folder_existance:   
                        check_task_status(task)
                    print(f"{task_description} ends")

                    

                percent = (i+1) / len(task_list)
                progress_text=f"The export is ongoing - {percent*100}%"
                progress_bar.progress(percent, text=progress_text)
                
        

            print("All the tasks have been done")
            # Reinitialization of variables, as if it has stopped
            st.session_state.expanded = 1
            st.session_state.button = 0
            st.session_state.end = 1
        
        # a message to notify that everything goes well 
        

def get_task_description(task,folder_existance):
    """
    Function to get the name of the processing task.
    Args: 
        task (object): Task object representing a task in Earth Engine.
    Returns:
        str: Formatted description of the task.
    """


    if folder_existance:
        if  "_" in task.config["description"]:
            task_description_list = task.config["description"].split("_")
            task_description = " ".join(task_description_list[:-1])
        else:
            task_description = task.status()["description"]
    else:
        if  "_" in task.status()["description"]:
            task_description_list = task.status()["description"].split("_")
            task_description = " ".join(task_description_list[:-1])
        else:
            task_description = task.status()["description"]

    return task_description


def apply_scale_factors(image:ee.Image):
    """
    Function to apply scale factors to an Earth Engine image.
    Args: 
        image (ee.Image): Earth Engine image object.
    Returns:
        ee.Image: Image with scale factors applied.
    """
    optical_bands = image.select('SR_B.').multiply(0.0000275).add(-0.2)
    thermal_bands = image.select('ST_B.*').multiply(0.00341802).add(149.0).subtract(273)
    return image.addBands(optical_bands, None, True).addBands(thermal_bands, None, True)

def add_hours(start, dec):
    """
    Function to add hours modulo 24.
    Args: 
        start (str or int): Starting hour as a string or integer.
        dec (str or int): Hour to be added as a string or integer.
    Returns:
        ee.Number: Resulting hour modulo 24.
    """
    start_hour_number = ee.Number.parse(start)
    dec_hour_number = ee.Number.parse(dec)
    real_start = start_hour_number.add(dec_hour_number).mod(24)
    return real_start

def check_task_status(task):
    """
    Function to continuously check the status of a task.
    Args: 
        task (object): Task object representing a task in Earth Engine.
    Returns:
        None
    """
    while task.active() :
        status = task.status()["state"]
        if st.session_state.status != status:
            print('State:', status)
            st.session_state.status = status

def compute_band_min_max(img, region):
    """
    Function to compute minimum and maximum values of a band in an image over a region.
    Args: 
        img (ee.Image): Earth Engine image object.
        band (str): Name of the band to compute min and max values.
        region (ee.Geometry): Earth Engine geometry object representing the region of interest.
    Returns:
        dict: Dictionary containing computed minimum and maximum values.
    """        
    stats = img.reduceRegion(
        reducer=ee.Reducer.minMax(),
        geometry=region,
        scale=30,
        maxPixels=1e13
    )
    return stats

def get_geometry_center_and_zoom(geometry):
    """
    Function to estimate center and zoom level, for the second map, from the clipping that 
    the user made on the first map
    Args: 
        geometry (ee.Geometry): Earth Engine geometry object.
    Returns:
        tuple: Tuple containing estimated center coordinates and zoom level.
    """
    # Calculate the bounds of the geometry
    bounds = geometry.bounds().getInfo()['coordinates'][0]
    lon_min = min([point[0] for point in bounds])
    lon_max = max([point[0] for point in bounds])
    lat_min = min([point[1] for point in bounds])
    lat_max = max([point[1] for point in bounds])

    # Calculate the center of the geometry
    lon_center = (lon_min + lon_max) / 2
    lat_center = (lat_min + lat_max) / 2

    # Estimate zoom level based on the extent of the geometry
    lon_extent = lon_max - lon_min
    lat_extent = lat_max - lat_min
    extent = max(lon_extent, lat_extent)

    # Convert extent to a zoom level
    # Something find by the Cat 
    if extent > 0:
        zoom = min(max(1, int(round(9 - math.log(extent, 2)))), 20)
    else:
        zoom = 8  # Default zoom level if extent is zero
    center = [lat_center, lon_center]

    return center, zoom


def first_calculate_coverage(image:ee.Image, aoi:ee.geometry):

    """
    Function to calculate the coverage of the temperature band among the aoi. This is very useful
    to filter among a lot of images that have only a little part of temperature band, but the user does not care.
    Args: 
        image (ee.Image) : An image from the merged image collection between the both landsat 8 and landsat 9
        aoi (ee.Geometry): The AOI from the drawing of the user
    Returns:
        image (ee.Image) : An image containing a new parameter, which is coverage_percentage
    """
    # Clip the image to the AOI and get the geometry to compare the remaining image with the AOI
    image_area = image.clip(aoi).geometry().area()
    aoi_area = aoi.area()
    
    # Calculate the coverage percentage
    coverage_percentage = ee.Number(image_area).divide(ee.Number(aoi_area))
    
    # Add the coverage percentage as a property to the image
    return image.set('coverage_percentage', coverage_percentage)
    

def calculate_coverage(image:ee.Image, aoi:ee.geometry):

    """
    Function to calculate the coverage of the temperature band among the aoi. This is very useful
    to filter among a lot of images that have only a little part of temperature band, but the user does not care.
    Args: 
        image (ee.Image) : An image from the merged image collection between the both landsat 8 and landsat 9
        aoi (ee.Geometry): The AOI from the drawing of the user
    Returns:
        image (ee.Image) : An image containing a new parameter, which is coverage_percentage
    """

    temp_area = image.select("temp")
    value = temp_area.reduceRegion(
        reducer=ee.Reducer.toList().count(),
        geometry = aoi,
        scale = 30,
        maxPixels=1e9
    ).get("temp")

    aoi_area = image.pixelArea().reduceRegion(
        reducer = ee.Reducer.count(),
        geometry=aoi,
        scale = 30,
        maxPixels=10e9
    ).get("area")
 
    
    # Calculate the coverage percentage
    coverage_percentage = ee.Number(value).divide(ee.Number(aoi_area))
    
    # Add the coverage percentage as a property to the image
    return image.set('coverage_percentage', coverage_percentage).set("aoi_area",aoi_area).set("temp_image",value)


def extract_data(map:geemap.Map,aoi:ee.geometry, EPSGloc, startdate, enddate, starthour, endhour, dechour, maxcloud,coverage_threshold, namelbl):
    """
    Extracts and visualizes data from Landsat and other Earth Engine datasets, and exports various layers to Google Drive.

    Args:
        map (geemap.Map): The geemap.Map object for displaying visualizations.
        aoi (ee.Geometry): Earth Engine geometry representing the area of interest.
        EPSGloc (int or str): EPSG code for the projection system.
        startdate (str): Start date for filtering images (format: 'YYYY-MM-DD').
        enddate (str): End date for filtering images (format: 'YYYY-MM-DD').
        starthour (str or int): Starting hour for filtering images (24-hour format).
        endhour (str or int): Ending hour for filtering images (24-hour format).
        dechour (str or int): Hour to be added or subtracted from start/end hour (24-hour format).
        maxcloud (int): Maximum cloud cover percentage for filtering images.
        namelbl (str): Name label used in folder and file names for exporting.

    Returns:
        geemap.Map: The updated geemap.Map object with layers added.
    """

    # Define bands and standard names for Landsat images
    LC89_BANDS = ['SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7', 'ST_B10']
    # LC57_BANDS = ['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B7', 'ST_B6']:
    STD_NAMES = ['blue', 'green', 'red', 'nir', 'swir1', 'swir2', 'temp']
    # Coverage threshold corresponds to the part of the image that exists in the temperature band
    folder = None
    folder_existance = 0
      
    # Extract an image collection from Landsat 8
    imageL8 = ee.ImageCollection("LANDSAT/LC08/C02/T1_L2") \
                .filterBounds(aoi) \
                .filterDate(startdate, enddate) \
                .filter(ee.Filter.lte('CLOUD_COVER_LAND', maxcloud)) \
                .map(apply_scale_factors) \
                .select(LC89_BANDS, STD_NAMES)
    
    # Extract an image collection from Landsat 9 
    imageL9 = ee.ImageCollection("LANDSAT/LC09/C02/T1_L2") \
                .filterBounds(aoi) \
                .filterDate(startdate, enddate) \
                .filter(ee.Filter.lte('CLOUD_COVER_LAND', maxcloud)) \
                .map(apply_scale_factors) \
                .select(LC89_BANDS, STD_NAMES)
    
    # Recalculating the start and end hours depending on where the area is in the world
    real_start_hour = add_hours(starthour, dechour)
    real_end_hour = add_hours(endhour, dechour)

    # Merging all the image collection into a single one, also filtering on the hour
    images_merged = ee.ImageCollection(imageL8.merge(imageL9)) \
                    .filter(ee.Filter.calendarRange(real_start_hour, real_end_hour, "hour"))
    

    ###### Testing the coverage map function here
    coverage_collection = images_merged.map(lambda image : calculate_coverage(image, aoi))
    on_coverage_filtered_collection =  coverage_collection.filter(ee.Filter.gte('coverage_percentage', coverage_threshold/100))
    

    if on_coverage_filtered_collection.size().getInfo() != 0:
        images_list = on_coverage_filtered_collection.toList(on_coverage_filtered_collection.size()).reverse()
        python_list = images_list.getInfo()
        entity_index =dict()
        select_box_list = []
        for i,image in enumerate(python_list):
            
            properties = image["properties"]
            coverage = properties["coverage_percentage"]
            date = properties['DATE_ACQUIRED']
            cloud_cover = properties["CLOUD_COVER"]
            landsat_type = properties["SPACECRAFT_ID"]
            scene_hour = properties["SCENE_CENTER_TIME"].split(".")[0]
            entity = f"Date and time: {date} {scene_hour} | Cloud cover: {round(cloud_cover,2)}% | Coverage: {round(coverage*100,2)}% | {landsat_type}"
            select_box_list.append(entity)
            entity_index[entity] = i
        image_count = images_list.size().getInfo()
        print(image_count)
        entity_chosen = st.selectbox(label=f"Chose an image, {len(python_list)} are available with your parameters",options=select_box_list)
        index = entity_index[entity_chosen]
        
        # # In case the list has more than one element, we can create a slider
        # if image_count>1:
        #     index = st.slider('Select image index', 0, image_count-1, 0)
        # else :
        #     index = image_count-1
            
        # This take the selection made by the user through the slider
        image = ee.Image(images_list.get(index)).clip(aoi)

        # Get information about the image that is printed to know more about it
        date = str(image.getInfo()["properties"]['DATE_ACQUIRED'])
        cloud_cover = str(image.getInfo()["properties"]["CLOUD_COVER"])
        landsat_type = str(image.getInfo()["properties"]["SPACECRAFT_ID"])
        scene_hour = str(image.getInfo()["properties"]["SCENE_CENTER_TIME"]).split(".")[0]
        coverage = float(image.getInfo()["properties"]["coverage_percentage"])
        
        
            
        # Compute min and max LST of the selected area 
        band_min_max = compute_band_min_max(image, aoi)
        temp_min =  band_min_max.getInfo()['temp_min']
        temp_max =  band_min_max.getInfo()['temp_max']

        # Gives information to the user avout the place and the EPSG projeciton used 
        # st.write(f"LST visualisation of {namelbl} with EPSG:{st.session_state.epsg_location}")
        # st.write(f"{namelbl} EPSG:{st.session_state.epsg_location} {date} - {scene_hour} - Cloud Cover: {cloud_cover}% - {landsat_type} - Coverage: {coverage*100:.4}%")
        # st.write(f"Min: {temp_min:.2f}°C - Max: {temp_max:.2f}°C")
        st.write(f"Area: {namelbl} - EPSG:{st.session_state.epsg_location} - Min: {temp_min:.2f}°C - Max: {temp_max:.2f}°C")
        # This session variable allow to display the map in case there are data
        st.session_state.data = 1

        # True and false color visualization
        true_color_visualization = {
            'bands': ['red', 'green', 'blue'],  # Example Landsat bands for true color visualization
            'min': 0,
            'max': 0.3,
            'gamma': 1.4
        }
        false_color_visualization = {
            'bands': ['nir', 'red', 'green'],  # Example Landsat bands for true color visualization
            'min': 0,
            'max': 0.3,
            'gamma': 1.4
        }

        lst_visualization = {
            'min': temp_min,
            'max': temp_max,
            'palette': [
                '040274', '040281', '0502a3', '0502b8', '0502ce', '0502e6',
                '0602ff', '235cb1', '307ef3', '269db1', '30c8e2', '32d3ef',
                '3be285', '3ff38f', '86e26f', '3ae237', 'b5e22e', 'd6e21f',
                'fff705', 'ffd611', 'ffb613', 'ff8b13', 'ff6e08', 'ff500d',
                'ff0000', 'de0101', 'c21301', 'a71001', '911003'
            ]
        }
        
        # Add all the visualization to the second map of the page
        # map.addLayer(ee.Geometry(temp_image), {'color': 'red'}, 'Rectangle')
        map.addLayer(image,true_color_visualization,"True Color 432")
        map.addLayer(image,false_color_visualization,"False Color 432")
        map.addLayer(image.select('temp'), lst_visualization , 'Surface Temperature')
        
    

        # Get et put in string important variables
        CRS = f'EPSG:{EPSGloc}'
        UTM = str(EPSGloc)

        date_split =  date.split("-")
        date = "_".join(date_split)
        folder = f'UHI_{namelbl}_n°{index}_{date}_{EPSGloc}'

        if does_folder_exist_on_drive(folder):
            folder_existance = 1

        # Task list initialization
        export_task_list = []

    ################################################### All the task #################################################  
        ## LST
        export_lst_task = ee.batch.Export.image.toDrive(
        image=image,
        description='LST_' + UTM,
        folder=folder,
        scale=30,
        maxPixels = 1e13,
        region=aoi.getInfo()['coordinates'],
        crs = CRS,
        fileFormat='GeoTIFF'
        )
        export_task_list.append(export_lst_task)

        ## Landcover
        landcover = ee.ImageCollection('GOOGLE/DYNAMICWORLD/V1').filterBounds(aoi).select('label').reduce(ee.Reducer.mode()).clip(aoi)
        export_landcover_task = ee.batch.Export.image.toDrive(
        image=landcover,
        description='Land_Cover_' + UTM,
        scale=30,
        maxPixels=1e13,
        folder=folder,
        crs=CRS
        )
        export_task_list.append(export_landcover_task)

        ## Area of Interest
        export_aoi_task = ee.batch.Export.table.toDrive(
            collection=ee.FeatureCollection(aoi),
            description='AOI_4326',
            fileFormat='SHP',
            folder=folder
        )
        export_task_list.append(export_aoi_task)

        ## Canopy Height
        canopy_height = ee.Image("users/nlang/ETH_GlobalCanopyHeight_2020_10m_v1").clip(aoi)
        export_canopy_height_task = ee.batch.Export.image.toDrive(
            image=canopy_height,
            description='Canopy_Height_' +UTM,
            scale=10,
            maxPixels=1e13,
            folder=folder,
            crs=CRS
        )
        export_task_list.append(export_canopy_height_task)

        ## DEM 
        DEMraw = ee.ImageCollection('projects/sat-io/open-datasets/FABDEM').filterBounds(aoi)
        DEM = DEMraw.mosaic().setDefaultProjection('EPSG:3857', None, 30).clip(aoi)
        export_dem_task = ee.batch.Export.image.toDrive(
            image=DEM,
            description='DEM_' +UTM,
            scale=30,
            maxPixels=1e13,
            folder=folder,
            crs=CRS
        )
        export_task_list.append(export_dem_task)  

        ## Soil properties
        soil_properties = ee.Image('ISDASOIL/Africa/v1/texture_class').clip(aoi).select(0).rename('texture') \
                        .addBands(ee.Image('ISDASOIL/Africa/v1/texture_class').select(1).rename('texture_ug'))
        export_soil_properties_task = ee.batch.Export.image.toDrive(
            image=soil_properties,
            description='Soil_Texture_' +UTM,
            scale=30,
            maxPixels=1e13,
            folder=folder,
            crs=CRS
        )
        export_task_list.append(export_soil_properties_task)

        ## Hydrologic Group
        hydrologic_soil_group = ee.Image('projects/sat-io/open-datasets/HiHydroSoilv2_0/Hydrologic_Soil_Group_250m').clip(aoi)
        export_hydrologic_soil_group_task = ee.batch.Export.image.toDrive(
            image=hydrologic_soil_group,
            description='Hydrologic_Soil_Group_' +UTM,
            scale=30,
            maxPixels=1e13,
            folder=folder,
            crs=CRS
        )
        export_task_list.append(export_hydrologic_soil_group_task)

        ## LCZ (Local Climate Zone)
        LCZ = ee.ImageCollection('RUB/RUBCLIM/LCZ/global_lcz_map/latest').mosaic().clip(aoi).select('LCZ_Filter')
        export_lcz_task = ee.batch.Export.image.toDrive(
            image=LCZ,
            description='LCZ_' +UTM,
            scale=100,
            maxPixels=1e13,
            folder=folder,
            crs=CRS
        )
        export_task_list.append(export_lcz_task)

        # Put the list of every task into a session state variable
        st.session_state.task_list = export_task_list
    else:
        st.write("No data available for the selected parameters, try with a different date interval or cloud cover")
        st.session_state.data = 0

    return map, folder, folder_existance