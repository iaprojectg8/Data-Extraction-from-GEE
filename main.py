from utils.imports import *
import subprocess

def start_streamlit():
    subprocess.run([
        "streamlit", "run", "extraction/extraction.py",
        "--server.headless", "true",
        "--browser.serverAddress", ""
    ])

# Start Streamlit in a separate thread
thread = threading.Thread(target=start_streamlit)
thread.start()

# Create a webview window to display the Streamlit app
webview.create_window('Extraction App', 'http://localhost:8501')
webview.start()