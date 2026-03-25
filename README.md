SKETCH is designed to allow the user to calibrate and draw lines on a given image or video feed.

Required Packages:
cv2 (pip install opencv-python)

## USE
Calibration:
Run the program and draw a line across an object of known length (i.e., a ruler) and define the length of line. The window will close and the program will calculate the pixels per mm of the distance you entered.

Sketching:
After calibration, the window will reappear. Lines drawn on the new window have their dimensions defined at their midpoint and have previews shown when placing/positioning. 

Errors:
To remove an anchor of a new line (i.e., you started a line you don't want to finish), right click inside the window to undo the point. To undo the entire last line you drew (not the last point made), right click inside the window.

Misc:
To change the source of the video feed from the default webcam to something like an external-usb webcam, find the device's reference no. and change it in the vid_cali script (line 9: [cap = cv2.VideoCapture(0)] -> [cap = cv2.VideoCapture(2)]). To find your devices' reference no., use lsusb (Linux) and find your device on the returned list.