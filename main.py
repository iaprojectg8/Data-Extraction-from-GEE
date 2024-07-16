from utils.imports import *

def start_streamlit():
    os.system("streamlit run extraction/extraction.py --server.headless true --browser.serverAddress ''")

# Start Streamlit in a separate thread
t = threading.Thread(target=start_streamlit)
t.start()

# Create a webview window to display the Streamlit app
webview.create_window('Extraction App', 'http://localhost:8501')
webview.start()