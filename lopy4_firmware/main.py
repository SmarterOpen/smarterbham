# Original library was from https://github.com/ThingType/HPMA115S0_Python_library but intended for Raspberry Pi
# Modifying to work with Pycom Lopy4

#BME680 project from Micropython.. may need some modifications to run
import nets  #used by Wifi interface
import machine
import bme680 #used for BME680 sensor code
from i2c import I2CAdapter #used by BME680 and other I2C sensors
from network import LoRa #used to publish data on the LoRa network
import socket #used for various WiFi and Lora connections
import ubinascii #Used to pack/unpack byte segments for sending data to LoRa
import struct #Used to pack/unpack byte segments for sending data to LoRa
import time #used for sleep commands
import utime #used for timing commands
import os
import math
import lorakeys #store the active LoRa private keys to send data to TheThingsNetwork
import pycom #Used to publish data to PyBytes thru Send_Signal
import ustruct #Used to pack/unpack byte segments for sending data to LoRa
import si1132
from machine import UART, I2C,Pin #enable the I2C bus
adc = machine.ADC()             # create an ADC object
adc.init(bits=12)
apin = adc.channel(pin='P13',attn=3)   # create an analog pin on P13 to measure incoming battery voltage thru a 2Mohm / 178kohm divider network, scaling 40v to 3.3v

pycom.heartbeat(False) #needs to be disabled for LED functions to work
pycom.rgbled(0x7f0000) #red

def getBattery():
  Batt=0
  i=0
  while (i<20):#take 20 readings and average it to get a more consistent value
    val = apin()*0.011849#calculated based on testing.  Voltage divider with 2Mohm resistor on high side and 178kohm with a parallelled 100nF cap on low side
    #this scales the 40v max input voltage down to 3.3v
    Batt+=val
    i+=1
  BattAverage=Batt/20.0
  print('Battery Voltage = ',BattAverage)
  return BattAverage

#get online using known nets if available
#Do this before working with anything else.. Because some code faults will kick you offline unless you're in range of the primary network in pybytes_config.json
#If that happens... set up a cellphone as a hotspot using the SAME credentials as the primary network in pybytes_config.json and reboot the sensors
#then when it gets back online, you can fix the code, push it and turn off the hotspot..
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
        
        
        
#added in code to make this code base work across all active assembles irregardless of which sensors are built in
HasSi1132=False #disable all inactive codes and activate the ones detected.
HasBME680=False
HasSi1151=False
HasGUVA=False
HasGUVB=False
HasVEML6075=False


i2c = I2C(0, pins=("P9","P10"))
i2c.init(I2C.MASTER, baudrate=100000)
activesensors=i2c.scan()#Scan for active I2C devices and store in a tuple
pybytes.send_signal(2,len(activesensors))
if len(activesensors)>0:#see if any devices were detected.
  for c in range (0,len(activesensors)):#enable code for any found sensors
    pybytes.send_signal(2,activesensors[c])#publish detected sensors to Pybytes for remote diagnostics
    time.sleep(1)#have to sleep 1s between each pybytes.send_signal
    if activesensors[c]==118:#0x60 IE bme680 - Sensor works but some boards may need calibration/ burn in to correct stuck VOC resistance.
      HasBME680=True
    if activesensors[c]==96:#0x60 IE Si1132 - Sensor marked EOL but may exist in some assemblies.  Code works but needs fine-tuning to work properly between low and high intensity
      HasSi1132=True
    if activesensors[c]==83:#0x60 IE Si1151 - Currently active sensor.  Note some old sensors may have wrong address 
      HasSi1151=True
    if activesensors[c]==81:#0x60 IE Si1151 - Currently active sensor.  Note some old sensors may have wrong address due to manufacturing defect.  They still work.
      HasSi1151wa=True# this is a rare batch of parts that has the wrong i2c address
    if activesensors[c]==56:#0x60 IE GenUV Sensor for UV-A - Small batch of sensors were assembled - the chip costs $45 in low quantities
      HasGUVA=True
    if activesensors[c]==57:#0x60 IE GenUV Sensor for UV-B - Small batch of sensors were assembled - the chip costs $45 in low quantities
      HasGUVB=True
    if activesensors[c]==20:#0x10 7 bit slave address per datasheet - sensor discontinued but may exist in some assemblies
      HasVEML6075=True
    if activesensors[c]==112:#0x38 7 bit slave address per datasheet - sensor discontinued but may exist in some assemblies
      HasVEML6070=True
    elif activesensors[c]==45:# not used yet.
      sensors2=True
    
    
  
