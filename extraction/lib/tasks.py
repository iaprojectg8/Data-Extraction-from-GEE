from utils.imports import *


######################################### Task manager dependances

def task_manager(folder_existance):
    """
    Function to manage tasks. Everything is done with session state variable, this is why there is not 
    any parameter or return. This goes when the "Launch button is activated, the task are successively
    launched one by one. This function contains a lot of displayings for the user to know the progress 
    of the different tasks.

    Args:
        folder_existance (bool): Boolean that indicates if the folder name already exists in the drive
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


def get_task_description(task,folder_existance):
    """
    Function to get the name of the processing task.
    Args: 
        task (object): Task object representing a task in Earth Engine.
    Returns:
        task_description (str): Formatted description of the task.
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
        
def check_task_status(task):
    """
    Function to continuously check the status of a task.
    Args: 
        task (object): Task object representing a task in Earth Engine.
    """
    while task.active() :
        status = task.status()["state"]
        if st.session_state.status != status:
            print('State:', status)
            st.session_state.status = status



######################################### All the tasks one by one 



def lst_task(image, UTM, folder, aoi, CRS):
    """
    Create the LST task, for the export

    Args:
        image (ee.image.Image): Image containing only the LST band
        UTM (str): EPSG code of the AOI
        folder (str): Name of the folder in which the data will be exported on the drive
        aoi (ee.Geometry):  The AOI from the drawing of the user
        CRS (str): EPSG code with the string 'EPSG:' added before
    Returns
        export_lst_task (ee.batch.Task): Task to export LST image on the drive
    """
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
    return export_lst_task

def landcover_task(UTM, folder, aoi, CRS):
    """
    Get the landcover image collection and create the landcover task, for the export

    Args:
        UTM (str): EPSG code of the AOI
        folder (str): Name of the folder in which the data will be exported on the drive
        aoi (ee.Geometry):  The AOI from the drawing of the user
        CRS (str): EPSG code with the string 'EPSG:' added before
    Returns
        export_landcover_task (ee.batch.Task): Task to export landcover image on the drive
    """
    landcover = ee.ImageCollection('GOOGLE/DYNAMICWORLD/V1').filterBounds(aoi).select('label').reduce(ee.Reducer.mode()).clip(aoi)
    export_landcover_task = ee.batch.Export.image.toDrive(
        image=landcover,
        description='Land_Cover_' + UTM,
        scale=30,
        maxPixels=1e13,
        folder=folder,
        crs=CRS
    )
    return export_landcover_task

def aoi_task(folder, aoi):
    """
    Create the AOI task, for the export

    Args:
        
        folder (str): Name of the folder in which the data will be exported on the drive
        aoi (ee.Geometry):  The AOI from the drawing of the user
       
    Returns
        export_aoi_task (ee.batch.Task): Task to export AOI files on the drive
    """
    export_aoi_task = ee.batch.Export.table.toDrive(
    collection=ee.FeatureCollection(aoi),
    description='AOI_4326',
    fileFormat='SHP',
    folder=folder
    )
    return export_aoi_task

def canopy_height_task(UTM, folder, aoi, CRS):
    """
    Get the canopy height image collection and create the canopy height task, for the export

    Args:
        UTM (str): EPSG code of the AOI
        folder (str): Name of the folder in which the data will be exported on the drive
        aoi (ee.Geometry):  The AOI from the drawing of the user
        CRS (str): EPSG code with the string 'EPSG:' added before
    Returns
        export_canopy_height_task (ee.batch.Task): Task to export canopy height image on the drive
    """
    canopy_height = ee.Image("users/nlang/ETH_GlobalCanopyHeight_2020_10m_v1").clip(aoi)
    export_canopy_height_task = ee.batch.Export.image.toDrive(
        image=canopy_height,
        description='Canopy_Height_' +UTM,
        scale=10,
        maxPixels=1e13,
        folder=folder,
        crs=CRS
    )
    return export_canopy_height_task

def dem_task(UTM, folder, aoi, CRS):
    """
    Get the DEM image collection and create the DEM task, for the export

    Args:
        UTM (str): EPSG code of the AOI
        folder (str): Name of the folder in which the data will be exported on the drive
        aoi (ee.Geometry):  The AOI from the drawing of the user
        CRS (str): EPSG code with the string 'EPSG:' added before
    Returns
        export_dem_task (ee.batch.Task): Task to export DEM image on the drive
    """
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
    return export_dem_task

