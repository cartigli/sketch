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
     """Returns the Euclidean distance between two coordinates."""
     x = b[0] - a[0]
     y = b[1] - a[1]
     return math.sqrt(x**2 + y**2)


def demi(a, b):
     """Finds the mdipoint of two coordinates."""
     x = (a[0] + b[0]) // 2
     y = (a[1] + b[1]) // 2
     return (x, y)


def verify(a, b):
     """Verify that the points chosen and their distance are acceptable."""
     tru = float(input("Enter the distance between these points (mm): "))
     lmk_dist = hypo(a, b)
     pix_per = lmk_dist / tru

     if tru <= 1.0 or lmk_dist <= 1.0:
          print("too small of a calibration region")
          return None
     print(f"Calibrated for: {pix_per:.3f} pixels per mm ({pix_per:.3f}=1mm)")

     return pix_per


def artist(bg, x, y, text=None):
     """Draws lines between coordinates pairs, with text if present."""
     cv2.line(bg, x, y, (0, 0, 255), 2)
     if text:
          cv2.putText(bg, text, demi(x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)


def watch_clicks(cap, win, pix_per, lines=None):
     """Watches the video feed & tracks mouse events; records left clicks' positions."""
     points = []
     live = None

     def mouse_event(event, x, y, flag, params):
          """Handle & check mouse events for relevant clicks."""
          nonlocal live
          if event == cv2.EVENT_LBUTTONDOWN:
               points.append((x, y))
          elif event == cv2.EVENT_RBUTTONDOWN:
               if points:
                    points.clear() # erase last selection
               elif lines:
                    lines.pop() # clear the last created line
          elif event == cv2.EVENT_MOUSEMOVE:
               live = (x, y)

     cv2.setMouseCallback(win, mouse_event)

     while len(points) < 2:
          ret, f = cap.read()
          if not ret:
               print("failed to grab frame")
               return (None, None)

          if lines:
               for c, d, vrai in lines:
                    artist(f, c, d, vrai)
          if len(points) == 1 and live and pix_per:
               artist(f, points[0], live, text=f"{(hypo(points[0], live)/pix_per):.3f} mm")
          elif len(points) == 1 and live and not pix_per:
               artist(f, points[0], live)

          cv2.imshow(win, f)

          key = cv2.waitKey(1)
          if key == ord('q') or key == 27:
               print("user quit")
               return (None, None)

     return points


@contextmanager
def wm(win):
     """Context manager for an image's window being created & destroyed upon return."""
     cv2.namedWindow(win, flags=cv2.WINDOW_FULLSCREEN)
     cv2.setWindowProperty(win, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
     yield win
     cv2.destroyAllWindows()


def main():
     pix_per = None
     cap = load_vid()
     if cap is None:
          return

     with wm("Select two points w.a known distance: ") as win:
          a, b = watch_clicks(cap, win, pix_per)
          cap.release() # close & reload so the window doesn't need to be closed/moved
          if not a:
               return

     pix_per = verify(a, b)
     if not pix_per:
          return

     cap = load_vid()
     with wm("Choose two points to find their distance: ") as win:
          lines = []
          while True:
               c, d = watch_clicks(cap, win, pix_per, lines)
               if not c:
                    break

               eucl = hypo(c, d)
               vrai = f"{(eucl / pix_per):.3f} mm"

               print(f"true distance: {vrai}")
               lines.append((c, d, vrai))

          cap.release()


if __name__=="__main__":
     main()