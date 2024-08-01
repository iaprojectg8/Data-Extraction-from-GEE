from pyqgis.utils.qgis_imports import *
from pyqgis.utils.qgis_variables import DATA_FOLDER, RESULTS_FOLDER
from pyqgis.algorithms.Script_Préparation_Données import ExtractionDuFichierCsvPourOutilIa

def make_csv(city):
    """
    Add the csv extension at a city name

    Args:
        city (str): City name that will be the CSV file name as well
    Return:
        city+".csv" (str): CSV filename of the city
    """
    return city+".csv"


def reorganize_folder(path):
    """
    Create data and results folder if they don't exist et return their paths. 
    Additionnally it moves the files from the folder root to the data folder

    Args:
        path (str): Path to the folder where the data are
    Returns:
        data_folder_path (str): Data folder path 
        results_folder_path (str): Results folder path
    """
    print(path)
    folder_dir = os.listdir(path)

    if DATA_FOLDER in folder_dir:
        print("Data folder already created")
        data_folder_path= os.path.join(path,DATA_FOLDER)
        print(data_folder_path)
    else : 
        data_folder_path = os.path.join(path,DATA_FOLDER)
        print(data_folder_path)
        os.makedirs(data_folder_path)
        for filename in os.listdir(path):
            file_path = os.path.join(path, filename)
            
            # Check if it is a file (not a directory)
            if os.path.isfile(file_path):
                shutil.move(file_path, data_folder_path)

    if RESULTS_FOLDER in folder_dir:
        results_folder_path = os.path.join(path,RESULTS_FOLDER)
        print(results_folder_path)
        print("Results folder already created")
    else : 
        results_folder_path = os.path.join(path,RESULTS_FOLDER)
        print(results_folder_path)
        os.makedirs(results_folder_path)

    return data_folder_path, results_folder_path

def get_epsg_and_city(entire_path:str):
    """
    Get epsg and city name from the path, as it provides it

    Args:
        entire_path (str): Entire path to the data folder
    Returns: 
        epsg (str): EPSG code for the data
        city (str): City corresponding to the data
    """
    # Get folder name string to then get the epsg and the city
    folder_name = entire_path.split("\\")[-1]
    folder_name_list = folder_name.split("_")
    
    # Get the epsg code
    epsg = folder_name_list[-1]
    uhi = folder_name_list[:-5]

    # Get the city name
    city ="_".join(uhi[1:])
    return epsg, city 


def set_aoi(landsat_path, epsg):
    """
    Set the AOI

    Args:
        landsat_path (str): Entire path to the data folder
        epsg (str): EPSG code
    Returns: 
        epsg (str): EPSG code for the data
        city (str): City corresponding to the data
    """
    if landsat_path:
        try:
            landsat_layer = QgsRasterLayer(landsat_path, "Landsat Image")
            if landsat_layer.isValid():

                target_crs = QgsCoordinateReferenceSystem('EPSG:4326')
                original_crs = QgsCoordinateReferenceSystem(f'EPSG:{epsg}')

                # Prepare a tool to transform an extent from a CRS to another
                coordinate_transform = QgsCoordinateTransform(original_crs, target_crs, QgsProject.instance())
                extent = landsat_layer.extent()

                # Now we use the tool that we have created to transform the extent
                transform_extent = coordinate_transform.transformBoundingBox(extent)
                print("transform extent", transform_extent)
                aoi = transform_extent
                print(aoi)
            else:
                aoi = None
        except Exception as e:
            print(f"Error setting extent: {str(e)}")
    return aoi

