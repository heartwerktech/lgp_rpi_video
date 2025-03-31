import os
import platform
import subprocess
import time
import signal
import atexit
import sys

VIDEO_FILE1 = "video1.mp4"
VIDEO_FILE2 = "video2.mp4"
DEFAULT_IMAGE = "kapelle.png"  # Default image to show between videos

# Global variable to keep track of background image process
background_process = None

def setup_background_image(image_path):
    """
    Display an image in the background that persists until the script exits
    """
    global background_process
    
    if not os.path.exists(image_path):
        print(f"ERROR: {image_path} not found in the current directory: {os.getcwd()}")
        return None
        
    # Print debugging info
    print(f"Setting up background image: {image_path}")
    print(f"Current directory: {os.getcwd()}")
        
    try:
        # First try a much simpler approach - just using feh to directly display the image
        # This is the most reliable method
        my_env = os.environ.copy()
        if "DISPLAY" not in my_env or not my_env["DISPLAY"]:
            my_env["DISPLAY"] = ":0"
        
        print(f"Using DISPLAY={my_env['DISPLAY']}")
        
        # Try a simpler command with fewer options
        cmd = ["feh", "--fullscreen", image_path]
        print(f"Running command: {' '.join(cmd)}")
        
        background_process = subprocess.Popen(
            cmd,
            env=my_env,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE
        )
        
        # Check if process started successfully
        time.sleep(1)
        if background_process.poll() is not None:
            # Process already exited, get error message
            _, stderr = background_process.communicate()
            print(f"Error starting feh: {stderr.decode()}")
            
            # Try alternative method with VLC
            return setup_background_with_vlc(image_path)
        
        # Register cleanup function
        atexit.register(cleanup_background)
        print("Background image setup successfully")
        return background_process
        
    except FileNotFoundError:
        print("feh is not installed. Trying alternative with VLC...")
        return setup_background_with_vlc(image_path)
    except Exception as e:
        print(f"Error setting up background with feh: {str(e)}")
        return setup_background_with_vlc(image_path)

def setup_background_with_vlc(image_path):
    """Alternative method using VLC to display background"""
    global background_process
    
    print("Attempting to set up background with VLC...")
    try:
        my_env = os.environ.copy()
        if "DISPLAY" not in my_env or not my_env["DISPLAY"]:
            my_env["DISPLAY"] = ":0"
            
        # Use VLC to display the image
        cmd = ["cvlc", "--video-wallpaper", "--no-audio", 
               "--image-duration", "-1", "--loop", image_path]
        print(f"Running VLC command: {' '.join(cmd)}")
        
        background_process = subprocess.Popen(
            cmd,
            env=my_env,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE
        )
        
        # Check if process started successfully
        time.sleep(1)
        if background_process.poll() is not None:
            # Process already exited
            _, stderr = background_process.communicate()
            print(f"Error starting VLC: {stderr.decode()}")
            return None
        
        atexit.register(cleanup_background)
        print("Background image setup with VLC successfully")
        return background_process
    except Exception as e:
        print(f"Error setting up background with VLC: {str(e)}")
        return None

def cleanup_background():
    """Clean up background process when script exits"""
    global background_process
    if background_process:
        print("Cleaning up background process...")
        background_process.terminate()
        background_process = None

def play(file_path):
    if not os.path.exists(file_path):
        print(f"{file_path} not found in the current directory: {os.getcwd()}")
    else:
        print(f"Playing video: {file_path}")
        try:
            # Set environment variables for VLC
            my_env = os.environ.copy()
            if "DISPLAY" not in my_env or not my_env["DISPLAY"]:
                my_env["DISPLAY"] = ":0"
            
            print(f"Using DISPLAY={my_env['DISPLAY']} for video playback")
            
            # Run VLC with overlay on top of background
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
        print(f"{image_path} not found in the current directory: {os.getcwd()}")
        return

    print(f"Displaying image: {image_path}" + (f" for {duration} seconds" if duration else ""))
    
    try:
        # Set environment variables
        my_env = os.environ.copy()
        if "DISPLAY" not in my_env or not my_env["DISPLAY"]:
            my_env["DISPLAY"] = ":0"
        
        print(f"Using DISPLAY={my_env['DISPLAY']}")
        
        # If duration is specified, display for that duration then exit
        if duration:
            # feh with auto-zoom and fullscreen
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
        print("feh is not installed. Using VLC as fallback...")
        try:
            # Try using VLC as a fallback
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
    print(f"Starting script with Python {sys.version}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Environment DISPLAY: {os.environ.get('DISPLAY', 'Not set')}")
    
    # Try to ensure DISPLAY is set
    if "DISPLAY" not in os.environ or not os.environ["DISPLAY"]:
        os.environ["DISPLAY"] = ":0"
        print("Set DISPLAY=:0")
    
    # Setup background image that persists
    bg = setup_background_image(DEFAULT_IMAGE)
    if not bg:
        print("Failed to set up background image. Continuing without background.")
    
    time.sleep(2) 
    
    # Now play videos - they will appear on top of the background
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
