import tkinter as tk
from PIL import Image, ImageTk
from gps_final import *
import io
from flask import Flask,Response,jsonify
port = serial.Serial("/dev/ttyUSB0", baudrate=115200, timeout=1)
ready_to_read_data=False
update =0
stream=io.BytesIO()
import io
import picamera
import logging
import socketserver
from threading import Condition
from http import server
from flask_cors import CORS
file_counter=0
def readSingleLine():
    rcv=port.readline().decode()
    return rcv
def runAtTest():
    port.write(('AT'+'\r\n').encode())            
def takePicture(cam,gps_info):
    cam.capture("img_"+str(gps_info[0])+str(gps_info[1])+str(gps_info[2])+str(gps_info[3])+".jpg")
def updateImage(label):
    stream.seek(0)
    #print(stream)
    img=Image.open(stream)
    img_obj=ImageTk.PhotoImage(img)
    label.config(image=img_obj)
    label.image=img_obj

def callBack():
    captureToStream(camera)
    updateImage(img_label)
    
def captureToStream(camera_obj):
    stream.seek(0)
    camera_obj.capture(stream,format='jpeg')

def start():
    operation_success=False
    runAtTest()
    rcv=readSingleLine()
    proceed=False
    while rcv:
        if(checkATStatus(rcv)):
            print(rcv+"Status:Ok \n")  #insert output to label
            proceed=True
            break
        else:
            rcv=readSingleLine()
    if(proceed):
        runGpsPowerCheck()
        rcv=readSingleLine()
        while(rcv):
            if(checkGpsPower(rcv)==1):
                print("power on")
                runSendDataToUart()        
                control=True
                thresh=30
                while thresh>20:
                    rcv= port.readline().decode()
                    res,msg=parseGps(rcv)
                    if res:
                        ready_to_read_data=True
                        thresh-=1
                        print("received valid data")
                    port.flushInput()
                operation_success=True
                break
            elif(checkGpsPower(rcv)==0):
                print("power off.....turnning On")
                runTurnOnGps()
                rcv=readSingleLine()
                while(rcv):
                    if (validateGpsOn(rcv)):
                        rcv=readSingleLine()
                        if(checkATStatus(rcv)):
                            print("power on success")   ###########
                            runSendDataToUart()
                            
                            control=True
                            thresh=30
                            while thresh>20:
                                rcv= port.readline().decode()
                                res,msg=parseGps(rcv)
                                if res:
                                    ready_to_read_data=True
                                    print("received valid data")
                                    #update=1
                                    #print(update)
                                    #break
                                    thresh-=1
                                port.flushInput()
                            operation_success=True
                            break
                        else:
                            print("power on failure")
                    else:
                        rcv=readSingleLine()
                
                break
            else:
                rcv=readSingleLine()
    print("return")
    return operation_success
        

        

def prepare():
    runAtTest()
    rcv=readSingleLine()
    proceed=False
    while rcv:
        if(checkATStatus(rcv)):
            print(rcv+"Status:Ok \n")  #insert output to label
            proceed=True
            break
        else:
            rcv=readSingleLine()
    if(proceed):
        runGpsPowerCheck()
        rcv=readSingleLine()
        while(rcv):
            if(checkGpsPower(rcv)==1):
                print("power on")
                #runSendDataToUart() ##############
                runTurnOffGps()
                break
            elif(checkGpsPower(rcv)==0):
                print("power off.....turnning On")
                runTurnOnGps()
                rcv=readSingleLine()
                while(rcv):
                    if (validateGpsOn(rcv)):
                        rcv=readSingleLine()
                        if(checkATStatus(rcv)):
                            print("power on success")   ###########
                            runSendDataToUart()
                            
                            control=True
                            thresh=30
                            while control:
                                rcv= port.readline().decode()
                                res,msg=parseGps(rcv)
                                if res:
                                    ready_to_read_data=True
                                    update=1
                                    print(update)
                                    break
                                port.flushInput()
                        
                            break
                        else:
                            print("power on failure")
                    else:
                        rcv=readSingleLine()
                
                break
            else:
                rcv=readSingleLine()
    
        
def parseGps(str):
    #print(str)
    msg=" "
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
            print(e)
    return [valid,msg]
def checkATStatus(response):
    validResponse=False
    if(response.find('OK')>-1):
        validResponse=True
    return validResponse

def checkGpsPower(response):
    powerStatus=-1                    #status 0:OFF 1:On -1:not identified
    if(response.find('CGNSPWR')>-1):
        if(response.find('0')>-1):
            powerStatus=0
        elif(response.find('1')>-1):
            powerStatus=1
    return powerStatus

def validateGpsOn(str):
    gpsOn=False
    if(str.find('CGNSPWR')>-1):
        if(str.find('1')>-1):
            gpsOn=True
    return gpsOn
def runGpsPowerCheck():
    port.write(('AT+CGNSPWR?'+'\r\n').encode())             # check GPS power status (0 OFF , 1 ON)
    #rcv = port.readline().decode()
def runSendDataToUart():
    port.write(('AT+CGNSTST=1'+'\r\n').encode())
    
def runTurnOffGps():
     port.write(('AT+CGNSPWR=0'+'\r\n').encode())
def runTurnOnGps():
     port.write(('AT+CGNSPWR=1'+'\r\n').encode())   
def readSingleLine():
    rcv=port.readline().decode()
    return rcv
def runAtTest():
    port.write(('AT'+'\r\n').encode())            
def updateLabel():
    print("update")
    rcv= port.readline().decode()
    res,msg=parseGps(rcv)
    if(res):
        lon_label["text"]=str(msg.lon) 
        lat_label["text"]=str(msg.lat)
        takePicture(camera,[msg.lon,msg.lon_dir,msg.lat,msg.lat_dir])
    callBack()    
    window.after(160,updateLabel)
    

app=Flask(__name__)
camera = picamera.PiCamera()
camera.resolution = (1920 ,1080)
CORS(app)
@app.route("/")        
def index():
    status=start()
    response={"status":status}
    return jsonify(response),200
@app.route("/location")
def location():
    response={}
    #response["Access-Control-Allow-Origin"]="*"
    rcv= port.readline().decode()
    while rcv:
        try:
            res,msg=parseGps(rcv)
            if(res):
                response["lon"]=msg.lon
                response["lat_dir"]=msg.lat_dir
                response["lat"]=msg.lat
                response["lon_dir"]=msg.lon_dir
                print(response)
                camera.capture("/home/pi/Desktop/Project_Files/images/"+msg.lon+" _ "+msg.lon_dir +"_"+ msg.lat+"_"+msg.lat_dir+" .jpg")
                break
            else:
                rcv=port.readline().decode()
        except (Exception):
            print("invalid data")
        
        #camera.capture(response["lon"] + response["lat"]+".jpg")
        #file_counter+=1
        
        #lon_label["text"]=str(msg.lon) 
        #lat_label["text"]=str(msg.lat)
        #takePicture(camera,[msg.lon,msg.lon_dir,msg.lat,msg.lat_dir])
    return jsonify(response),200
@app.route("/stop")
def st():
    response={"status":"true"}
    print("called")
    #camera = picamera.PiCamera()
    #camera.resolution = (320 ,200)
    #camera.capture("test_image.jpg")
    #camera.start_preview()
    time.sleep(10)
    #camera.stop_preview()
    return jsonify(response),200
    
    
if __name__ =='__main__':
    app.run('192.168.43.90',5000)
