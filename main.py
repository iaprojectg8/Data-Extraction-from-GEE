from utils.imports import *
import subprocess

def start_streamlit():
    subprocess.run([
        "streamlit", "run", "extraction/extraction_script.py",
        "--browser.serverAddress", ""
    ])

# Start Streamlit in a separate thread
t = threading.Thread(target=start_streamlit)
t.start()

# Create a webview window to display the Streamlit app
webview.create_window('Extraction App', 'http://localhost:8501')
webview.start()