i2c_dev = I2CAdapter()
if HasBME680 == True:
  sensor = bme680.BME680(i2c_device=i2c_dev)
if HasSi1132 == True:
  si = si1132.SI1132(i2c_dev)

#Older dust sensors have a 2 year life unless the fan is cycled on/off between readings. 
#These older sensors also don't respond to commands that would activate the fan properly,
#So I added a MOSFET to switch the fan power remotely to put it into low power mode.
#Typical power consumption is 80mA for the sensor alone.. so cutting the sensor off saves A LOT of power
DUSTEN = Pin('P23', mode=Pin.OUT)
PinOn=1
PinOff=0
#DUSTEN.value(PinOn)
DUSTEN.value(PinOff)
print("turning fan off")



# Initialise LoRa in LORAWAN mode.
# Please pick the region that matches where you are using the device:
# Asia = LoRa.AS923
# Australia = LoRa.AU915
# Europe = LoRa.EU868
# United States = LoRa.US915
#lora = LoRa(mode=LoRa.LORAWAN, region=LoRa.US915)

#Above code bypassed because I needed to manually select the correct frequencies to work properly in the US.
#Otherwise, it wanted to send to 64 channels randomly and 88% would be to inactive channels for that region
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


print('US channels set')
time.sleep(1)
print('Joining LoRa via OTAA')

# join a network using ABP (Activation By Personalization)  This was highly problematic because when the sensor lost power, the sent counter would reset and no data would get thru
#lora.join(activation=LoRa.ABP, auth=(dev_addr, nwk_swkey, app_swkey))
# join a network using OTAA (Over the Air Activation)
lora.join(activation=LoRa.OTAA, auth=(lorakeys._dev_eui,lorakeys._app_eui, lorakeys._app_key), timeout=0, dr=0)

#currently, this waits to join a channel.. but if no LoRa devices are available, it would stick here forever
#I want to eventually set this up so it checks for WIFI first.. and sends direct to AWS.. If Wifi isn't available, fallback to LoRa
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

#send a status to Pybytes that we made it past the first few states (IE LoRa)
pybytes.send_signal(2,0)
#BME680 project from Micropython.. written for Pycom Wipy but doesn't utilize the proprietary module to manage/convert the VOC data
#Init the BME680
# These oversampling settings can be tweaked to
# change the balance between accuracy and noise in
# the data.
if HasBME680 == True:

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
#send a status update to Pybytes that we're about to start the Loop
pybytes.send_signal(2,1)

while 1:
  print("Looping")
  DUSTEN.value(PinOn)
  print("turning fan on")
  #hpma115S0.startParticleMeasurement()#Wake up the HOneywell dust sensor
  time.sleep(6)#Give Honeywell sensor 6 seconds for readings to normalize
  inp='' #zero out the input buffer
  recv=[]#zero out the receive tuple
  dump=uart.read()#zero out the receive buffer
  start=utime.ticks_ms()#set up a start point for sensor timeout
  pm10=ustruct.pack('>H',int(0))#put some null values in these registers in case there's no HPMA sensor found
  pm25=ustruct.pack('>H',int(0))
  pm1=ustruct.pack('>H',int(0))
  pm4=ustruct.pack('>H',int(0))
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
          checkforcompact=recv[4]+recv[5]+recv[10]+recv[11]#the Compact version of the HPMA115 has additional pm1 and pm4 values..Add these bytes together
          #but the stupid thing is, they rearrange the byte locations rather than use unused bytes in the old 32 byte packet
          #this is infuriating since there's no legitimate way to differentiate the sensors in code EXCEPT hope that there should never be ZERO for any of the particulate values
          if checkforcompact==0:#If the bytes you added together are all zero, then we MOST LIKELY have the old non-compact sensor. *fingerscrossed*
            pm10=ustruct.pack('>H',int((recv[6]*256)+recv[7]))
            pm25=ustruct.pack('>H',int((recv[8]*256)+recv[9]))
          else:
            pm1=ustruct.pack('>H',int((recv[4]*256)+recv[5]))
            pm25=ustruct.pack('>H',int((recv[6]*256)+recv[7]))
            pm4=ustruct.pack('>H',int((recv[8]*256)+recv[9]))
            pm10=ustruct.pack('>H',int((recv[10]*256)+recv[11]))
          break
        else:
          print('recv=',recv)#we failed the checksum, so publish some diagnostic data for troubleshooting
          print('checksum fail',sent,'!=',calc)
      else:
        print('second char mismatch =',inp)# first character matched but second didn't..  This should never happen?

  DUSTEN.value(PinOff)
  print("turning fan off")

   
