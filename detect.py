# Run this on the Nano
import cv2
import threading
from cv2 import ROTATE_90_CLOCKWISE
from cv2 import ROTATE_90_COUNTERCLOCKWISE
from cv2 import ROTATE_180
from deepstack_sdk import ServerConfig, Face
import time
import getopt
import sys
import requests

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
        opts, args = getopt.getopt(argv,"t:c:h:r:i:",["timer=", "confidence=", "hook=", "rotation=", "input="])
    except getopt.GetoptError:
      print('-r <0, 90, 180, 270> Rotation')
      print('-i <rtsp stream uri>')
      print('-t <time in ms between relay triggers>')
      print('-c <min confidence for trigger>')
      print('-h <webhook uri for detection>')
      sys.exit(2)

    rotation = 0
    hook = "" 
    c = "0.8"
    t = "5000"

    for opt, arg in opts:
        if opt in ("-i", "--input"):
            input = arg
        if opt in ("-r", "--rotation"):
            rotation = arg
        if opt in ("-h", "--hook"):
            hook = arg
        if opt in ("-c", "--confidence"):
            c = arg
        if opt in ("-t", "--timer"):
            t = arg

    confidence = float(c)
    capture = VideoCapture(input)
    config = ServerConfig("http://localhost:8080")
    face = Face(config)

    last_detect = 0
    last_recog = 0
    last_open = 0

    delay_detect = 500   # 200 ms = 5fps
    delay_recog = 1000
    delay_relay = int(t)

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
                        if rotation == "90":
                            cv2.rotate(cropped, cv2.cv2.ROTATE_90_CLOCKWISE)
                        if rotation == "270":
                            cv2.rotate(cropped, cv2.cv2.ROTATE_90_COUNTERCLOCKWISE)
                        if rotation == "180":
                            cv2.rotate(cropped, cv2.cv2.ROTATE_180)
                        response = face.recognizeFace(cropped, output=None )

                        if len(response.detections) > 0:
                            detection = response.detections[0]
                            if(detection.userid != "unknown"):
                                print("Spotted: " + detection.userid + " with confidence " + str(detection.confidence))
                                if(detection.confidence >= confidence) and (now > last_open + delay_relay):
                                    last_open = now
                                    print("opening door")
                                    requests.get(hook)
                    last_recog = now

if __name__ == "__main__":
   main(sys.argv[1:])