import cv2
import numpy as np
import glob

"""
Calibrates a camera's intrinsic matrix & saves the values needed for reprojection.

Uses OpenCV's Camera Calibration module, specifically with their 9x6 checkerboard pattern.
"""

ROWS = 6 # corners (vertical)
COLS = 9 # corners (horizontal)
SQUARE_SIZE = 23 # each square's size (mm)


def main(cimgs):
     objp = np.zeros((ROWS * COLS, 3) ,np.float32)
     objp[:, :2] = np.mgrid[0:COLS, 0:ROWS].T.reshape(-1, 2) * SQUARE_SIZE

     obj_points = []
     img_points = []

     images = glob.glob(cimgs)
     gray = None

     for path in images:
          img = cv2.imread(path)
          gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

          found, corners = cv2.findChessboardCorners(gray, (COLS, ROWS), None)

          print(f"{path}: found={found}, shape={gray.shape}")

          if found:
               refined = cv2.cornerSubPix(
                    gray, corners, (11, 11), (-1, -1),
                    (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
               )
               obj_points.append(objp)
               img_points.append(refined)
          else:
               print(f"Board not found in {path}; skipping")

     ret, camera_matrix, dist_coeffs, rvecs, tvecs = cv2.calibrateCamera(
          obj_points, img_points, gray.shape[::-1], None, None
     )

     print(f"Reprojection error: {ret}") # ret = overall prediction error in pixels

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
     cimgs = "/home/t/cali.A1/*.png"
     main(cimgs)