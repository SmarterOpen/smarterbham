# Original library was from https://github.com/ThingType/HPMA115S0_Python_library but intended for Raspberry Pi
# Modifying to work with Pycom Lopy4

#BME680 project from Micropython.. may need some modifications to run
import nets
import machine 
import bme680
from i2c import I2CAdapter
from network import LoRa
import socket
import ubinascii
import struct
import time
import utime
import os
import math
import lorakeys
import pycom
import ustruct
import si1132
from machine import Pin
pycom.heartbeat(False) #needs to be disabled for LED functions to work
pycom.rgbled(0x7f0000) #red

# write a routine to enable libraries only when that sensor is online - that way I can use the same base code everywhere and just bypass uninstalled sensors
from machine import I2C,Pin
i2c = I2C(0, pins=("P9","P10"))
i2c.init(I2C.MASTER, baudrate=100000)
activesensors=i2c.scan()
if len(activesensors)>0:
  for c in range (0,len(activesensors)):
    if activesensors[c]==96:#0x60 IE Si1132
      HasSi1132=True
    elif activesensors[c]==118:#0x76  IE: BME680
      HasBME680=True
    elif activesensors[c]==45:# not used yet.
      sensors2=True
    
    
  
i2c_dev = I2CAdapter()
if HasBME680 == True:
  sensor = bme680.BME680(i2c_device=i2c_dev)
if HasSi1132 == True:
  si = si1132.SI1132(i2c_dev)

DUSTEN = Pin('P23', mode=Pin.OUT)
PinOn=1
PinOff=0
#DUSTEN.value(PinOn)
DUSTEN.value(PinOff)
print("turning fan off")
#time.sleep(6)
#DUSTEN.value(PinOn)
#print("turning fan on")
#time.sleep(6)
#get online using known nets if available
if machine.reset_cause() != machine.SOFT_RESET:
    from network import WLAN
    wl = WLAN()
    wl.mode(WLAN.STA)
    original_ssid = wl.ssid()
    original_auth = wl.auth()

    print("Scanning for known wifi nets")
    available_nets = wl.scan()
    netsisee = frozenset([e.ssid for e in available_nets])

    known_nets_names = frozenset([key for key in nets.known_nets])
    net_to_use = list(netsisee & known_nets_names)
    try:
        net_to_use = net_to_use[0]
        net_properties = nets.known_nets[net_to_use]
        pwd = net_properties['pwd']
        sec = [e.sec for e in available_nets if e.ssid == net_to_use][0]
        if 'wlan_config' in net_properties:
            wl.ifconfig(config=net_properties['wlan_config'])
        wl.connect(net_to_use, (sec, pwd), timeout=10000)
        while not wl.isconnected():
            machine.idle() # save power while waiting
        print("Connected to "+net_to_use+" with IP address:" + wl.ifconfig()[0])
        pybytes.reconnect()

    except Exception as e:
        print("Failed to connect to any known network, going into AP mode")
        wl.init(mode=WLAN.AP, ssid=original_ssid, auth=original_auth, channel=6, antenna=WLAN.INT_ANT)
