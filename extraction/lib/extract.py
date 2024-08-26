from utils.imports import *
from utils.variables import LC89_BANDS, STD_NAMES
from drive.drive import does_folder_exist_on_drive
from lib.tasks import put_all_task_in_list
from lib.callbacks import callback_stop_export

######################################### Calculation on ee data

def apply_scale_factors(image:ee.Image):
    """
    Function to apply scale factors to an Earth Engine image.
    Args: 
        image (ee.Image): Earth Engine image object.
    Returns:
        image (ee.Image): Image with scale factors applied.
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
        real_start (ee.Number): Resulting hour modulo 24.
    """
    start_hour_number = ee.Number.parse(start)
    dec_hour_number = ee.Number.parse(dec)
    real_start = start_hour_number.add(dec_hour_number).mod(24)
    return real_start


def compute_band_min_max(img, region):
    """
    Function to compute minimum and maximum values of a band in an image over a region.
    Args: 
        img (ee.Image): Earth Engine image object.
        band (str): Name of the band to compute min and max values.
        region (ee.Geometry): Earth Engine geometry object representing the region of interest.
    Returns:
        stats (dict): Dictionary containing computed minimum and maximum values.
    """        
    stats = img.reduceRegion(
        reducer=ee.Reducer.minMax(),
        geometry=region,
        scale=30,
        maxPixels=1e13
    )
    return stats



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
    # Select the temp band to make the calculation of coverage on it
    temp_area = image.select("temp")
    # Count the amount of temperature pixel in the selected area
    temp_pixel_amount = temp_area.reduceRegion(
        reducer=ee.Reducer.toList().count(),
        geometry = aoi,
        scale = 30,
        maxPixels=1e9
    ).get("temp")
    # Count the total of pixel
    total_pixel_amount = image.pixelArea().reduceRegion(
        reducer = ee.Reducer.count(),
        geometry=aoi,
        scale = 30,
        maxPixels=1e9
    ).get("area")
 
    # Calculate the coverage percentage
    coverage_percentage = ee.Number(temp_pixel_amount).divide(ee.Number(total_pixel_amount))

    return image.set('coverage_percentage', coverage_percentage).set("total_pixel_amount",total_pixel_amount).set("temp_pixel_amount",temp_pixel_amount)


######################################### Image management


def extract_image_collection(aoi, startdate, enddate, maxcloud):
    """
    Extract the image collection from Landsat8 and Landsat9 with a certain 
    amount of constraints

    Args:
        aoi (ee.Geometry) :  The AOI from the drawing of the user
        startdate (str): Start date chosen by the user with the calendar tools
        enddate (str): End date date chosen by the user with the calendar tools
        maxcloud (str): Maximum cloud percentage chosen by the user with the slider
    Returns:
        imageL8 (ee.ImageCollection): Image collection extracted from landsat8 
        imageL9 (ee.ImageCollection): Image collection extracted from landsat9
    """
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
    
    return imageL8, imageL9


def manage_available_images(python_list):
    """
    Extract interesting features from the images got and make list with them.

    Args:
        python_list (list): It contains all the features for each images
    Returns:
        entity_to_index (dict): Contains descriptions and indices
        select_box_list (list): Contains all the description of the images
    """
    entity_to_index =dict()
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
        entity_to_index[entity] = i

    return entity_to_index, select_box_list

def get_folder_properties(epsg, date, area_name, index):
    """
    Get properties to make quite unique folder name for the export

    Args:
        epsg (str): EPSG code of the selected area
        date (str): date of the image selected
        area_name (str): Name given by the user to the area
        index (int): Index corresponding to the location in the list of the selected image
    Returns:
        CRS (str): It will be placed in the parameters for each export
        UTM (str): This will be noted on each filename exported, to know the epsg of it
        folder (str): Entire name of the folder that will be on the drive
    """
    # Get et put in string important variables
    CRS = f'EPSG:{epsg}'
    UTM = str(epsg)

    date_split =  date.split("-")
    date = "_".join(date_split)
    folder = f'UHI_{area_name}_n°{index}_{date}_{epsg}'

    return CRS, UTM, folder


def get_temp_min_max(image, aoi):
    """
    Get Minimum and Maximum temperature from the image area selected

    Args:
        image (ee.image.Image): Image containing only the LST band, to make the visualization
        aoi (ee.Geometry):  The AOI from the drawing of the user
        
    Returns
        temp_min (float): Minimum temperature of the LST in the selected AOI
        temp_max (float): Maximum temperature of the LST in the selected AOI
    """
    # Compute min and max LST of the selected area 
    band_min_max = compute_band_min_max(image, aoi)
    temp_min =  band_min_max.getInfo()['temp_min']
    temp_max =  band_min_max.getInfo()['temp_max']

    return temp_min, temp_max


######################################### Visualization

