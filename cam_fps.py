import cv2
from picamera2 import Picamera2
import time
picam2 = Picamera2()
picam2.preview_configuration.main.size = (320,180)
picam2.preview_configuration.main.format = "RGB888"
picam2.preview_configuration.controls.FrameRate = 60
picam2.preview_configuration.align()
picam2.configure("preview")
picam2.start()

while True:
    tstart = time.time()
    im = picam2.capture_array()
    cv2.imshow("Camera", im)
    if cv2.waitKey(1) == ord('q'):
        break
    tend = time.time()
    looptime = tend-tstart
    fps=1/looptime
    print(fps)
cv2.destroyAllWindows()