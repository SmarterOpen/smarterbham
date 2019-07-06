# Original library was from https://github.com/ThingType/HPMA115S0_Python_library but intended for Raspberry Pi
# Modifying to work with Pycom Lopy4

#BME680 project from Micropython.. may need some modifications to run
import bme680
from i2c import I2CAdapter
from network import LoRa
import socket
import ubinascii
import struct
import time
import os
import math
import lorakeys
import pycom
import ustruct
pycom.heartbeat(False) #needs to be disabled for LED functions to work
pycom.rgbled(0x7f0000) #red
#from machine import I2C,Pin
#i2c = I2C(0, pins=("P9","P10"))
#i2c.init(I2C.MASTER, baudrate=100000)
i2c_dev = I2CAdapter()
sensor = bme680.BME680(i2c_device=i2c_dev)


#VEML6070 code for Python on Raspberry Pi 2/3
#import veml6070

# Initialise LoRa in LORAWAN mode.
# Please pick the region that matches where you are using the device:
# Asia = LoRa.AS923
# Australia = LoRa.AU915
# Europe = LoRa.EU868
# United States = LoRa.US915
#lora = LoRa(mode=LoRa.LORAWAN, region=LoRa.US915)
lora = LoRa(mode=LoRa.LORAWAN, public=1,  adr=0, tx_retries=0)
for i in range(0, 71):
    lora.remove_channel(i)
print('Removed default channels')
time.sleep(1)
    
    # Set US ISM 915 channel plan for TTN US
lora.add_channel(0, frequency=903900000, dr_min=0, dr_max=3)
lora.add_channel(1, frequency=904100000, dr_min=0, dr_max=3)
lora.add_channel(2, frequency=904300000, dr_min=0, dr_max=3)
lora.add_channel(3, frequency=904500000, dr_min=0, dr_max=3)
lora.add_channel(4, frequency=904700000, dr_min=0, dr_max=3)
lora.add_channel(5, frequency=904900000, dr_min=0, dr_max=3)
lora.add_channel(6, frequency=905100000, dr_min=0, dr_max=3)
lora.add_channel(7, frequency=905300000, dr_min=0, dr_max=3)
#channel	8:	903900000	hz	min_dr	0	max_dr	3				
#channel	9:	904100000	hz	min_dr	0	max_dr	3				
#channel	10:	904300000	hz	min_dr	0	max_dr	3				
#channel	11:	904500000	hz	min_dr	0	max_dr	3				
#channel	12:	904700000	hz	min_dr	0	max_dr	3				
#channel	13:	904900000	hz	min_dr	0	max_dr	3				
#channel	14:	905100000	hz	min_dr	0	max_dr	3				
#channel	15:	905300000	hz	min_dr	0	max_dr	3				

print('US channels set')
time.sleep(1)
print('Joining LoRa via OTAA')
# join a network using ABP (Activation By Personalization)
#lora.join(activation=LoRa.ABP, auth=(dev_addr, nwk_swkey, app_swkey))
# join a network using OTAA (Over the Air Activation)
lora.join(activation=LoRa.OTAA, auth=(lorakeys._dev_eui,lorakeys._app_eui, lorakeys._app_key), timeout=0, dr=0)
# wait until the module has joined the network
while not lora.has_joined():
    time.sleep(2.4)
    pycom.rgbled(0x7f7f00) #ylw    
    time.sleep(0.1)
    pycom.rgbled(0x000000) #blk    
    print('Not yet joined...')
    pass
# create a LoRa socket
s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)

# set the LoRaWAN data rate
s.setsockopt(socket.SOL_LORA, socket.SO_DR, 3)
#from hpma115s0 import HPMA115S0
import time
from machine import UART

#BME680 project from Micropython.. may need some modifications to run.. Actually, looks like it was written for Pycom Wipy
#i2c_dev = I2CAdapter()
#sensor = bme680.BME680(i2c_device=i2c)

# initialize class for HPMA115S0 Honeywell Dust Particulate sensor
# sensor returns PM2.5 and PM10 particulate count in Parts Per Billion
# across serial UART at 9600, 8,N,1
#hpma115S0 = HPMA115S0()
#uart = UART(1, 9600)                         # init with given baudrate
#uart.init(9600, bits=8, parity=None, stop=1) # init with given parameters
# datasheet https://sensing.honeywell.com/honeywell-sensing-particulate-hpm-series-datasheet-32322550
# Recommended to prolong sensor (Fan) life to shut off sensor fan (send Stop measurements CMD) between readings
# when ready to read, send start measurement command, wait at least 6 seconds, then Read measurement command.
# When sensor intially starts, it auto-writes a 32 byte string with these values embedded once per second.. 
# you have to send stop auto send command to disable this.

#hpma115S0.init()

