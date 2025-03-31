import os
import platform
import subprocess

VIDEO_FILE = "video1.mp4"

def play_with_omxplayer(file_path):
    try:
        subprocess.run(["omxplayer", file_path])
    except FileNotFoundError:
        print("omxplayer is not installed. Try using VLC instead.")

def play_with_vlc(file_path):
    try:
        subprocess.run(["cvlc", "--play-and-exit", file_path])
    except FileNotFoundError:
        print("VLC is not installed. Install it using 'sudo apt install vlc'.")

if __name__ == "__main__":
    if not os.path.exists(VIDEO_FILE):
        print(f"{VIDEO_FILE} not found in the current directory.")
    else:
        play_with_vlc(VIDEO_FILE)
        # play_with_omxplayer(VIDEO_FILE)
