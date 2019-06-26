# Original library was from https://github.com/ThingType/HPMA115S0_Python_library but intended for Raspberry Pi
# Modifying to work with Pycom Lopy4

#BME680 project from Micropython.. may need some modifications to run
#import bme680
#from i2c import I2CAdapter

#VEML6070 code for Python on Raspberry Pi 2/3
import veml6070


from hpma115s0 import HPMA115S0
import time
from machine import UART

#BME680 project from Micropython.. may need some modifications to run.. Actually, looks like it was written for Pycom Wipy
#i2c_dev = I2CAdapter()
#sensor = bme680.BME680(i2c_device=i2c_dev)

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

#BME680 project from Micropython.. may need some modifications to run.. Actually, looks like it was written for Pycom Wipy
#Init the BME680
# These oversampling settings can be tweaked to
# change the balance between accuracy and noise in
# the data.
#sensor.set_humidity_oversample(bme680.OS_2X)
#sensor.set_pressure_oversample(bme680.OS_4X)
#sensor.set_temperature_oversample(bme680.OS_8X)
#sensor.set_filter(bme680.FILTER_SIZE_3)


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
   
#BME680 project from Micropython.. may need some modifications to run.. Actually, looks like it was written for Pycom Wipy
#   try:
#    while True:
#        if sensor.get_sensor_data():
#
#            output = "{} C, {} hPa, {} RH, {} RES,".format(
#                sensor.data.temperature,
#                sensor.data.pressure,
#                sensor.data.humidity,
#                sensor.data.gas_resistance)
#
#            print(output)
#            time.sleep(1)
#except KeyboardInterrupt:
#    pass

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

   time.sleep(300)#wait 5 minutes before next reading