#pybytes.send_signal(2,0)
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
uart = UART(1, 9600)                         # init with given baudrate
uart.init(9600, bits=8, parity=None, stop=1) # init with given parameters
read_timeout=2000
MSG_CHAR_1 = b'\x42' # First character to be recieved in a valid packet
MSG_CHAR_2 = b'\x4d' # Second character to be recieved in a valid packet
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
if HasBME680 == True:
  sensor = bme680.BME680(i2c_device=i2c_dev)
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
pybytes.send_signal(2,0)
while 1:
   print("Looping")
   DUSTEN.value(PinOn)
   print("turning fan on")
  #hpma115S0.startParticleMeasurement()#Wake up the HOneywell dust sensor
   time.sleep(6)#Give Honeywell sensor 6 seconds for readings to normalize
   inp=''
   recv=[]
   dump=uart.read()
   start=utime.ticks_ms()
   pm10=ustruct.pack('>H',int(-1))
   pm25=ustruct.pack('>H',int(-1))
   while(utime.ticks_diff(start,utime.ticks_ms())> -read_timeout):
      if(uart.any()>0):
         inp = uart.read(1) # Read a character from the input
      #print('char received=',inp)
      if inp == MSG_CHAR_1: # check it matches
         #print('first match')
         recv += inp # if it does add it to recieve string
         if(uart.any()>0):
            inp = uart.read(1) # read the next character
            if inp == MSG_CHAR_2: # check it's what's expected
            #print('second match')
               recv += inp # att it to the recieve string
               recv += uart.read(30) # read the remaining 30 bytes
               calc = 0
               ord_arr = []
               for c in bytearray(recv[:-2]): #Add all the bytes together except the checksum bytes
                  calc += c
                  ord_arr.append(c)
            # self.logger.debug(str(ord_arr))
               sent = (recv[-2] << 8) | recv[-1] # Combine the 2 bytes together
               if sent == calc: 
                  print('recv=',recv)
                  pm10=ustruct.pack('>H',int((recv[6]*256)+recv[7]))
                  pm25=ustruct.pack('>H',int((recv[8]*256)+recv[9]))
                  print('pm10=',pm10)
                  print('pm2.5=',pm25)
                  break
                  #pm10[0] = recv[3]
                  #pm10[1]= recv[4]
                  #pm25[0] = recv[5]
                  #pm25[1]= recv[6]
               else:
                  print('recv=',recv)
                  print('checksum fail',sent,'!=',calc)
               #  pm10=ustruct.pack('>H',int(-1))
               #  pm25=ustruct.pack('>H',int(-1))
            else:
               print('second char mismatch =',inp)
   #pybytes.send_signal(2,1)
   DUSTEN.value(PinOff)
   print("turning fan off")

   #if (hpma115S0.readParticleMeasurement()):#Get the current dust particulate Reading
   #    print("PM2.5: %d ug/m3" % (hpma115S0._pm2_5))
   #    pybytes.send_signal(0, hpma115S0._pm2_5)
   #    time.sleep(1)
   #    print("PM10: %d ug/m3" % (hpma115S0._pm10))
   #    pybytes.send_signal(1, hpma115S0._pm10)
   #time.sleep(1)
   #hpma115S0.stopParticleMeasurement()#Sleep the fan on the Dust sensor
   
#BME680 project from Micropython.. may need some modifications to run.. Actually, looks like it was written for Pycom Wipy
   tempstruct=ustruct.pack('>H',int(0))
   dewstruct=ustruct.pack('>H',int(0))
   pressstruct=ustruct.pack('>H',int(0))
   relhumidstruct=ustruct.pack('>H',int(0))
   
   if HasBME680 == True:
   
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
            #pybytes.send_signal(2,sensor.data.temperature)
   #            time.sleep(2)
   #            time.sleep(1)
   #         else:
   #            pybytes.send_signal(2,58)

      except Exception as e:
         print('DEBUG :: @Get Reading from the BME680 :: Exception: ' + str(e))
   #      pybytes.send_signal(2,85)
   #      pycom.rgbled(red)
         pass
   broadlum=0
   IR=0
   if HasSi1132 == True:
      try:
         broadlum=round(si.read_visible())
         broadlumstruct=struct.pack(">h",broadlum)
      except Exception as e:
         print('DEBUG :: @Get Reading from the si1132 :: Exception: ' + str(e))
         pass
      try:
         IR=round(si.read_IR())
         IRlumstruct=struct.pack(">h",IR)
      except Exception as e:
         print('DEBUG :: @Get Reading from the si1132 :: Exception: ' + str(e))
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
   s.send(bytes([pm25[0],pm25[1],pm10[0],pm10[1],
                  tempstruct[0],tempstruct[1],
                  relhumidstruct[0],relhumidstruct[1],
                  dewstruct[0],dewstruct[1],
                  pressstruct[0],pressstruct[1],
                  0x0b,0x0c,
                  broadlumstruct[0],broadlumstruct[1],
                  IRlumstruct[0],IRlumstruct[1],
                  #vocStruct[0],vocStruct[1],vocStruct[2],vocStruct[3]]))
                  0x00,0x00,0x00,0x00]))#VOC resistance?  
      
   pybytes.send_signal(0,(pm25[0]*256)+pm25[1])
   time.sleep(1)
   pybytes.send_signal(1,(pm10[0]*256)+pm10[1])
   time.sleep(1)
      
   pybytes.send_signal(4,int(sensor.data.temperature))
   time.sleep(1)
   pybytes.send_signal(5,int(sensor.data.humidity))
   time.sleep(1)
   pybytes.send_signal(6,int(sensor.data.dew_point))
   time.sleep(1)
   pybytes.send_signal(7,int(sensor.data.pressure*0.2952998307)/10)
   time.sleep(1)
   pybytes.send_signal(8,broadlum)
   time.sleep(1)
   pybytes.send_signal(10,IR)
      
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