#BME680 project from Micropython.. may need some modifications to run.. Actually, looks like it was written for Pycom Wipy
  tempstruct=ustruct.pack('>H',int(0))#lets start by zeroing out the structs used to send to LoRa in case the sensor isn't found, we can still publish everything else
  dewstruct=ustruct.pack('>H',int(0))
  pressstruct=ustruct.pack('>H',int(0))
  relhumidstruct=ustruct.pack('>H',int(0))
  vocStruct=ustruct.pack('>L',int(0))

  if HasBME680 == True:#if the BME was detected, get some data.

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
        vocStruct=ustruct.pack('>L',int(sensor.data.gas_resistance))

    except Exception as e:
      print('DEBUG :: @Get Reading from the BME680 :: Exception: ' + str(e))#oops, something went wrong,, publish some diagnostic data to troubleshoot
      pass
    
#let's look for some light sensor data
#but first, let's zero out the placeholders
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
  broadlumstruct=struct.pack(">h",broadlum)
  IRlumstruct=struct.pack(">h",IR)
  Battery=getBattery() #measure the input voltage on P13
  BattStruct=ustruct.pack('>H',int(Battery*10))#use an int instead of a float with 1 decimal accuracy, on TTN packet decoder this gets divided by 10

  s.setblocking(True)
  print("Sending data!")
  s.send(bytes([pm25[0],pm25[1],pm10[0],pm10[1],#Particulate values for pm2.5 and pm10
                 tempstruct[0],tempstruct[1],#Temperature
                 relhumidstruct[0],relhumidstruct[1],#Relative Humidity
                 dewstruct[0],dewstruct[1],#dewpoint
                 pressstruct[0],pressstruct[1],#Barometric Pressure
                 0x00,0x00,#This is a placeholder for UV data from the Si1133
                 broadlumstruct[0],broadlumstruct[1],
                 IRlumstruct[0],IRlumstruct[1],
                 vocStruct[0],vocStruct[1],vocStruct[2],vocStruct[3],#VOC Resistance
                 pm1[0],pm1[1],pm4[0],pm4[1],#particulate values for pm1 and pm4
                 BattStruct[0],BattStruct[1]#Battery Voltage
               ]))
   
#Publish duplicate data to Pybytes.. Have to put a 1s delay between each packet or it will reject them.. Them's the Pybytes rules, not mine!
  pybytes.send_signal(0,(pm25[0]*256)+pm25[1])
  time.sleep(1)
  pybytes.send_signal(1,(pm10[0]*256)+pm10[1])
  time.sleep(1)
  pybytes.send_signal(3,sensor.data.gas_resistance)#This is frustrating as frig... Pybytes treats this as a Signed Long not an Unsigned Long.. So the data looks wierd sometimes if the value is high IE > 0xF000 0000
  time.sleep(1)
  pybytes.send_signal(4,int(sensor.data.temperature))
  time.sleep(1)
  pybytes.send_signal(5,int(sensor.data.humidity))
  time.sleep(1)
  pybytes.send_signal(6,int(sensor.data.dew_point))
  time.sleep(1)
  pybytes.send_signal(7,int(sensor.data.pressure*0.2952998307)/10)#this is frustrating as well.. pybytes takes this in as a float and blows the decimal to kingdom come.. it should be a 0.1 InHg value but pybytes displays it to 10 places..
  time.sleep(1)
  pybytes.send_signal(8,broadlum)
  time.sleep(1)
  pybytes.send_signal(10,IR)
  time.sleep(1)
  pybytes.send_signal(11,(pm1[0]*256)+pm1[1])
  time.sleep(1)
  pybytes.send_signal(12,(pm4[0]*256)+pm4[1])
  time.sleep(1)
  pybytes.send_signal(13,Battery)
 
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

 
