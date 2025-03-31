import cv2
import numpy as np
import time
import os
from ffpyplayer.player import MediaPlayer
from typing import Optional

# --- Constants ---
DEFAULT_FPS = 30
SYNC_THRESHOLD_SEC = 0.01 # Sync if video is ahead by more than 10ms
MIN_WAIT_MS = 1

def play_video_with_audio(video_path: str, window_name: str = "Video") -> None:
    """
    Plays a video file with audio using OpenCV for video and ffpyplayer for audio.
    Attempts synchronization based on player PTS. Resources are cleaned up automatically.

    Args:
        video_path: Path to the video file.
        window_name: Name for the OpenCV display window.
    """
    video: Optional[cv2.VideoCapture] = None
    player: Optional[MediaPlayer] = None
    window_created = False

    try:
        # --- Initialization ---
        video = cv2.VideoCapture(video_path)
        if not video.isOpened():
            raise IOError(f"Error: Could not open video '{video_path}'")

        try:
            player = MediaPlayer(video_path)
            audio_enabled = True
            print(f"Audio enabled for '{video_path}'")
        except Exception as e:
            print(f"Warning: Error initializing audio player for '{video_path}': {e}. Proceeding without audio sync.")
            audio_enabled = False
            player = None # Ensure player is None if init fails

        fps = video.get(cv2.CAP_PROP_FPS)
        if fps <= 0:
            print(f"Warning: Could not read FPS from video. Using default: {DEFAULT_FPS}")
            fps = DEFAULT_FPS
        base_frame_delay_ms = int(1000 / fps)

        # --- Window Setup ---
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        window_created = True
        # Attempt fullscreen - may depend on backend/window manager
        cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        # A short wait might help the window manager apply the property
        cv2.waitKey(50) # Reduced wait time

        print(f"Playing '{os.path.basename(video_path)}' (FPS: {fps:.2f}). Press 'q' or ESC to quit.")

        # --- Main Playback Loop ---
        fullscreen_set_in_loop = False # Flag to try setting fullscreen again
        while True:
            grabbed, frame = video.read()
            if not grabbed:
                print("End of video stream.")
                break # Exit loop normally

            current_wait_ms = base_frame_delay_ms

            # --- Audio Sync Logic ---
            if audio_enabled and player:
                audio_pts: Optional[float] = None
                try:
                    audio_frame, val = player.get_frame(show=False)

                    if val == 'eof':
                        print("End of audio stream.")
                        if player: player.close_player() # Close early
                        player = None
                        audio_enabled = False # Stop trying audio sync
                    elif audio_frame is not None:
                        audio_pts = player.get_pts() # Time in seconds
                    # If val is not 'eof' and audio_frame is None, might be buffering. Use base delay.
                    # If val is None, an issue might have occurred. Use base delay.

                except Exception as e:
                    print(f"Error during audio processing: {e}. Disabling audio sync.")
                    if player: player.close_player()
                    player = None
                    audio_enabled = False

                # --- Adjust wait time based on sync ---
                if audio_pts is not None:
                    video_pts_msec = video.get(cv2.CAP_PROP_POS_MSEC)
                    video_pts = video_pts_msec / 1000.0 if video_pts_msec > 0 else 0
                    delay = video_pts - audio_pts # Positive if video is ahead

                    if delay > SYNC_THRESHOLD_SEC: # Video is ahead, wait longer
                        current_wait_ms = max(MIN_WAIT_MS, int(delay * 1000))
                    else: # Video is behind or synced, proceed quickly
                        current_wait_ms = MIN_WAIT_MS

            # --- Display Frame and Handle Input ---
            cv2.imshow(window_name, frame)

            # Try setting fullscreen again after showing the first frame
            if not fullscreen_set_in_loop:
                cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
                cv2.waitKey(1) # Short delay might help
                fullscreen_set_in_loop = True

            key = cv2.waitKey(max(MIN_WAIT_MS, current_wait_ms)) & 0xFF
            if key == ord('q') or key == 27: # 27 is ESC key
                print("Playback interrupted by user.")
                break # Exit loop

    except IOError as e: # Handle errors opening video
        print(e)
    except cv2.error as e: # Handle OpenCV specific errors
        print(f"OpenCV error during playback: {e}")
    except Exception as e: # Catch other unexpected errors
         print(f"An unexpected error occurred during playback: {e}")
    finally:
        # --- Cleanup ---
        print("Cleaning up resources...")
        if video is not None and video.isOpened():
            video.release()
        if player is not None:
            try:
                player.close_player()
            except Exception as e:
                print(f"Error closing audio player: {e}")
        if window_created:
            cv2.destroyWindow(window_name)
            cv2.waitKey(1) # Allow window system to process close event

def main() -> None:
    print("Playing videos with audio sync attempt:\n")

    # Ensure video files are in the same directory or provide full paths
    script_dir = os.path.dirname(__file__)
    # Define video files as raw filenames
    video_filenames = [
        "video2.mp4",
        "video1.mp4",
        "video2.mp4",
        "video1.mp4",
    ]

    # Construct full paths and filter for existing files
    valid_videos = []
    for filename in video_filenames:
        full_path = os.path.join(script_dir, filename)
        if os.path.exists(full_path):
            valid_videos.append(full_path)
        else:
            print(f"Warning: Video file not found: {full_path}. Skipping.")


    if not valid_videos:
        print("No valid video files found in the list.")
        return

    print(f"Found {len(valid_videos)} video files to play.")

    for i, video_file in enumerate(valid_videos):
        window_title = f"Video Player - {os.path.basename(video_file)}"
        print(f"--- Playing {os.path.basename(video_file)} ({i+1}/{len(valid_videos)}) --- ")
        try:
            play_video_with_audio(video_file, window_title)
        except Exception as e: # Catch errors from play_video_with_audio if they escape its own try/except
            print(f"Critical error during playback attempt of {os.path.basename(video_file)}: {e}")
            # Ensure window is destroyed if play_video_with_audio failed badly
            cv2.destroyWindow(window_title)
            cv2.waitKey(1)
        print(f"--- Finished {os.path.basename(video_file)} ---\n")

    print("All playback attempts completed!")
    # Final cleanup just in case any window lingered
    cv2.destroyAllWindows()
    cv2.waitKey(1)

if __name__ == '__main__':
    main()