import os
import platform
import subprocess
import time

VIDEO_FILE1 = "video1.mp4"
VIDEO_FILE2 = "video2.mp4"

def play(file_path):
    if not os.path.exists(file_path):
        print(f"{VIDEO_FILE1} not found in the current directory.")
    else:
        try:
            subprocess.run(["cvlc", "--play-and-exit", "--fullscreen", file_path])
        except FileNotFoundError:
            print("VLC is not installed. Install it using 'sudo apt install vlc'.")

if __name__ == "__main__":
    play(VIDEO_FILE1)   
    
    # Wait for 3 seconds before playing the next video
    time.sleep(3)
    
    # Play video2.mp4 after the first video finishes
    play(VIDEO_FILE2)
