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
        #self._serial = serial.Serial()
        #self._serial.port = ser
        #self._serial.baudrate = 9600
        #self._serial.stopbits = serial.STOPBITS_ONE
        #self._serial.bytesize = serial.EIGHTBITS
        #self._serial.timeout = 1
        #self._serial.open()
        _uart = UART(1, 9600)                         # init with given baudrate
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

    def startParticleMeasurement(self):
        """
        Function which starts sensor measurement
        """
        cmd = [0x68, 0x01, 0x01, 0x96]
        self.sendCmd(cmd)

    def stopParticleMeasurement(self):
        """
        Function which stops sensor measurement
        """
        cmd = [0x68, 0x01, 0x02, 0x95]
        self.sendCmd(cmd)

    def disableAutoSend(self):
        """
        Function which stops auto send by the sensor
        """
        cmd = [0x68, 0x01, 0x20, 0x77]
        self.sendCmd(cmd)

    def readParticleMeasurement(self):
        """
        Function which sends a read command to sensor to get retrieve datas
        """
        cmdBuf = [0x68, 0x01, 0x04, 0x93]

        self.sendCmd(cmdBuf)

        if (self.readCmdResp(READ_PARTICLE_MEASUREMENT) == (HPM_READ_PARTICLE_MEASUREMENT_LEN - 1)):
            self._pm2_5 = self._dataBuf[0] * 256 + self._dataBuf[1]
            self._pm10 = self._dataBuf[2] * 256 + self._dataBuf[3]

            return True
        #pm2_5=self._dataBuf[0] * 256 + self.dataBuf[1]
        #print(pm2_5)

        return False

    def readStringUntil(self, terminator):
        """
        Function to start reading when the sensor is ready to transmit datas

        """
        c = self._uart.read()
        print("Serial:")
        print(c)
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
