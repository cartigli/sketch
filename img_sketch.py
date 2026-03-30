import os
import cv2
import math

from contextlib import contextmanager

"""
Load a single image in & sketch on it.
"""


def load_img(src):
     """Load an image from the disk into memory."""
     if not os.path.exists(src):
          print(f"No image found at {src}")
          return None

     img = cv2.imread(src)
     if img is None:
          return None

     h, w = img.shape[:2]
     print(f"Loaded image w.dims: {w}x{h}")
     return img


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


def get_clicks(img, win):
     """Watches the image's window & tracks mouse events; records left clicks' positions."""
     points = []

     def mouse_event(click, x, y, flag, params):
          if click != 1:
               return
          points.append((x, y))

     cv2.setMouseCallback(win, mouse_event)

     while len(points) <2:
          cv2.imshow(win, img)

          key = cv2.waitKey(1) & 0xFF

          if key == ord('q'):
               points = [None, None]
               break

     return points


def cv_draw(img, c, d, vrai, win):
     """Draws a line between two points of an image."""
     cv2.line(img, c, d, (0, 0, 255), 3)
     cv2.putText(img, vrai, demi(c, d), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 5)

     cv2.imshow(win, img)
     cv2.waitKey(1)
     return


@contextmanager
def wm(win):
     """Context manager for an image's window being created & destroyed upon return."""
     cv2.namedWindow(win, flags=cv2.WINDOW_FULLSCREEN)
     cv2.setWindowProperty(win, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
     yield win
     cv2.destroyAllWindows()


def main(src):
     minn = 1.0

     img = load_img(src)
     if not img:
          return

     with wm("Select two points w.a known distance: ") as win:
          a, b = get_clicks(img, win)
          if not a:
               return

          lmk_dist = hypo(a, b)

          tru = float(input("Enter the true distance between these points (> 1.0 mm): "))

          if tru <= minn or lmk_dist <= minn*10:
               print("too small of a calibration region")
               return

          pix_per = lmk_dist / tru
          print(f"Calibrated for: {pix_per:.3f} pixels per mm ({pix_per:.3f}=1mm)")

     with wm("Choose two points to find their distance: ") as win:
          while True:
               c, d = get_clicks(img, win)
               if not c:
                    break

               eucl = hypo(c, d)
               vrai = f"{(eucl/pix_per):.3f} mm"

               cv_draw(img, c, d, vrai, win)

               print(f"true distance: {vrai}")


if __name__=="__main__":
     src = "/Volumes/HomeXx/compuir/test.JPG"
     main(src)