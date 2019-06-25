#library file for Lopy4 to transmit on US915 channels to our TTN gateways
#this was originally running as main.py but needs to be recompiled as a library to improve code readability..
#code came from multiple sources on the pycom forums

import time
import math 
# Create library object using our Bus I2C port
#i2c = busio.I2C(board.SCL, board.SDA)
#from machine import I2C, Pin
#i2c = I2C(0, pins=("P9","P10"))
#i2c.init(I2C.MASTER, baudrate=100000)

     
 # main.py -- put your code here!
from network import LoRa
import socket
import ubinascii
import struct
import time
import os
import math
import abpkeys
import pycom
import ustruct

# Initialise LoRa in LORAWAN mode.
# Please pick the region that matches where you are using the device:
# Asia = LoRa.AS923
# Australia = LoRa.AU915
# Europe = LoRa.EU868
# United States = LoRa.US915
lora = LoRa(mode=LoRa.LORAWAN, region=LoRa.US915)

# create an ABP authentication params
#my keys are stored in abpkeys.py then linked here so I have the same source running 
#on multiple devices
dev_addr=abpkeys.dev_addr
nwk_swkey=abpkeys.nwk_swkey
app_swkey=abpkeys.app_swkey

    # If you don't delete unused channels, you will get something like 95% upload failure.
    # after removing all the unused channels and just adding the 8 used by the gateway, this will revert to
    # 99.9% success provided  you have good RSSI

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


print('restoring LoRa NVRAM')
lora.nvram_restore()
print('Joining LoRa via ABP')
# join a network using ABP (Activation By Personalization)
lora.join(activation=LoRa.ABP, auth=(dev_addr, nwk_swkey, app_swkey))

# create a LoRa socket
s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)

# set the LoRaWAN data rate
s.setsockopt(socket.SOL_LORA, socket.SO_DR, 3)

while (1):
   # make the socket blocking
   # (waits for the data to be sent and for the 2 receive windows to expire)
   s.setblocking(True)
   print("Sending data!")
#        s.send(bytes([bytestream[4], bytestream[5], bytestream[6],bytestream[7],tempstruct[0],tempstruct[1],rhstruct[0],rhstruct[1],dewstruct[0],dewstruct[1],presstruct[0],presstruct[1],broadlumstruct[0],broadlumstruct[1],IRlumstruct[0],IRlumstruct[1]]))#,relativehumid,dewpoint]))
  
   s.send(bytes([0x00,0x22,0x00,0x12,0x00,0x13,0x00,0x25,0x00,0x0a,0x0b,0x0c,0x0d,0x0e,0x0f,0x10]))

   print('saving LoRa NVRAM')
   lora.nvram_save()
    # make the socket non-blocking
    # (because if there's no data received it will block forever...)
   s.setblocking(False)
   print("receiving data!")
    # get any data received (if any...)
   data = s.recv(64)
   print(data)
   print("Go to sleep 5 minutes!")
   time.sleep(300)    
