from hpma115s0 import HPMA115S0
import time
from machine import UART
hpma115S0 = HPMA115S0()
#uart = UART(1, 9600)                         # init with given baudrate
#uart.init(9600, bits=8, parity=None, stop=1) # init with given parameters


hpma115S0.init()
print("Starting")
#data= uart.readall()
time.sleep(1)# then give it another second for the next good byte to come in.

while 1:
   print("Looping")
   hpma115S0.startParticleMeasurement()
   time.sleep(6)
   if (hpma115S0.readParticleMeasurement()):
       print("PM2.5: %d ug/m3" % (hpma115S0._pm2_5))
       pybytes.send_signal(0, hpma115S0._pm2_5)
       time.sleep(1)
       print("PM10: %d ug/m3" % (hpma115S0._pm10))
       pybytes.send_signal(1, hpma115S0._pm10)
   time.sleep(1)
   hpma115S0.stopParticleMeasurement()
   time.sleep(300)
