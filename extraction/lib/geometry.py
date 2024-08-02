from utils.imports import *
from lib.callbacks import callback_stop_export
from lib.helpers import flatten_with_coordinates


######################################### Work directly with geometry


def fill_geometry(output):
    """
    Function to get the output and the geometry from the output. Actually it is done to create
    the geometry in all the possible cases.
    Args: 
        output (dict): geometry object.
        
    Returns:
        output (dict) : same as the entry except there is the shape key added with the corresponding value
        geometry (dict) : This geometry will be then use to get the coordinates
    """
    # i am going to try to make a function with this part
    if 'last_active_drawing' in output and output['last_active_drawing'] is not None :
        last_drawing = output['last_active_drawing']
        if 'geometry' in last_drawing :
            geometry = last_drawing["geometry"]
   
    elif "shape" in output :
        shape = output["shape"]["features"][0]
        geometry = shape["geometry"]

    return output, geometry


def get_ee_geometry(geometry):
    """
    Function to get an ee_geometry object from a shapely geometry one
    Args: 
        geometry (dict): geometry object.
        
    Returns:
        ee_geometry (dict)
    """
    # Get the coordinates and calculate the EPSG
    coordinates = geometry['coordinates']
    if geometry["type"] == "MultiPolygon":
        flatten_coordinates = flatten_with_coordinates(coordinates)
        epsg_code = get_epsg_from_polygon(flatten_coordinates)
        ee_geometry = ee.Geometry.MultiPolygon(coordinates)
    elif geometry["type"] == "Polygon":
        epsg_code = get_epsg_from_polygon(coordinates[0])
        ee_geometry = ee.Geometry.Polygon(coordinates)

    st.session_state.epsg_location = epsg_code
    
    if "geometry" not in st.session_state:
        st.session_state.geometry = ee_geometry
    if ee_geometry != st.session_state.geometry:
        st.session_state.geometry = ee_geometry
        callback_stop_export() 
    return ee_geometry


######################################### Center and zoom



def get_geometry_center_and_zoom_json(coordinates):
    """
    Function to estimate center and zoom level from a GeoJSON geometry.
    
    Args: 
        geojson_geometry (dict): GeoJSON geometry object.
        
    Returns:
        center (list): List that contains the center of the map corresponding to the AOI coordinates
        zoom (int): Estimated zoom for the current AOI

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


def get_geometry_center_and_zoom(geometry):
    """
    Function to estimate center and zoom level, for the second map, from the clipping that 
    the user made on the first map
    Args: 
        geometry (ee.Geometry): Earth Engine geometry object.
    Returns:
        center (tuple): Tuple containing estimated center coordinates
        zoom (int): Int containing the extimated zoom level
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
    if extent > 0:
        zoom = min(max(1, int(round(9 - math.log(extent, 2)))), 20)
    else:
        # Default zoom level if extent is zero
        zoom = 8  
    center = [lat_center, lon_center]

    return center, zoom


def get_gdf_zoom(gdf):
    """
    Function zoom level based on a geo dataframe
    in a GeoDataFrame.

    Args:
        gdf (geopandas.GeoDataFrame): GeoDataFrame containing geometries.

    Returns:
        zoom (int): Int containing estimated  zoom level.
    """
    # Calculate the bounds of the geometries
    bounds = gdf.total_bounds
    lon_min, lat_min, lon_max, lat_max = bounds

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

    return  zoom


    


######################################### EPSG, UTM, CRS



def get_utm_epsg(lat, lon):
    """
    Returns the EPSG code for the UTM zone based on the given latitude and longitude.

    Args:
    lat (float): Latitude of the point.
    lon (float): Longitude of the point.

    Returns:
    epsg_code (int): EPSG code for the UTM zone.
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
    epsg_code (int): EPSG code for the UTM zone.
    """
    # Create a polygon from the rectangle coordinates
    polygon = Polygon(polygon_coordinates)
    centroid = polygon.centroid
    
    # Get the EPSG code for the UTM zone of the centroid
    epsg_code = get_utm_epsg(centroid.y, centroid.x)
    
    return epsg_code