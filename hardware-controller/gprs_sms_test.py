import serial
import time

class GprsSmsTest:
    def __init__(self):
        self.serial_port =serial.Serial("/dev/ttyUSB0", baudrate=115200, timeout=1)
    def runAtTest(self): #run at test to check if hardware responds
        self.serial_port.write(('AT'+'\r\n').encode())
        time.sleep(0.1)
    def runTurnOffCommandEcho(self): # turn command echo off
        self.serial_port.write(('ATE0'+'\r\n').encode())
        time.sleep(0.1)
    def runSmsTextMode(self):
        self.serial_port.write(('AT+CMGF=1'+'\r\n').encode())
        time.sleep(0.1)
    def runNotificationSettings(self):
        self.serial_port.write(('AT+CNMI=2,1,0,0,0'+'\r\n').encode())
        time.sleep(0.1)
    def runSetPhoneNumber(self):
        self.serial_port.write(('AT+CMGS="+############"'+'\r\n').encode())
        time.sleep(0.1)
    def runSetMessageContent(self):
        self.serial_port.write(('PI test message'+'\r\n').encode())
        time.sleep(0.1)