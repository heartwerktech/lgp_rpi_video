import cv2
import numpy as np
import time

class VideoProcessor:
	def __init__(self, path):
		self.path = path
		self.video = None
		self.frame_count = 0
		self.width = 0
		self.height = 0
		
	def open(self):
		"""Open the video file and get its properties"""
		self.video = cv2.VideoCapture(self.path, cv2.CAP_FFMPEG)
		
		if not self.video.isOpened():
			raise ValueError(f"Could not open video file: {self.path}")
			
		# Get video properties
		self.frame_count = int(self.video.get(cv2.CAP_PROP_FRAME_COUNT))
		self.width = int(self.video.get(cv2.CAP_PROP_FRAME_WIDTH))
		self.height = int(self.video.get(cv2.CAP_PROP_FRAME_HEIGHT))
		
		print(f"Opened video: {self.path} ({self.frame_count} frames, {self.width}x{self.height})")
		return self
		
	def get_frame(self, frame_idx):
		"""Get a specific frame by its index"""
		if frame_idx >= self.frame_count:
			return None
			
		# Set position to the requested frame
		self.video.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
		ret, frame = self.video.read()
		
		if not ret:
			return None
			
		return frame
		
	def frames(self):
		"""Generator that yields frames one at a time"""
		# Reset to the beginning of the video
		self.video.set(cv2.CAP_PROP_POS_FRAMES, 0)
		
		print(f"Processing video: {self.path}")
		for i in range(self.frame_count):
			ret, frame = self.video.read()
			if not ret:
				break
			yield frame
			
		print(f"Finished processing video: {self.path}")
			
	def close(self):
		"""Release the video resource"""
		if self.video is not None:
			self.video.release()
			self.video = None

def process_videos(video_paths):
	"""Process multiple videos without loading them entirely into memory"""
	results = []
	
	for path in video_paths:
		processor = VideoProcessor(path).open()
		
		# Here you can process frames one by one instead of loading all at once
		# For example, you might collect statistics or analyze each frame
		frame_count = 0
		for frame in processor.frames():
			# Process the frame here
			frame_count += 1
			
		processor.close()
		results.append({
			'path': path,
			'frame_count': frame_count,
			'width': processor.width,
			'height': processor.height
		})
		
	return results

def main():
	print("Processing videos:\n")
	
	results = process_videos(["video1.mp4", "video2.mp4"])
	
	for result in results:
	# Need to cast these values to int to pass them as parameters for numpy
	frameCount = int(my_video.get(cv2.CAP_PROP_FRAME_COUNT))
	frameWidth = int(my_video.get(cv2.CAP_PROP_FRAME_WIDTH))
	frameHeight = int(my_video.get(cv2.CAP_PROP_FRAME_HEIGHT))

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
		buf[cur_frame] = frame
		cur_frame += 1

	# Release the VideoCapture since we don't need it anymore
	my_video.release()
	
	print(f"Video {path}, fully loaded\n")

	return buf

def main():
	print("Loading videos:\n")

	video1 = load_video("video1.mp4")
	video2 = load_video("video2.mp4")

	print("All videos loaded.")

	print("Pausing a bit so you can read the memory usage :'D")
	time.sleep(5)
	print("Bisous, bbye!\n")

if __name__ == '__main__':
	main()