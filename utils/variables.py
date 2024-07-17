CREDENTIALS_PATH = "drive/credentials.json"
TOKEN_PATH = "drive/token.json"

GEE_PROJECT = 'utils/gee_project.json'
DOWNLOAD_PATH = "drive/download_path.txt"



# This scope is the only one to use because this is the one that provide all the abilities on files and folders
SCOPE = "https://www.googleapis.com/auth/drive"



def get_download_path():
    with open(DOWNLOAD_PATH,"r") as f:
        path = f.read()
    return path
    

# This is the path where all the dataste are 
PATH =  get_download_path()



C1 = 1.19104e8
C2 = 14387.7


BAND_INFO = {
    "10": {"UCC": 0.006882, "K1": 3040.14, "K2": 1735.34, "Wavelength": 8.291},
    "11": {"UCC": 0.006780, "K1": 2482.38, "K2": 1666.40, "Wavelength": 8.634},
    "12": {"UCC": 0.006590, "K1": 1935.06, "K2": 1585.42, "Wavelength": 9.075},
    "13": {"UCC": 0.005693, "K1": 866.47, "K2": 1350.07, "Wavelength": 10.657},
    "14": {"UCC": 0.005225, "K1": 641.33, "K2": 1271.22, "Wavelength": 11.318}
}

CIJ_VALUES_STD66 = {
    "13": {
        "c11": 0.06524,
        "c12": -0.55835,
        "c13": -0.00284,
        "c21": -0.05878,
        "c22": -0.75881,
        "c23": 1.35633,
        "c31": 1.06576,
        "c32": 0.00327,
        "c33": -0.43020
    },
    "14": {
        "c11": 0.10062,
        "c12": -0.79740,
        "c13": -0.03091,
        "c21": -0.13563,
        "c22": -0.39414,
        "c23": 1.60094,
        "c31": 1.10559,
        "c32": -0.17664,
        "c33": -0.56515
    }
}


CIJ_VALUES_TIGR61 = {
    "13": {
        "c11": 0.05327,
        "c12": -0.48444,
        "c13": 0.00764,
        "c21": -0.03937,
        "c22": -0.74611,
        "c23": 1.24532,
        "c31": 1.05742,
        "c32": -0.03015,
        "c33": -0.39461
    },
    "14": {
        "c11": 0.07965,
        "c12": -0.66528,
        "c13": -0.01578,
        "c21": -0.09580,
        "c22": -0.48582,
        "c23": 1.46358,
        "c31": 1.08983,
        "c32": -0.17029,
        "c33": -0.52486
    }
}