from utils.imports import *
from utils.variables import PYTHON_EXECUTABLE_PATH, LOGO_PATH



def put_logo_if_possible():
    with open(LOGO_PATH, "rb") as file:
        svg_content = file.read()
    st.set_page_config(page_title="Data Extraction",page_icon=svg_content)
    st.title("Data Extraction")


def flatten_with_coordinates(nested_list):
    """
    Flattens a list of lists while preserving coordinates as tuples.
    
    Parameters:
    nested_list (list): A nested list structure where coordinates are tuples of size 2.
    
    Returns:
    list: A flat list with coordinates preserved as tuples.
    """
    flat_list = []

    for item in nested_list:
        if isinstance(item, list) and len(item) != 2:
            flat_list.extend(flatten_with_coordinates(item))
        else:
            flat_list.append(item)
        # else:
        #     raise ValueError("All coordinates must be tuples of size 2")

    return flat_list



# This function is not used at all in the process, this is just a function that is very interesting
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
    # Perform reverse geocoding
    url = f"https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat={centroid.y}&lon={centroid.x}"
    response = requests.get(url)
    data = response.json()

    if "address" in data:
        if "city" in data["address"]:
            city = data["address"]["city"]
            return city
        elif "county" in data["address"]:
            return data["address"]["county"]
    else:
        return None