def create_and_add_visualizations(temp_min, temp_max, map, image):
    """
    Create visualizations and add them to the map

    Args:
        temp_min (float): Minimum temperature of the LST in the selected AOI
        temp_max (float): Maximum temperature of the LST in the selected AOI
        map (geemap.foliumap.Map): Second map on which the visualization will be added 
        image (ee.image.Image): Image containing only the LST band, to make the visualization
    """
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
    map.addLayer(image,true_color_visualization,"True Color 432")
    map.addLayer(image,false_color_visualization,"False Color 432")
    map.addLayer(image.select('temp'), lst_visualization , 'Surface Temperature')


######################################### Main part on the data extraction


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
        map (geemap.Map): The updated map object with layers added.
        folder (str): Name of the folder in the drive
        folder_existance (bool): Just to know if this folder name exists on the drive
    """
    # Coverage threshold corresponds to the part of the image that exists in the temperature band
    parameters_list = list((aoi, EPSGloc, startdate, enddate, starthour, endhour, dechour, maxcloud,coverage_threshold))
    folder = None
    folder_existance = 0

    imageL8, imageL9 = extract_image_collection(aoi=aoi, startdate=startdate, enddate=enddate, maxcloud=maxcloud)

    # Recalculating the start and end hours depending on where the area is in the world
    real_start_hour = add_hours(starthour, dechour)
    real_end_hour = add_hours(endhour, dechour)

    # Merging all the image collection into a single one, also filtering on the hour
    images_merged = ee.ImageCollection(imageL8.merge(imageL9)) \
                    .filter(ee.Filter.calendarRange(real_start_hour, real_end_hour, "hour"))

    # Put a filter on the image collection to keep the images that respects the threeshold
    coverage_collection = images_merged.map(lambda image : calculate_coverage(image, aoi))
    on_coverage_filtered_collection =  coverage_collection.filter(ee.Filter.gte('coverage_percentage', coverage_threshold))
  

    if on_coverage_filtered_collection.size().getInfo() != 0:

        # If the parameters don't change, we don't need to redo the following operation
        # Thus it saves some time.
        if parameters_list != st.session_state.parameters_list:

            # Here we get the available list of images that corresponds to the coverage filter
            images_list = on_coverage_filtered_collection.toList(on_coverage_filtered_collection.size()).reverse()
            st.session_state.images_list = images_list
            
            # Put the list in a python list to have this in local, and accelerate the process
            python_list = images_list.getInfo()
            st.session_state.python_list = python_list
            st.session_state.parameters_list = parameters_list
            callback_stop_export()

        entity_to_index, select_box_list = manage_available_images(python_list=st.session_state.python_list)
    

        # Selection made by the user
        entity_chosen = st.selectbox(label=f"Chose an image, {len(st.session_state.python_list)} are available with your parameters",options=select_box_list)
        if entity_chosen == st.session_state.entity_chosen:
            # Keep writing information if the user launch an export or a download
            st.write(f"Area: {namelbl} - EPSG:{st.session_state.epsg_location} - Min: {st.session_state.temp_min:.2f}°C - Max: {st.session_state.temp_max:.2f}°C")
            return st.session_state.second_map, st.session_state.folder_name, st.session_state.folder_existance
        
        # All the following part is not executed if all the parameters are the same, and the 
        # images chosen by the user in the selectbox is the same as well
        st.session_state.entity_chosen = entity_chosen
        index = entity_to_index[entity_chosen]
        
        # Get the selected image
        image = ee.Image(st.session_state.images_list.get(index)).clip(aoi)
        date = str(image.getInfo()["properties"]['DATE_ACQUIRED'])
        
   
        temp_min, temp_max = get_temp_min_max(image=image, aoi=aoi)
        st.session_state.temp_min = temp_min
        st.session_state.temp_max = temp_max

        # Display information for the user
        st.write(f"Area: {namelbl} - EPSG:{st.session_state.epsg_location} - Min: {temp_min:.2f}°C - Max: {temp_max:.2f}°C")

        # This session variable allow to display the map in case there are data
        st.session_state.data = 1
          
        # The visualisation is the part that takes the most of time
        create_and_add_visualizations(temp_min=temp_min, temp_max=temp_max, map=map, image=image)
        CRS, UTM, folder = get_folder_properties(epsg=EPSGloc, date=date, area_name=namelbl, index=index)
        st.session_state.folder_name = folder
        
    
        if does_folder_exist_on_drive(folder):
            folder_existance = 1

        st.session_state.folder_existance = folder_existance

        # Put the list of every task into a session state variable
        st.session_state.task_list = put_all_task_in_list(image=image, UTM=UTM, folder=folder, aoi=aoi, CRS=CRS)
    else:
        st.write("No data available for the selected parameters, try with a different date interval or cloud cover")
        st.session_state.data = 0

    return map, folder, folder_existance