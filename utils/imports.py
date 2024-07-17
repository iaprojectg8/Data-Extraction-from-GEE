
# Import for the folium map and all the folium functionalities
import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import Draw 

# Import to use the Google Earth Engine function
import ee
import geemap.foliumap as geemap


# A lot of needed module for the app to work
import webview
import math
import time
import threading
import os
from datetime import datetime
import json
from shapely.geometry import Polygon
import requests

# Import for the drive downloading
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload
from google.auth.exceptions import RefreshError
