import streamlit as st
import cv2
import numpy as np
import tempfile
import time

# GUI Configuration
st.set_page_config(page_title="Object Tracking App", 
                   layout="wide",
                   page_icon=":guardsman:")

st.title("Object Tracking with Background Subtraction")
st.markdown("""
This application allows you to upload a video file and perform object tracking using background subtraction. The original video frames and the processed frames with detected objects will be displayed side by side.
""")

# Function to convert image to RGB format
def convert_img(img):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return img

# File uploader
uploaded_file = st.file_uploader("Upload a Video", type=["mp4", "avi", "mov"])

if uploaded_file is not None:
    tfile = tempfile.NamedTemporaryFile(delete=False)
    tfile.write(uploaded_file.read())
    tfile.close()
    
    # Read the video file
    captures = cv2.VideoCapture(tfile.name)
    
    if not captures.isOpened():
        st.error("Error opening video file.")
    else:
        # Sliders for customization
        rectangle_color = st.color_picker("Select Rectangle Color", "#FF0000")
        playback_speed = st.slider("Select Playback Speed (ms)", min_value=1, max_value=100, value=30)
        
        # Convert color from hex to BGR
        rect_color_bgr = tuple(int(rectangle_color.lstrip("#")[i:i+2], 16) for i in (4, 2, 0))
        
        # Video placeholders
        col1, col2 = st.columns(2)
        stframe_original = col1.empty()
        stframe_processed = col2.empty()
        progress_bar = st.empty()  # Placeholder for progress bar
        remaining_time_text = st.empty()  # Placeholder for remaining time text
        
        back_subtractor = cv2.createBackgroundSubtractorMOG2()
        total_frames = int(captures.get(cv2.CAP_PROP_FRAME_COUNT))
        frame_rate = captures.get(cv2.CAP_PROP_FPS)
        duration = total_frames / frame_rate
        
        frame_count = 0
        
        # Stop button
        stop_button = st.button("Stop Video")
        
        while captures.isOpened():
            if stop_button:
                st.warning("Video processing stopped by user.")
                progress_bar.empty()  # Remove progress bar
                remaining_time_text.empty()  # Remove remaining time text
                break

            ret, frame = captures.read()
            if not ret:
                st.warning("End of video file.")
                progress_bar.empty()  # Remove progress bar
                remaining_time_text.empty()  # Remove remaining time text
                break
            
            fg_mask = back_subtractor.apply(frame)
            contours, _ = cv2.findContours(fg_mask, 
                                           cv2.RETR_EXTERNAL,
                                           cv2.CHAIN_APPROX_SIMPLE)
            for contour in contours:
                if cv2.contourArea(contour) > 300:
                    x, y, w, h = cv2.boundingRect(contour)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), rect_color_bgr, 2)
            
            # Update video frames
            stframe_original.image(convert_img(frame), channels="RGB")
            stframe_processed.image(convert_img(fg_mask), channels="RGB")
            
            # Update progress bar
            frame_count += 1
            progress_bar.progress(frame_count / total_frames)
            
            # Calculate and update remaining time outside the loop
            elapsed_time = frame_count / frame_rate
            remaining_time = max(0, duration - elapsed_time)
            remaining_time_text.text(f"Remaining Time: {remaining_time:.2f} seconds")
            
            # Sleep for playback speed
            time.sleep(playback_speed / 1000)
        
        captures.release()
        st.success("Video processing completed.")