# Original library was from https://github.com/ThingType/HPMA115S0_Python_library but intended for Raspberry Pi
# Modifying to work with Pycom Lopy4

from hpma115s0 import HPMA115S0
import time
from machine import UART

# initialize class for HPMA115S0 Honeywell Dust Particulate sensor
# sensor returns PM2.5 and PM10 particulate count in Parts Per Billion
# across serial UART at 9600, 8,N,1
hpma115S0 = HPMA115S0()
#uart = UART(1, 9600)                         # init with given baudrate
#uart.init(9600, bits=8, parity=None, stop=1) # init with given parameters
# datasheet https://sensing.honeywell.com/honeywell-sensing-particulate-hpm-series-datasheet-32322550
# Recommended to prolong sensor (Fan) life to shut off sensor fan (send Stop measurements CMD) between readings
# when ready to read, send start measurement command, wait at least 6 seconds, then Read measurement command.
# When sensor intially starts, it auto-writes a 32 byte string with these values embedded once per second.. 
# you have to send stop auto send command to disable this.

hpma115S0.init()
print("Starting")
#data= uart.readall()
time.sleep(1)# then give it another second for the next good byte to come in.

while 1:
   print("Looping")
   hpma115S0.startParticleMeasurement()#Wake up the HOneywell dust sensor
   time.sleep(6)#Give Honeywell sensor 6 seconds for readings to normalize
   if (hpma115S0.readParticleMeasurement()):#Get the current dust particulate Reading
       print("PM2.5: %d ug/m3" % (hpma115S0._pm2_5))
       pybytes.send_signal(0, hpma115S0._pm2_5)
       time.sleep(1)
       print("PM10: %d ug/m3" % (hpma115S0._pm10))
       pybytes.send_signal(1, hpma115S0._pm10)
   time.sleep(1)
   hpma115S0.stopParticleMeasurement()#Sleep the fan on the Dust sensor
   time.sleep(300)#wait 5 minutes before next reading
