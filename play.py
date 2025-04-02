import os
import platform
import subprocess
import time
import signal
import atexit
import sys

VIDEO_FILE1 = "kaya1.mp4"
# VIDEO_FILE1 = "video1.mp4"
VIDEO_FILE2 = "video2.mp4"
DEFAULT_IMAGE = "kapelle.png"  # Default image to show between videos

# Global variable to keep track of background image process
background_process = None

def ensure_display_env():
    """Ensure DISPLAY environment variable is set"""
    my_env = os.environ.copy()
    if "DISPLAY" not in my_env or not my_env["DISPLAY"]:
        my_env["DISPLAY"] = ":0"
    return my_env

def setup_background_image(image_path):
    """Display an image in the background that persists until the script exits"""
    global background_process
    
    if not os.path.exists(image_path):
        print(f"Error: {image_path} not found")
        return None
        
    try:
        # Try feh first (preferred method)
        my_env = ensure_display_env()
        cmd = ["feh", "--fullscreen", image_path]
        
        background_process = subprocess.Popen(
            cmd,
            env=my_env,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE
        )
        
        # Check if process started successfully
        time.sleep(1)
        if background_process.poll() is not None:
            # Process already exited, try VLC
            return setup_background_with_vlc(image_path)
        
        # Register cleanup function
        atexit.register(cleanup_background)
        return background_process
        
    except FileNotFoundError:
        # Feh not installed, try VLC
        return setup_background_with_vlc(image_path)
    except Exception:
        # Any other error, try VLC
        return setup_background_with_vlc(image_path)

def setup_background_with_vlc(image_path):
    """Alternative method using VLC to display background"""
    global background_process
    
    try:
        my_env = ensure_display_env()
        # Use VLC to display the image
        cmd = ["cvlc", "--video-wallpaper", "--no-audio", 
               "--image-duration", "-1", "--loop", image_path]
        
        background_process = subprocess.Popen(
            cmd,
            env=my_env,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE
        )
        
        # Check if process started successfully
        time.sleep(1)
        if background_process.poll() is not None:
            return None
        
        atexit.register(cleanup_background)
        return background_process
    except Exception:
        return None

def cleanup_background():
    """Clean up background process when script exits"""
    global background_process
    if background_process:
        background_process.terminate()
        background_process = None

def play(file_path):
    """Play video file using VLC in fullscreen mode"""
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found")
    else:
        try:
            my_env = ensure_display_env()
            subprocess.run(
                ["cvlc", "--play-and-exit", "--fullscreen", "--no-video-title-show", file_path],
                env=my_env
            )
        except FileNotFoundError:
            print("VLC is not installed. Install it using 'sudo apt install vlc'.")

def display_image(image_path, duration=None):
    """
    Display an image in fullscreen mode
    :param image_path: Path to the image file
    :param duration: How long to display the image in seconds (None = until manually closed)
    """
    if not os.path.exists(image_path):
        print(f"Error: {image_path} not found")
        return

    try:
        # Try using feh first
        my_env = ensure_display_env()
        
        if duration:
            # Display for specific duration
            proc = subprocess.Popen(
                ["feh", "--fullscreen", "--auto-zoom", image_path],
                env=my_env
            )
            time.sleep(duration)
            proc.terminate()
        else:
            # Display until program is interrupted
            subprocess.run(
                ["feh", "--fullscreen", "--auto-zoom", image_path],
                env=my_env
            )
    except FileNotFoundError:
        # Fall back to VLC if feh not available
        try:
            my_env = ensure_display_env()
            if duration:
                subprocess.run(
                    ["cvlc", "--play-and-exit", "--fullscreen", 
                     "--image-duration", str(duration), image_path],
                    env=my_env
                )
            else:
                subprocess.run(
                    ["cvlc", "--play-and-exit", "--fullscreen", 
                     "--image-duration", "-1", image_path],
                    env=my_env
                )
        except FileNotFoundError:
            print("Neither feh nor VLC is installed.")

if __name__ == "__main__":
    # Ensure DISPLAY is set
    os.environ.setdefault("DISPLAY", ":0")
    
    # Setup background image that persists
    bg = setup_background_image(DEFAULT_IMAGE)
    if not bg:
        print("Failed to set up background image.")
    
    time.sleep(2) 
    
    # Play videos
    play(VIDEO_FILE1)
    time.sleep(2) 
    play(VIDEO_FILE2)
    
    # Keep script running to maintain background
    print("Press Ctrl+C to exit...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting...")
        # Cleanup done automatically via atexit
