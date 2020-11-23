
from picamera import PiCamera

class CameraController:
    def __init__(self,camera_object,resolution):
        self.camera_object=camera= PiCamera()
        self.resolution=(resolution[0],resolution[1])
    def setResolution(self,resolution):
        self.resolution=(resolution[0],resolution[1])
    def takePicture(self,file_name):
        self.camera_object.capture(file_name)
    