def soil_properties_task(UTM, folder, aoi, CRS):
    """
    Get the soil properties image collection and create the soil properties task, for the export

    Args:
        UTM (str): EPSG code of the AOI
        folder (str): Name of the folder in which the data will be exported on the drive
        aoi (ee.Geometry):  The AOI from the drawing of the user
        CRS (str): EPSG code with the string 'EPSG:' added before
    Returns
        export_soil_properties_task (ee.batch.Task): Task to export soil properties image on the drive
    """
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
    return export_soil_properties_task

def hydrologic_soil_group_task(UTM, folder, aoi, CRS):
    """
    Get the hydrologic soil group image collection and create the hydrologic soil group task, for the export

    Args:
        UTM (str): EPSG code of the AOI
        folder (str): Name of the folder in which the data will be exported on the drive
        aoi (ee.Geometry):  The AOI from the drawing of the user
        CRS (str): EPSG code with the string 'EPSG:' added before
    Returns
        export_hydrologic_soil_group_task (ee.batch.Task): Task to export hydrologic soil group image on the drive
    """
    hydrologic_soil_group = ee.Image('projects/sat-io/open-datasets/HiHydroSoilv2_0/Hydrologic_Soil_Group_250m').clip(aoi)
    export_hydrologic_soil_group_task = ee.batch.Export.image.toDrive(
        image=hydrologic_soil_group,
        description='Hydrologic_Soil_Group_' +UTM,
        scale=30,
        maxPixels=1e13,
        folder=folder,
        crs=CRS
    )
    return export_hydrologic_soil_group_task

def lcz_task(UTM, folder, aoi, CRS):
    """
    Get the LCZ image collection and create the LCZ task, for the export

    Args:
        UTM (str): EPSG code of the AOI
        folder (str): Name of the folder in which the data will be exported on the drive
        aoi (ee.Geometry):  The AOI from the drawing of the user
        CRS (str): EPSG code with the string 'EPSG:' added before
    Returns
        export_lcz_task (ee.batch.Task): Task to export LCZ image on the drive
    """
    LCZ = ee.ImageCollection('RUB/RUBCLIM/LCZ/global_lcz_map/latest').mosaic().clip(aoi).select('LCZ_Filter')
    export_lcz_task = ee.batch.Export.image.toDrive(
        image=LCZ,
        description='LCZ_' +UTM,
        scale=100,
        maxPixels=1e13,
        folder=folder,
        crs=CRS
    )
    return export_lcz_task

######################################### Put all the tasks into a list


def put_all_task_in_list(image, UTM, folder, aoi, CRS):
    """
    Add all the task into a list

    Args:
        image (ee.image.Image): Image containing only the LST band, to make the visualization
        UTM (str): EPSG code of the AOI
        folder (str): Name of the folder in which the data will be exported on the drive
        aoi (ee.Geometry):  The AOI from the drawing of the user
        CRS (str): EPSG code with the string 'EPSG:' added before
    Returns
        export_task_list (list): This list contains all the task to for the export to the drive
    """

    export_task_list = []
    ## LST
    export_lst_task = lst_task(image=image, UTM=UTM, folder=folder, aoi=aoi, CRS=CRS)
    export_task_list.append(export_lst_task)

    ## Landcover
    export_landcover_task = landcover_task(UTM=UTM, folder=folder, aoi=aoi, CRS=CRS)
    export_task_list.append(export_landcover_task)

    ## Area of Interest
    export_aoi_task = aoi_task(folder=folder, aoi=aoi)
    export_task_list.append(export_aoi_task)

    ## Canopy Height
    export_canopy_height_task = canopy_height_task(UTM=UTM, folder=folder, aoi=aoi, CRS=CRS)
    export_task_list.append(export_canopy_height_task)

    ## DEM 
    export_dem_task = dem_task(UTM, folder, aoi, CRS)
    export_task_list.append(export_dem_task)  

    # Soil properties
    export_soil_properties_task = soil_properties_task(UTM=UTM, folder=folder, aoi=aoi, CRS=CRS)
    export_task_list.append(export_soil_properties_task)

    ## Hydrologic Group
    export_hydrologic_soil_group_task =hydrologic_soil_group_task(UTM=UTM, folder=folder, aoi=aoi, CRS=CRS)
    export_task_list.append(export_hydrologic_soil_group_task)

    ## LCZ (Local Climate Zone)
    export_lcz_task = lcz_task(UTM=UTM, folder=folder, aoi=aoi, CRS=CRS)
    export_task_list.append(export_lcz_task)

    return export_task_list
