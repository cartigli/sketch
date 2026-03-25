import os
import math
from contextlib import contextmanager

import cv2


def load_vid():
     """Load a video feed from a cam into memory."""
     cap = cv2.VideoCapture(0)

     ret, f = cap.read()

     if not ret:
          print("Failed to grab frame.")
          return None

     h, w = f.shape[:2]
     print(f"Loaded video feed w.dims: {w}x{h}")
     return cap


def hypo(a, b):
     """Returns the Euclidean distance between two coordinate pairs."""
     x = b[0] - a[0]
     y = b[1] - a[1]
     return math.sqrt(x**2 + y**2)


def demi(a, b):
     """Finds the mdipoint of a given line."""
     x = (a[0] + b[0]) // 2
     y = (a[1] + b[1]) // 2
     return (x, y)


def watch_clicks(cap, win, lines=None):
     """Watches the video feed & tracks mouse events; records left clicks' positions."""
     points = []

     def mouse_event(click, x, y, flag, params):
          if click != 1:
               return
          points.append((x, y))

     cv2.setMouseCallback(win, mouse_event)

     while len(points) < 2:
          ret, f = cap.read()
          if not ret:
               print(f"Failed to grab frame")
               points = [None, None]
               break

          if lines:
               for c, d, vrai in lines:
                    cv2.line(f, c, d, (0, 0, 255), 3)
                    cv2.putText(f, vrai, demi(c, d), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 5)

          cv2.imshow(win, f)
          if cv2.waitKey(1) == ord('q'):
               points = [None, None]
               break

     return points


def cv_sketch(cap, lines, win):
     """Draws a line between two coordinates on a live video feed."""
     ret, f = cap.read()

     for c, d, vrai in lines:
          cv2.line(f, c, d, (0, 0, 255), 3)
          cv2.putText(f, vrai, demi(c, d), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 5)

     cv2.imshow(win, f)
     cv2.waitKey(1)
     return


@contextmanager
def wm(win):
     """Context manager for an image's window being created & destroyed upon return."""
     cv2.namedWindow(win, flags=cv2.WINDOW_FULLSCREEN)
     cv2.setWindowProperty(win, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
     yield win
     cv2.destroyAllWindows()

@contextmanager
def wvm(win):
     """Context manager for an video feed's window being created & destroyed upon return."""
     cv2.namedWindow(win, flags=cv2.WINDOW_FULLSCREEN)
     cv2.setWindowProperty(win, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
     yield win
     cv2.destroyAllWindows()


def main(src):
     cap = load_vid()
     if cap is None:
          return

     with wm("Select two points w.a known distance: ") as win:
          a, b = watch_clicks(cap, win, lines=None)
          if not a:
               return

          tru = float(input("Enter the true distance between these points (mm): "))
          if tru <= 0:
               print("Cannot calibrate on distance of 0 mm or less")
               return

          lmk_dist = hypo(a, b)
          if lmk_dist <= 1.0:
               print("Less than 1 pixel is too small of a calibration region")
               return

          pix_per = lmk_dist / tru
          print(f"Calibrated for: {pix_per:.3f} pixels per mm ({pix_per:.3f}=1mm)")

     with wm("Choose two points to find their distance: ") as win:
          lines = []

          while True:
               c, d = watch_clicks(cap, win, lines)

               if not c:
                    break

               eucl = hypo(c, d)
               vrai = f"{(eucl/pix_per):.3f} mm"

               lines.append((c, d, vrai))

               # cv_sketch(cap, lines, win)
               print(f"true distance: {vrai}")

          cap.release()


if __name__=="__main__":
     src = "/Volumes/HomeXx/compuir/test.JPG"
     main(src)