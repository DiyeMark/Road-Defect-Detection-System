import time
import pynmea2
class GpsParser:
    def parseGps(self,str):
        valid=False
        if (str.find('GGA')>0):
        try:
            msg=pynmea2.parse(str)
            lon1=msg.lon
            lat1=msg.lat
            
            print("lon "+lon1 +"lon_dir "+msg.lon_dir+"  lat: "+lat1+" lat_dir "+msg.lat_dir)
            if lon1:
                if lat1:
                    valid=True
        except Exception as e:
            print(print("couldnt parse gps"))
    return valid
