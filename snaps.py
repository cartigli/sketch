import os
import cv2
import shutil
from contextlib import contextmanager

"""
Streams a device's video feed and writes selected frames to disk (for calibration).
"""

def out_mgr(out):
     """Handles creation/deletion of the directory of calibration images."""
     if os.path.exists(out):
          rm = input(f"{out} alreaedy exists; replace it? [y/n]: ")
          if rm in ("y", "Y", "yes", " y", "y "):
               shutil.rmtree(out)
          else:
               print("understood; abandoning")
               return False
     os.mkdir(out)
     return True


@contextmanager
def creek(src=0):
     """Context manager for the video feed device & its closing."""
     cap = cv2.VideoCapture(src, cv2.CAP_V4L2)
     h, w = cap.read()[1].shape[:2]
     print(f"loaded video feed w.dims: {w}x{h}")
     yield cap
     cap.release()
     cv2.destroyAllWindows()


def main(out, src=0):
     """Plays a video feed while capturing frames when 'x' is pressed (q/e for quit/exit)."""
     cnt = 0
     if not out_mgr(out):
          return

     with creek(src) as cap:
          while True:
               r, f = cap.read()
               if not r:
                    print("failed to grab frame")
                    break
               cv2.imshow("Capturing Calibration:", f)

               key = cv2.waitKey(1) & 0xFF
               if key == ord("x"):
                    nom = os.path.join(out, f"calimg_{cnt}.png")
                    cv2.imwrite(nom, f)
                    print(f"saved {nom} to disk")
                    cnt += 1
               elif key in (ord("q"), ord("e")):
                    print("user quit")
                    break


if __name__=="__main__":
     src = 2
     out = "/home/t/cali.A1"
     main(out, src)