#BME680 project from Micropython.. may need some modifications to run.. Actually, looks like it was written for Pycom Wipy
#Init the BME680
# These oversampling settings can be tweaked to
# change the balance between accuracy and noise in
# the data.
try:
   sensor.set_humidity_oversample(bme680.OS_2X)
   sensor.set_pressure_oversample(bme680.OS_4X)
   sensor.set_temperature_oversample(bme680.OS_8X)
   sensor.set_filter(bme680.FILTER_SIZE_3)
except Exception as e:
   print('DEBUG :: @init the BME680 :: Exception: ' + str(e))
   pycom.rgbled(red)
   machine.idle()



print("Starting")
#data= uart.readall()
time.sleep(1)# then give it another second for the next good byte to come in.

while 1:
   print("Looping")
   #hpma115S0.startParticleMeasurement()#Wake up the HOneywell dust sensor
   time.sleep(6)#Give Honeywell sensor 6 seconds for readings to normalize
   #if (hpma115S0.readParticleMeasurement()):#Get the current dust particulate Reading
   #    print("PM2.5: %d ug/m3" % (hpma115S0._pm2_5))
   #    pybytes.send_signal(0, hpma115S0._pm2_5)
   #    time.sleep(1)
   #    print("PM10: %d ug/m3" % (hpma115S0._pm10))
   #    pybytes.send_signal(1, hpma115S0._pm10)
   #time.sleep(1)
   #hpma115S0.stopParticleMeasurement()#Sleep the fan on the Dust sensor
   
#BME680 project from Micropython.. may need some modifications to run.. Actually, looks like it was written for Pycom Wipy
   try:
      #while True:
      if sensor.get_sensor_data():

         output = "{} C, {} hPa, {} RH, {} RES,".format(
            sensor.data.temperature,
            sensor.data.pressure,
            sensor.data.humidity,
            sensor.data.gas_resistance)

         print(output)
         tempstruct=ustruct.pack('>H',int(sensor.data.temperature))
         dewstruct=ustruct.pack('>H',int(sensor.data.dew_point))
         pressstruct=ustruct.pack('>H',int(sensor.data.pressure))
         print('pressure:',pressstruct[0]*256+pressstruct[1])
         relhumidstruct=ustruct.pack('>H',int(sensor.data.humidity))
         #vocStruct=ustruct.pack('>L',int(sensor.data.gas_resistance))
         pybytes.send_signal(2,sensor.data.temperature)
#            time.sleep(2)
#            time.sleep(1)
#         else:
#            pybytes.send_signal(2,58)

   except Exception as e:
      print('DEBUG :: @Get Reading from the BME680 :: Exception: ' + str(e))
#      pybytes.send_signal(2,85)
#      pycom.rgbled(red)
      pass
#Code for VEML6070 on Raspberry Pi 2/3  may need modification
#if __name__ == '__main__':
#    veml = veml6070.Veml6070()
#    for i in [veml6070.INTEGRATIONTIME_1_2T,
#              veml6070.INTEGRATIONTIME_1T,
#              veml6070.INTEGRATIONTIME_2T,
#              veml6070.INTEGRATIONTIME_4T]:
#        veml.set_integration_time(i)
#        uv_raw = veml.get_uva_light_intensity_raw()
#        uv = veml.get_uva_light_intensity()
#print "Integration Time setting %d: %f W/(m*m) from raw value %d" % (i, uv, uv_raw)
   s.setblocking(True)
   print("Sending data!")
#        s.send(bytes([bytestream[4], bytestream[5], bytestream[6],bytestream[7],tempstruct[0],tempstruct[1],rhstruct[0],rhstruct[1],dewstruct[0],dewstruct[1],presstruct[0],presstruct[1],broadlumstruct[0],broadlumstruct[1],IRlumstruct[0],IRlumstruct[1]]))#,relativehumid,dewpoint]))
  #Dust_pm2.5H,Dust_pm2.5L,Dust_pm10H,Dust_pm10L,SignedCelciusH,SignedCelciusL,SignedDewpointH,SignedDewpointL,RHH,RHL,Press*10H,Press*10L,UVH,UVL,AMBH,AMBL,IRH,IRL
#   s.send(bytes([0x00,0x22,0x00,0x12,0x00,0x13,0x00,0x25,0x01,0x2a,0x0b,0x0c,0x0d,0x0e,0x0f,0x10]))
   s.send(bytes([0x00,0x22,0x00,0x12,
                 tempstruct[0],tempstruct[1],
                 relhumidstruct[0],relhumidstruct[1],
                 dewstruct[0],dewstruct[1],
                 pressstruct[0],pressstruct[1],
                 0x0b,0x0c,
                 0x0d,0x0e,
                 0x0f,0x10,
                 #vocStruct[0],vocStruct[1],vocStruct[2],vocStruct[3]]))
                 0x00,0x00,0x00,0x00]))#VOC resistance?  

   print('saving LoRa NVRAM')
   lora.nvram_save()
    # make the socket non-blocking
    # (because if there's no data received it will block forever...)
   s.setblocking(False)
   print("receiving data!")
    # get any data received (if any...)
   data = s.recv(64)
   print(data)
   time.sleep(300)#wait 5 minutes before next reading
