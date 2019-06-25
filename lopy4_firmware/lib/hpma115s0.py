import time
from machine import UART

READ_PARTICLE_MEASUREMENT = 4
HPM_READ_PARTICLE_MEASUREMENT_LEN = 5
HPM_MAX_RESP_SIZE = 8
HPM_CMD_RESP_HEAD = 0x40


class HPMA115S0:
    #_serial = None
    _uart =UART(1,9600)
    _pm2_5 = None
    _pm10 = None
    _dataBuf = [None] * (HPM_READ_PARTICLE_MEASUREMENT_LEN - 1)

    def __init__(self):
        """
        Constructor for the HPMA115S0 class
        """
        #self._serial = serial.Serial()#these six lines were how Python sets up the UART on Raspberry Pi
        #self._serial.port = ser
        #self._serial.baudrate = 9600
        #self._serial.stopbits = serial.STOPBITS_ONE
        #self._serial.bytesize = serial.EIGHTBITS
        #self._serial.timeout = 1
        #self._serial.open()
        _uart = UART(1, 9600)                         # init Lopy4 UART with given baudrate
        _uart.init(9600, bits=8, parity=None, stop=1) # init with given parameters

    def init(self):
        """
        Function which initializes the sensor.
        """
        print("Initializing")
        time.sleep(0.1)
        self.startParticleMeasurement()
        time.sleep(0.1)
        self.disableAutoSend()
        trash = self._uart.read()
    def sendCmd(self, cmdBuf):
        """
        Function which sends a serial command to the sensor (cf datasheet)

        Params:
                cmdBuf: the array containing the datas to be sent
        """
        trash = self._uart.read()            # clear buffer spicer

        self._uart.write(bytearray(cmdBuf))

    def readCmdResp(self, cmdType):
        """
        Function which reads command response from the sensor

        Params: 
                cmdType : Expected command type
        """
        respBuf = [None] * HPM_MAX_RESP_SIZE
        respIdx = 0
        calChecksum = 0
        for i in range(0, len(respBuf)):
            respBuf[i] = 0

        if (self.readStringUntil(HPM_CMD_RESP_HEAD)):
            respBuf[0] = HPM_CMD_RESP_HEAD
            respBuf[1] = ord(self._uart.read(1))# read 1 byte  spicer

            if (respBuf[1] and ((respBuf[1] + 1) <= len(respBuf) - 2) and (respBuf[1] - 1) <= len(self._dataBuf)):
                resp = self.readBytes(respBuf, respBuf[1] + 1, 2)
                respBuf = resp[0]
                respCount = resp[1]
                if (respCount == respBuf[1] + 1):
                    if (respBuf[2] == cmdType):
                        while (respIdx < (2 + respBuf[1])):
                            calChecksum += respBuf[respIdx]
                            respIdx += 1
                        calChecksum = (65536 - calChecksum) % 256
                        if (calChecksum == respBuf[2 + respBuf[1]]):
                            print("received valid data")
                            for i in range(0, len(self._dataBuf)):
                                self._dataBuf[i] = 0
                            j = 0
                            for i in range(0, 4):
                                self._dataBuf[j] = respBuf[i + 3]
                                j += 1
                            return (respBuf[1] - 1)
        return False

    def startParticleMeasurement(self):#Wakes up the sensor and enables the fan.  Wait at least 6 seconds before first reading
        """
        Function which starts sensor measurement
        """
        cmd = [0x68, 0x01, 0x01, 0x96]
        self.sendCmd(cmd)

    def stopParticleMeasurement(self):#Sleep the sensor and disable the fan.  Do this when not reading to extend fan life
        """
        Function which stops sensor measurement
        """
        cmd = [0x68, 0x01, 0x02, 0x95]
        self.sendCmd(cmd)

    def disableAutoSend(self):#sensor auto-transmits 32 byte packet every second unless you do this.  
        """
        Function which stops auto send by the sensor
        """
        cmd = [0x68, 0x01, 0x20, 0x77]
        self.sendCmd(cmd)

    def readParticleMeasurement(self):#after starting measurement and waiting 6 seconsd, call this to get a reading
        """
        Function which sends a read command to sensor to get retrieve datas
        """
        cmdBuf = [0x68, 0x01, 0x04, 0x93]

        self.sendCmd(cmdBuf)

        if (self.readCmdResp(READ_PARTICLE_MEASUREMENT) == (HPM_READ_PARTICLE_MEASUREMENT_LEN - 1)):
            self._pm2_5 = self._dataBuf[0] * 256 + self._dataBuf[1]
            self._pm10 = self._dataBuf[2] * 256 + self._dataBuf[3]

            return True
        

        return False

    def readStringUntil(self, terminator):
        """
        Function to start reading when the sensor is ready to transmit datas

        """
        c = self._uart.read()
        print("Serial:")#added local serial output for debug purpose
        print(c)# for some reason it's not getting any output - this returns "None" to serial port
        if c is not None:
             for a in range(len(c)):
                  cn = ord(a)
                  if cn == terminator:
                       return True

    def readBytes(self, buffer, length, index):
        count = 0
        while (count < length):
            c = self._uart.read()
            for ch in c:
                ch = ord(c)
                if (ch < 0):
                    break
                buffer[index] = ch
                count += 1
                index += 1
        return [buffer, count]

    
    
    #currently, I can send these commands in the pybytes.pycom.io terminal view and get valid data/responses
    #but the code doesn't seem to work correctly as shown above.
    #uart = UART(1, 9600)
    #uart.init(9600, bits=8, parity=None, stop=1)
    #startcmd = [0x68, 0x01, 0x01, 0x96]
    #stopcmd = [0x68, 0x01, 0x02, 0x95]
    #disableautocmd = [0x68, 0x01, 0x20, 0x77]
    #readcmd = [0x68, 0x01, 0x04, 0x93]
    #uart.write(bytearray(disableautocmd))
    #uart.write(bytearray(startcmd))
    #trash=uart.read()
    #wait six seconds
    #uart.write(bytearray(readcmd))
    #data=uart.read()
    #print(data)
    #it will output something like this:b'@\x05\x04\x00\x30\x00\x31V'
    #pycom displays bit streams preceded with b' and ending with '
    #these bit streams will convert AlphaNumeric characters to their ASCII equivalent but other characters will display as \x00
    #which is the hex value of the last 2 digits.
    #the above sample output would translate to pm2.5 = 0030 or 48 ppb and pm10 = 0031 or 49ppb
    #see honeywell datasheet
    #the checksum arguments in the code are very important as they will ensure only valid data is output
    #if the checksum doesn't match, there's some issue in communications.
