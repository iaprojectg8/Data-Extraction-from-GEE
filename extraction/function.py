from config.imports import *

def update_file_path():
    """
    Function to update the folder path to download the drive files, when the user update it
    Args: 
        None
    Returns:
        None
    """
    st.session_state.folder_path = st.session_state.input_path

def callback_gray():
    """
    Callback function to make all the parameters disabled
    Args: 
        None
    Returns:
        None
    """
    st.session_state.gray = 1


def callback_gray_back():
    """
    Callback function to make all the parameters widget available again
    Args: 
        None
    Returns:
        None
    """
    st.session_state.gray = 0


def callback_map():
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
    callback_gray()



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
    st.session_state.downoloaded_but_not_reset = 0
    callback_gray_back()

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

def get_epsg_from_rectangle(rectangle_coords):
    """
    Returns the EPSG code for the UTM zone based on the centroid of the given rectangle coordinates.

    Args:
    rectangle_coords (list): List of tuples representing the (longitude, latitude) coordinates of the rectangle's corners.

    Returns:
    int: EPSG code for the UTM zone.
    """
    # Create a polygon from the rectangle coordinates
    polygon = Polygon(rectangle_coords)
    centroid = polygon.centroid
    
    # Get the EPSG code for the UTM zone of the centroid
    epsg_code = get_utm_epsg(centroid.y, centroid.x)
    
    return epsg_code



def task_manager():
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

                if not task.active():
                    
                    # Launch the task
                    task.start()
                    task_description = get_task_description(task)
                    task_description_list.append(task_description)
                    st.session_state.task_text_list = " - ".join(task_description_list)
                    writer.write(st.session_state.task_text_list)
                    print(f"{task_description} starts")
        
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
        

def get_task_description(task):
    """
    Function to get the name of the processing task.
    Args: 
        task (object): Task object representing a task in Earth Engine.
    Returns:
        str: Formatted description of the task.
    """
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
        images_list = on_coverage_filtered_collection.toList(on_coverage_filtered_collection.size())
        image_count = images_list.size().getInfo()
        
        # In case the list has more than one element, we can create a slider
        if image_count>1:
            index = st.slider('Select image index', 0, image_count-1, 0)
        else :
            index = image_count-1
            
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
        st.write(f"LST visualisation of {namelbl} with EPSG:{st.session_state.epsg_location}")
        st.write(f"{date} - {scene_hour} - Cloud Cover: {cloud_cover} - {landsat_type} - Coverage: {coverage*100:.4}%")
        st.write(f"Min: {temp_min:.2f}°C - Max: {temp_max:.2f}°C")

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
        folder = f'UHI_{namelbl}_{EPSGloc}'

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

    return map, folder