# I used this as the main.py to test the HPMA sensor. No library files were used
# the code mostly works to output sensor data to the USB UART.  On occasion, the sensor gets stuck
#in an unknown state and stops responding.  If I power-cycle the sensor but leave the Pycom running, it works fine
#emailed Honeywell support for info to work around.. otherwise, may need to tie the power pin to a GPIO so it can be cycled manually
# Daniel Near 10/20/2019 9:32pm
from machine import UART
import time
uart = UART(1, 9600)
uart.init(9600, bits=8, parity=None, stop=1)
startcmd = [0x68, 0x01, 0x01, 0x96]
stopcmd = [0x68, 0x01, 0x02, 0x95]
disableautocmd = [0x68, 0x01, 0x20, 0x77]
readcmd = [0x68, 0x01, 0x04, 0x93]

trash=uart.read()
print('disableAuto')
uart.write(bytearray(disableautocmd))
time.sleep(0.5)
data=uart.read()
print(data)


while (1):
     print('waking up HPMA')
     uart.write(bytearray(startcmd))
     trash=uart.read()
     print(trash)
     print('disable Autosend')
     uart.write(bytearray(disableautocmd))
     time.sleep(0.5)
     data=uart.read()
     print(data)
     print('wait 6s before read')
     time.sleep(6)#wait six seconds
     print('starting read')
     trash=uart.read()
     uart.write(bytearray(readcmd))
     time.sleep(0.5)
     data=uart.read()
     print(data)
     time.sleep(0.5)
     trash=uart.read()
     print('Stopping measurements')
     uart.write(bytearray(stopcmd))
     print('Sleeping 30s')
     time.sleep(30)
