# Run this on the Nano
import cv2
import threading
from deepstack_sdk import ServerConfig, Face
import time
import getopt
import sys

class VideoCapture:
    def __init__(self, name):
        self.cap = cv2.VideoCapture(name)
        self.t = threading.Thread(target=self._reader)
        self.t.daemon = True
        self.t.start()

    def _reader(self):
        while True:
            ret = self.cap.grab()
            if not ret:
                break

    def read(self):
        ret, frame = self.cap.retrieve()
        return ret, frame

    def release(self):
        self.cap.release()

def current_milli_time():
    return round(time.time() * 1000)

def main(argv):

    try:
        opts, args = getopt.getopt(argv,"i:",["input="])
    except getopt.GetoptError:
      print('-i <rtsp stream uri>')
      sys.exit(2)

    for opt, arg in opts:
        if opt in ("-i", "--input"):
            input = arg

    capture = VideoCapture(input)
    config = ServerConfig("http://localhost:8080")
    face = Face(config)

    last_detect = 0
    last_recog = 0

    delay_detect = 500   # 200 ms = 5fps
    delay_recog = 1000

    print("Starting")
    while True:
        now = current_milli_time()

        if now > last_detect + delay_detect:
            ret, frame = capture.read()
            if ret:
                response = face.detectFace(frame, output=None )
                last_detect = now
                if now > last_recog + delay_recog:
                    count = len(response)
                    print("Recog on " + str(count) + " objects")
                    for obj in response:
                        cropped = frame[obj.y_min:obj.y_max, obj.x_min:obj.x_max]
                        response = face.recognizeFace(cropped, output=None )

                        if len(response.detections) > 0:
                            detection = response.detections[0]
                            if(detection.userid != "unknown"):
                                print("Spotted: " + detection.userid + " with confidence " + str(detection.confidence))
                                # OPEN THE DOOR HERE
                    last_recog = now

if __name__ == "__main__":
   main(sys.argv[1:])