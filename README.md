<div style="text-align: center;">
    <h1>Data extraction</h1>
</div>



This application allows you to extract Land Surface Temperature (LST) data for a given study area using Google Earth Engine and display it using a web-based interface.

## Features

- Authenticate with Google Earth Engine
- Extract LST data for the specified area and time period
- Visualize the data on an interactive map
- Launch and stop data export tasks to Google Drive
- Download the files from the drive
- Chose the local path to make the download

## Prerequisites

Make sure you have the following :

- Python 3.7 or higher
- Google Cloud project

## Setup


1. **Create a virtual environement**:
Open a command prompt or a terminal and create a virtual environment:
```
python -m venv yourenvname
```

2. **Activate it**:
```
yourenvname\Scripts\activate
```
4. **Install the dependencies**:
```
pip install -r requirements.txt
```

## Project

First if you do not have any Google Earth Engines project, you need to create one. To do this I recommend you to watch this video:
[![Watch the video](images/image_gee.png)](https://www.youtube.com/watch?v=B0ZOebP3OyQ)


Finally to make the process work you need to put your Earth Engine project name into the file `extraction/gee_project.json`, the name of your project instead of mine.
In the location said change the string framed in red.

<div style="text-align: center;" >
    <img src="images/gee_project_screen.png">
</div>

## Drive
In order to get the files on your local computer, you can download them from the app. But to be able to do that you need to get your own credentials, from the [Google Cloud Platform](https://console.cloud.google.com/). I let you read the document I have made for this.


## Execution
To execute the program, still in the command prompt run this :
```
python main.py
```

## The App
On the application, you have 2 main parts, the parameters and the map. Select your own parameters.

Then use the drawing tool of the map and make a zone on which you want to extract data from. If there is data it will show you an LST visualization of your selected zone. Unfortunately, depending on your selected parameters it is possible that no data is available. Thus you need to change them to have something to extract (cloud cover, coverage percentage or date interval are the best parameters to change if you don't have any data).

Thus you can extract the data with the button or draw another zone. If you need to stop the extraction during the process don't hesitate, the "Stop" button is in this purpose.

Finally, you can download the folder containing all the exported data, that are stored on the drive. You just need to click on the button. If it is the first time that you make the app run, you will have to connect to your Google account linked to the GEE project to be able to download. Of course, if you did not follow my guide to create your credentials, you will not be able to download, you will get an error when connecting. 

Here is a brief video on how you can use the app.


[![Watch the video](images/appealing_image.png)](https://www.youtube.com/watch?v=u-F7HcA686E)


