import time
import math
import threading
from contextlib import contextmanager

import cv2
import numpy as np

"""
Stream a device's video output & draw in real time on the output.

The calibration data from opencv's calibration module is loaded & applied 
to the image to obtain the corrected reprojection, if applicable.
"""


class Stream:
     """Initiates video stream & starts thread to grab frames in the bg."""

     def __init__(self, src=0, bfsz=1, cald=None, thread=True):
          """Initiates the video capture source, sets buffer, initiates thread, and unpacks reprojections.
          Defaults: source=built-in cam, buffer=1, calibration=none, threading=enabled
          """
          self.cap = cv2.VideoCapture(src, cv2.CAP_V4L2)
          self.cap.set(cv2.CAP_PROP_BUFFERSIZE, bfsz)
          self.ret, self.f = self.cap.read()

          self.thread = thread

          if self.thread:
               self._lock = threading.Lock()
               self._stopped = False
               threading.Thread(target=self._update, daemon=True).start()
          else:
               self._lock = None

          if cald:
               self.cal = np.load(cald)
               self.map_x, self.map_y = self.cal["map_x"], self.cal["map_y"]
          else:
               self.cal = None

     def _update(self):
          """Threaded method for grabbing frames in the bg."""
          while not self._stopped:
               ret, f = self.cap.read()
               with self._lock:
                    self.ret, self.f = ret, f

     def read(self):
          """Grabs the most recent frame from threaded process (if threading).
          Applies the calibration reprojection if present.
          """
          if self.thread:
               with self._lock:
                    if not self.ret:
                         return None, None
                    if self.cal:
                         fcal = cv2.remap(self.f.copy(), self.map_x, self.map_y, cv2.INTER_LINEAR)
                         return self.ret, fcal
                    return self.ret, self.f.copy()
          else:
               if not self.ret:
                    return None, None
               if self.cal:
                    fcal = cv2.remap(self.f.copy(), self.map_x, self.map_y, cv2.INTER_LINEAR)
                    return self.ret, fcal
               return self.ret, self.f.copy()

     def kill(self):
          """Stops the threaded process and releases the video capture generator."""
          if self.thread:
               self._stopped = True
          self.cap.release()


def hypo(a, b):
     """Returns the Euclidean distance between two coordinate pairs."""
     x = b[0] - a[0]
     y = b[1] - a[1]
     return math.sqrt(x**2 + y**2)


def demi(a, b):
     """Finds the midpoint of two coordinate pairs."""
     x = (a[0] + b[0]) // 2
     y = (a[1] + b[1]) // 2
     return (x, y)


def verify(a, b):
     """Verify the points chosen (and their distance) are meet the minimum acceptable distances."""
     tru = float(input("Enter the distance between these points (mm): "))
     lmk_dist = hypo(a, b)
     pix_per = lmk_dist / tru

     if tru <= 1.0 or lmk_dist <= 1.0:
          print("too small of a calibration region")
          return None

     print(f"calibrated: {pix_per:.3f} pixels per mm")
     return pix_per


def artist(bg, x, y, text=None, crosshairs=False):
     """Draws lines between coordinates pairs, and text + crosshairs if applicable."""
     cv2.line(bg, x, y, (0, 0, 255), 2)
     if text:
          cv2.putText(bg, text, demi(x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
     if crosshairs:
          size = 4
          for e, f in (x, y):
               cv2.line(bg, (e-size, f), (e+size, f), (0, 255, 0), 1)
               cv2.line(bg, (e, f-size), (e, f+size), (0, 255, 0), 1)


def watch_clicks(stream, win, pix_per, lines=None, chain=False):
     """Watches the video feed & tracks mouse events.
     Records the left clicks & quit mechanisms."""
     points = []
     live = None

     def mouse_event(event, x, y, flag, params):
          """Handle & check mouse events for relevant clicks."""
          nonlocal live
          if event == cv2.EVENT_LBUTTONDOWN:
               points.append((x, y))
          elif event == cv2.EVENT_RBUTTONDOWN:
               if points:
                    lines.pop()
               elif lines:
                    lines.pop() # clear the last created line
               else:
                    points.clear() # erase last selection
          elif event == cv2.EVENT_MOUSEMOVE:
               live = (x, y)

     cv2.setMouseCallback(win, mouse_event)

     if lines and chain:
          points.append(lines[-1][1])

     while len(points) < 2:
          ret, f = stream.read()
          if not ret:
               return (None, None)

          if lines:
               for c, d, vrai in lines:
                    artist(f, c, d, vrai, crosshairs=True)
          if len(points) == 1 and live and pix_per:
               artist(f, points[0], live, text=f"{(hypo(points[0], live)/pix_per):.3f} mm", crosshairs=True)
          elif len(points) == 1 and live and not pix_per:
               artist(f, points[0], live, crosshairs=True)

          cv2.imshow(win, f)
          key = cv2.waitKey(1)

          if key == ord('q') or key == 27:
               print("user quit")
               return (None, None)
          elif key == ord('c'):
               print(f"user set chain: {not chain}")
               chain = not chain
               if chain:
                    if lines and not points:
                         points.append(lines[-1][1])
               if not chain:
                    points.clear()

     return points, chain


@contextmanager
def wm(win):
     """Context manager for an image's window being created & destroyed upon return."""
     cv2.namedWindow(win, flags=cv2.WINDOW_FULLSCREEN)
     cv2.setWindowProperty(win, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
     yield win
     cv2.destroyAllWindows()


def main(src=0, cald=None):
     pix_per = None
     stream = Stream(src=src, cald=cald)

     with wm("Select two points w.a known distance: ") as win:
          points, _ = watch_clicks(stream, win, pix_per)
          stream.kill()
          if not points:
               return

     pix_per = verify(*points)
     if not pix_per:
          return

     flood = Stream(src=src, cald=cald)
     with wm("Choose two points to find their distance: ") as win:
          chain = True
          lines = []
          while True:
               points, chain = watch_clicks(flood, win, pix_per, lines, chain)
               if not points:
                    break

               eucl = hypo(*points)
               vrai = f"{(eucl / pix_per):.3f} mm"

               print(f"true distance: {vrai}")
               lines.append((*points, vrai))

          flood.kill()


if __name__=="__main__":
     main(src=0)