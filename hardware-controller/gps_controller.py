import serial
import time

class GpsController:
    def __init__(self,port):
        self.serial_port=port
    def runPowerGps(self):
        self.serial_port.write(('AT+CGNSPWR=1'+'\r\n').encode())
        time.sleep(0.1)
    def runSetBaudRate(self):
        self.serial_port.write(('AT+CGNSIPR=115200'+'\r\n').encode())
        time.sleep(0.1)
    def runSendDataToUart(self):
        self.serial_port.write(('AT+CGNSTST=1'+'\r\n').encode())
        time.sleep(0.1)
    def runPrintGpsInfo(self):
        self.serial_port.write(('AT+CGNSINF'+'\r\n').encode())
        time.sleep(0.1)
    def checkGpsPower(self,response):
        powerStatus=-1                    #status 0:OFF 1:On -1:not identified
        if(response.find('CGNSPWR')>-1):
            if(response.find('0')>-1):
                powerStatus=0
            elif(response.find('1')>-1):
                powerStatus=1
        return powerStatus
    def validateGpsOn(self,str):
        gpsOn=False
        if(str.find('CGNSPWR')>-1):
            if(str.find('1')>-1):
                gpsOn=True
        return gpsOn
    def runTurnOffGps(self):
        self.serial_port.write(('AT+CGNSPWR=0'+'\r\n').encode())
    def runTurnOnGps(self):
        self.serial_port.write(('AT+CGNSPWR=1'+'\r\n').encode())