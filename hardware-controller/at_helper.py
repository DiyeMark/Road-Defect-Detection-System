class ATHelper:
    def __init__(self,port):
        self.serial_port= port
    def runAtTest(self):
        self.serial_port.write(('AT'+'\r\n').encode())
    def readSingleLine(self):
        response=self.serial_port.readline().decode()
        return response
    def checkAtStatus(self,response):
        validResponse=False
        if(response.find('OK')>-1):
            validResponse=True
        return validResponse


