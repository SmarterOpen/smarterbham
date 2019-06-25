#placeholder for Silicon Labs digital light sensors library
#two versions of this are being tested for use, the SI1151 and the SI1132
#the 1132 were accidentally populated on the 10 prototype units, I intended to put the 1151..
#If the underlying code is radically different, may split this into separate libraries for each sensor
#SI1151 measures Ambient and IR light levels and outputs via I2C bus.
#there are 2 alternate versions of this chip, the 1152 and 1153, but these variants are mostly
#concerned with proximity detection and other purposes and the only difference is that some of the 
#unused pins are used to drive an illumination LED on command.
#Datasheet here: https://www.silabs.com/documents/public/data-sheets/si115x-datasheet.pdf
#SI1132 measures UV, Ambient and IR Light levels and outputs via I2C bus
#Datasheet here: https://www.silabs.com/documents/public/data-sheets/Si1132.pdf
#adafruit has an arduino library for the si1145, which may be somewhat similar
#https://github.com/adafruit/Adafruit_SI1145_Library
