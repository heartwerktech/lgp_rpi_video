import cv2
import numpy as np
import time
import os
from ffpyplayer.player import MediaPlayer

def play_video_with_audio(video_path, window_name="Video"):
	"""
	Play a video with audio in fullscreen mode
	"""
	# Create a named window in fullscreen mode
	cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
	cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
	
	# Open video file with both OpenCV and ffpyplayer
	video = cv2.VideoCapture(video_path, cv2.CAP_FFMPEG)
	player = MediaPlayer(video_path)
	
	if not video.isOpened():
		print(f"Error: Could not open video {video_path}")
		return
	
	fps = video.get(cv2.CAP_PROP_FPS)
	delay = int(1000 / fps)
	
	while True:
		ret, frame = video.read()
		audio_frame, val = player.get_frame()
		
		if not ret:
			print("End of video")
			break
			
		# Display the frame
		cv2.imshow(window_name, frame)
		
		# If audio frame is available, determine the delay for proper synchronization
		if val != 'eof' and audio_frame is not None:
			img, t = audio_frame
			# Wait for the proper amount of time
			sync_delay = int(delay - t * 1000) if t * 1000 < delay else 1
			sync_delay = max(1, sync_delay)  # Ensure delay is at least 1ms
		else:
			sync_delay = delay
			
		# Exit if 'q' or 'ESC' is pressed
		key = cv2.waitKey(sync_delay) & 0xFF
		if key == ord('q') or key == 27:  # 27 is ESC key
			break
			
	# Clean up
	video.release()
	cv2.destroyWindow(window_name)

def load_video(path):
	my_video = cv2.VideoCapture(path, cv2.CAP_FFMPEG)

	# Need to cast these values to int to pass them as parameters for numpy
	frameCount = int(my_video.get(cv2.CAP_PROP_FRAME_COUNT))
	frameWidth = int(my_video.get(cv2.CAP_PROP_FRAME_WIDTH))
	frameHeight = int(my_video.get(cv2.CAP_PROP_FRAME_HEIGHT))
	fps = my_video.get(cv2.CAP_PROP_FPS)

	buf = np.empty((frameCount, frameHeight, frameWidth, 3), np.dtype('uint8'))

	cur_frame = 0
	ret = True

	print(f"Loading video: {path}")
	while cur_frame < frameCount and ret:
	    # read() returns two values
	    # - ret: False if there was a problem getting a new frame
	    #		(end of file or an error)
	    # - frame: A new frame
		ret, frame = my_video.read()
		if ret:
			buf[cur_frame] = frame
			cur_frame += 1

	# Release the VideoCapture since we don't need it anymore
	my_video.release()
	
	print(f"Video {path}, fully loaded\n")

	return buf, fps

def play_video(video_buffer, fps, window_name="Video"):
	"""
	Play a video from a buffer of frames in fullscreen mode
	"""
	# Create a named window in fullscreen mode
	cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
	cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
	
	# Calculate delay between frames in milliseconds
	delay = int(1000 / fps)
	
	for i, frame in enumerate(video_buffer):
		cv2.imshow(window_name, frame)
		
		# Wait for 'delay' milliseconds between frames
		# Exit if 'q' or 'ESC' is pressed
		key = cv2.waitKey(delay) & 0xFF
		if key == ord('q') or key == 27:  # 27 is ESC key
			break
	
	cv2.destroyWindow(window_name)

def main():
	print("Loading and playing videos:\n")

	# Check if we should use preloaded mode (no audio) or direct playback (with audio)
	use_audio = True
	
	if use_audio:
		# Play videos directly with audio
		print("Playing video1 with audio...")
		play_video_with_audio("video1.mp4", "Video 1")
		
		print("Playing video2 with audio...")
		play_video_with_audio("video2.mp4", "Video 2")
	else:
		# Original preloaded video approach (no audio)
		video1, fps1 = load_video("video1.mp4")
		video2, fps2 = load_video("video2.mp4")
		
		print("All videos loaded.")
		
		print("Playing video1...")
		play_video(video1, fps1, "Video 1")
		
		print("Playing video2...")
		play_video(video2, fps2, "Video 2")
	
	print("Playback completed!")
	cv2.destroyAllWindows()

if __name__ == '__main__':
	main()