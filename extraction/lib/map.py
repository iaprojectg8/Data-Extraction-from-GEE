from utils.imports import *

def restrict_iframe():
    """
    Function to restrict the iframe. Actually when testing the app, there were numerous cases in which
    the expander heigth was enormous
    """
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
    """
    Function to initialize the expander in which the first map will be.
    Args: 
        json_gdf (dict): JSON object in which there are the coordinates of an uploaded shape file .
    Returns:
        output (dict) : It contains either the shape file coordiantes either the drawn shape ones
    """
    # This allow to hide the map when some button is pressed
    with st.expander("Draw a zone", st.session_state.expanded,icon=":material/draw:"):
        output = st_folium(st.session_state.first_map, use_container_width=True)

        if json_gdf:
            output["shape"] = json_gdf
        
        return output
        


def map_initialization():
    """
    Function to initialize a map just before to assign anything to it
    Returns:
        m : It corresponds to the created map
    """
    m = folium.Map(location=(1,20), zoom_start=3) 
    Draw().add_to(m)
    st.session_state.first_map = m
    return m
