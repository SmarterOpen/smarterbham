#Library space reserved for Bosch BME680 sensor
#this sensor outputs temperature, Humidity, Barometric Pressure and VOC (Volatile Organic Compounds) via the I2C bus
#there's existing code for Arduino for this so it shouldn't be hard to cross-compile to Python
#will link to it shortly.
#Bosch BME680 datasheet https://ae-bst.resource.bosch.com/media/_tech/media/datasheets/BST-BME680-DS001.pdf
#adafruit has a circuitpython example for BME680
#needs some modification since the ARM M0 micropython code is *slightly* different
#https://github.com/adafruit/Adafruit_CircuitPython_BME680

