import os
import cv2
import numpy as np


"""
Calibrates a camera's intrinsic matrix & saves the values needed for reprojection.

Uses OpenCV's Camera Calibration module, specifically with their 9x6 checkerboard pattern.
After printing their pattern, the squares measured to be ~16 mm across.
"""

ROWS = 9 # corners (vertical)
COLS = 6 # corners (horizontal)
SQUARE_SIZE = 16 # each square's size (mm)


def main(src):
     objp = np.zeros((ROWS * COLS, 3) ,np.float32)
     objp[:, :2] = np.mgrid[0:COLS, 0:ROWS].T.reshape(-1, 2) * SQUARE_SIZE

     obj_points = []
     img_points = []

     pixels = None
     gray = None
     pos = 0
     neg = 0

     for path in os.scandir(src):
          _, sfx = os.path.splitext(path)
          if sfx in (".JPG", ".png"):
               img = cv2.imread(path)
               gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

               if (neg + pos) == 0:
                    h, w = img.shape[:2]
                    pixels = h*w
                    print(f"loaded first img w.dims: {w}x{h}")

               found, corners = cv2.findChessboardCorners(gray, (COLS, ROWS), None
                    # cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_NORMALIZE_IMAGE
                    )

               if found:
                    pos += 1
                    refined = cv2.cornerSubPix(
                         gray, corners, (15, 15), (-1, -1),
                         (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
                         )

                    obj_points.append(objp)
                    img_points.append(refined)
                    print(f"\033[32mfound board! ({path.path})\033[0m")
               else:
                    neg += 1
                    print(f"\033[31mno board found ({path.path})\033[0m")

     ret, camera_matrix, dist_coeffs, rvecs, tvecs = cv2.calibrateCamera(
          obj_points, img_points, gray.shape[::-1], None, None
          # flags=cv2.CALIB_RATIONAL_MODEL
          )

     print(f"Board detection rate: {(100*(pos/(neg+pos))):.2f}% boards detected [of {neg+pos} images]")
     print(f"Reprojection error: {ret:.3f} pixels (mse)") # ret = overall prediction error (squared) per-point in pixels
     if pixels:
          print(f"Error proportional to resolution: {(ret/pixels):.12f} ({pixels} pixels)")

     h, w = gray.shape
     new_matrix, roi = cv2.getOptimalNewCameraMatrix(
          camera_matrix, dist_coeffs, (w, h), 1, (w, h)
          )

     map_x, map_y = cv2.initUndistortRectifyMap(
          camera_matrix, dist_coeffs, None, new_matrix, (w, h), cv2.CV_32FC1
          )

     np.savez("calibration.npz",
          camera_matrix = camera_matrix,
          dist_coeffs=dist_coeffs,
          new_matrix=new_matrix,
          map_x=map_x,
          map_y=map_y,
          roi=roi
          )


if __name__ == "__main__":
     # src = "/home/t/calgp2"
     src = "/home/t/cali.A1"
     main(src)