def set_parameters(data_path, results_path, epsg_num, city):
    """
    Set all the parameters in a dictionary to give them afterward to the algorithm 

    Args:
        data_path (str): Entire path to the data folder
        results_path (str): Entire path to the results folder
        epsg_num (str): EPSG code
        city (str): City corresponding to the data
    Returns: 
        parameters (dict): This dictionary contains all the parameters that the algorithm needs to work
    """
    # List all files in the directory
    files_in_directory = os.listdir(data_path)
    print(files_in_directory)

    # Initialize variables for each file type
    lst_raster = ''
    mnt_raster = ''
    occupation_du_sol_raster = ''
    nature_du_sol_raster = ''
    hauteur_arboree_raster = ''
    categorie_hydrologique_raster = ''
    zone_climatique_raster = ''
    ### city n'est surement pas bon, à voir pour le change ensuite
    csv_file = make_csv(city)
    print(csv_file)
    tableur_sortie = os.path.join(results_path,csv_file)
    print(tableur_sortie)

    # Loop through files and match based on conditions
    for file in files_in_directory:
        if str(epsg_num) in file and not file.endswith(".aux.xml"):
            file_lowered = file.lower()
            # LST condition
            if "lst" in file_lowered or "temperature" in file_lowered:
                lst_raster = os.path.join(data_path,file)
            # MNT condition
            elif "dem" in file_lowered or "mnt" in file_lowered:
                mnt_raster = os.path.join(data_path,file)
            # Occupation du sol condition
            elif "land_cover" in file_lowered or "occupation" in file_lowered:
                occupation_du_sol_raster = os.path.join(data_path,file)
            # Nature du sol condition
            elif "soil_texture" in file_lowered or "nature" in file_lowered:
                nature_du_sol_raster = os.path.join(data_path,file)
            # Hauteur arborée condition
            elif "canopy_height" in file_lowered or "hauteur_arbore" in file_lowered:
                hauteur_arboree_raster = os.path.join(data_path,file)
            # Catégorie hydrologique condition
            elif "hydrologic_soil_group" in file_lowered or "groupe_hydrologique" in file_lowered:
                categorie_hydrologique_raster = os.path.join(data_path,file)
            # Zone climatique condition
            elif "lcz" in file_lowered or "zone_climatique" in file_lowered:
                zone_climatique_raster = os.path.join(data_path,file)
            # Tableur en sortie condition
            
    uhi_aoi = set_aoi(lst_raster,epsg=epsg)

    parameters = {
        'image_landsat_9': lst_raster,
        'numro_de_bande_de_la_lst': 7,
        'rsolution_de_la_couche_lst_m': 30,
        'raster_du_mnt': mnt_raster,
        'raster_de_loccupation_du_sol_dwv1': occupation_du_sol_raster,
        'raster_de_la_nature_du_sol': nature_du_sol_raster,
        'raster_de_la_hauteur_arbore': hauteur_arboree_raster,
        'raster_de_la_catgorie_hydrologique': categorie_hydrologique_raster,
        'raster_de_la_zone_climatique_lcz': zone_climatique_raster,
        'scr_de_projection_des_donnes': QgsCoordinateReferenceSystem(epsg_num), 
        'emprise_de_calcul_de_luhi': uhi_aoi,  # Presumably set elsewhere
        'nom_du_champ_daltitude': 'ALT',
        'nom_du_champ_de_nature_du_sol': 'NATSOL',
        'nom_du_champ_de_pente': 'PENTE',
        'nom_du_champ_dexposition': 'EXP',
        'nom_du_champ_doccupation_du_sol': 'OCCSOL',
        'nom_du_champ_pour_le_caractre_urbainrural': 'URB',
        'nom_du_champ_de_hauteur_arbore': 'HAUTA',
        'nom_du_champ_de_catgorie_hydrologique': 'CATHYD',
        'nom_du_champ_de_zone_climatique': 'ZONECL',
        'nom_du_champ_dalbedo': 'ALB',
        'tableur_sortie': tableur_sortie
    }

    return parameters

if __name__ == '__main__':

    # Initialize pyqgis 
    app = QApplication(sys.argv)
    Processing.initialize()

    # This allows to take the path given by the main program, extraction.pys
    parser = argparse.ArgumentParser(description='Run QGIS processing with specified path.')
    parser.add_argument('path', type=str, help='Path to the input directory')
    args = parser.parse_args()

    # Get the epsg and the city name from the path given by the main program
    path = args.path
    epsg, city = get_epsg_and_city(path)

    # Reorganize the folder given by the path
    data_path, results_path = reorganize_folder(path)
    print("Result path :", results_path)

    # Set the parameters
    parameters = set_parameters(data_path, results_path,epsg_num=epsg,city=city)
    print(parameters)  # For testing, print the parameters

    # Initialize algorithm, context, feedback
    algorithm = ExtractionDuFichierCsvPourOutilIa()
    context = QgsProcessingContext()
    feedback = QgsProcessingFeedback()

    # Run the algorithm
    result = algorithm.processAlgorithm(parameters, context, feedback)
