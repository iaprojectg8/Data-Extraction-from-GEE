import os
import subprocess
import streamlit as st


def callback_click():
    st.session_state.launched = 1
    st.session_state.kill=0
    st.session_state.process = subprocess.Popen(
            ['python', 'subprocess_script.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True  # This makes sure the output is read as text instead of bytes
        )

def callback_kill():
    st.session_state.kill = 1
    st.session_state.launched = 0
    st.session_state.process.terminate()
    

def main():

    if "launched" not in st.session_state:
        st.session_state.launched = 0
    if "kill" not in st.session_state:
        st.session_state.kill = 0
    if "process" not in st.session_state:
        st.session_state.process = 0
    # Create a Streamlit progress bar
    progress_bar = st.progress(0)
    progress_text = st.empty()

    st.button("Click", on_click=callback_click)
    st.button("Kill", on_click=callback_kill)
        # Launch subprocess with a timeout
    
    if st.session_state.launched:

        # Read progress updates from the subprocess
        for line in st.session_state.process.stdout:
            st.write(f"Received line: {line.strip()}")  # Debug: Show received lines
            
                
            try:
                progress = int(line.strip())*10
                progress_bar.progress(progress)
                progress_text.text(f"Progress: {progress}%")
                if progress >= 100:
                    break
            except ValueError:
                st.write(f"ValueError: Could not convert {line.strip()} to int")  # Debug: Show conversion errors
                print()
                continue
        
    print(st.session_state.process.poll())
    print(st.session_state.process.wait())


if __name__ == "__main__":
    main()