import os
import subprocess
import streamlit as st

def main():
    # Create a Streamlit progress bar
    progress_bar = st.progress(0)
    progress_text = st.empty()

    if st.button("Click"):
        # Launch subprocess with a timeout
    
        process = subprocess.Popen(
            ['python', 'subprocess_script.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True  # This makes sure the output is read as text instead of bytes
        )

        # Read progress updates from the subprocess
        for line in process.stdout:
            st.write(f"Received line: {line.strip()}")  # Debug: Show received lines
            try:
                progress = int(line.strip())*10
                progress_bar.progress(progress)
                progress_text.text(f"Progress: {progress}%")
                if progress >= 100:
                    break
            except ValueError:
                st.write(f"ValueError: Could not convert {line.strip()} to int")  # Debug: Show conversion errors
                continue
        print(" First wait", process.wait())
        print(process.poll())
        print(" Second wait", process.wait())
        # process.stdout.close()
        # process.stderr.close()
        print(process.poll())
        print("Third wait", process.wait())


if __name__ == "__main__":
    main()