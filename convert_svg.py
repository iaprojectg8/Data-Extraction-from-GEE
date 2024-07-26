import streamlit as st
import cairosvg
from PIL import Image
import io

# Path to the SVG file
svg_file_path = "images/Logo_G8.svg"
pgn_file_path = "images/Logo_G8.png"
png_keran_file_path = "images/keran.png"

# Convert SVG to PNG
with open(svg_file_path, "rb") as svg_file:
    svg_content = svg_file.read()
    png_content = cairosvg.svg2png(bytestring=svg_content)

# Save the PNG to a file
with open(pgn_file_path, "wb") as png_file:
    png_file.write(png_content)

# Load the PNG image
png_image = Image.open(png_keran_file_path)

# Set the page configuration
st.set_page_config(page_title="My App", page_icon=png_image, layout="wide")

# Display the app content
st.title('Streamlit App with SVG as Page Icon')
st.write("This Streamlit app uses an SVG image as the page icon, converted to PNG.")

# Display the PNG image in the app
st.image(png_image, caption='Logo Image')
