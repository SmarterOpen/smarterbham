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
#
#Code copied from https://github.com/ControlEverythingCommunity/SI1132/blob/master/Python/SI1132.py 
#this needs to be tweaked to work with MicroPython
# Distributed with a free-will license.
# Use it any way you want, profit or free, provided it fits in the licenses of its associated works.
# SI1132
# This code is designed to work with the SI1132_I2CS I2C Mini Module available from ControlEverything.com.
# https://www.controleverything.com/content/Light?sku=SI1132_I2CS#tabs-0-product_tabset-2

import smbus
import time

bus = smbus.SMBus(1)
# SI1132 address, 0x60(96)
# Enable UVindex measurement coefficients
bus.write_byte_data(0x60, 0x13, 0x29)
bus.write_byte_data(0x60, 0x14, 0x89)
bus.write_byte_data(0x60, 0x15, 0x02)
bus.write_byte_data(0x60, 0x16, 0x00)

# SI1132 address, 0x60(96)
# Select PARAM_WR register, 0x17(23)
# 		0xF0(15)	Enable UV, Visible, IR
bus.write_byte_data(0x60, 0x17, 0xF0)
# SI1132 address, 0x60(96)
# Select COMMAND register, 0x18(24)
#		0x01 | 0xA0(161)   Select CHLIST register in RAM
bus.write_byte_data(0x60, 0x18, (0x01 | 0xA0))
time.sleep(0.01)
# SI1132 address, 0x60(96)
# Read data back from 0x2E(46), 1 byte
response = bus.read_byte_data(0x60, 0x2E)

# SI1132 address, 0x60(96)
# Select INT Output Enable register, 0x03(03)
#		0x01(01)	INT pin driven low
bus.write_byte_data(0x60, 0x03, 0x01)
# SI1132 address, 0x60(96)
# Select ALS Interrupt Enable register, 0x04(04)
#		0x01(01)	Assert INT pin whenever VIS or UV measurements are ready
bus.write_byte_data(0x60, 0x04, 0x01)
# SI1132 address, 0x60(96)
# Select HW_KEY register, 0x07(07)
#		0x17(23)	Default value
bus.write_byte_data(0x60, 0x07, 0x17)

# SI1132 address, 0x60(96)
# Select PARAM_WR register, 0x17(23)
#		0x00(0)		Small IR photodiode
bus.write_byte_data(0x60, 0x17, 0x00)
# SI1132 address, 0x60(96)
# Select COMMAND register, 0x18(24)
#		0x0E | 0xA0(174)    Select ALS_IR_ADCMUX register in RAM
bus.write_byte_data(0x60, 0x18, (0x0E | 0xA0))
time.sleep(0.01)
# SI1132 address, 0x60(96)
# Read data back from 0x2E(46), 1 byte
response = bus.read_byte_data(0x60, 0x2E)

# SI1132 address, 0x60(96)
# Select PARAM_WR register, 0x17(23)
#		0x00(0)		Set ADC Clock divided / 1
bus.write_byte_data(0x60, 0x17, 0x00)
# SI1132 address, 0x60(96)
# Select COMMAND register, 0x18(24)
#		0x1E | 0xA0(190)    Select ALS_IR_ADC_GAIN register in RAM
bus.write_byte_data(0x60, 0x18, (0x1E | 0xA0))
time.sleep(0.01)
# SI1132 address, 0x60(96)
# Read data back from 0x2E(46), 1 byte
response = bus.read_byte_data(0x60, 0x2E)

# SI1132 address, 0x60(96)
# Select PARAM_WR register, 0x17(23)
# 		0x70(112)	Set 511 ADC Clock
bus.write_byte_data(0x60, 0x17, 0x70)
# SI1132 address, 0x60(96)
# Select COMMAND register, 0x18(24)
#		0x1D | 0xA0(189)    Select ALS_IR_ADC_COUNTER register in RAM
bus.write_byte_data(0x60, 0x18, (0x1D | 0xA0))
time.sleep(0.01)
# SI1132 address, 0x60(96)
# Read data back from 0x2E(46), 1 byte
response = bus.read_byte_data(0x60, 0x2E)

# SI1132 address, 0x60(96)
# Select PARAM_WR register, 0x17(23)
# 		0x00(0)		Set ADC Clock divided / 1
bus.write_byte_data(0x60, 0x17, 0x00)
# SI1132 address, 0x60(96)
# Select COMMAND register, 0x18(24)
#		0x11 | 0xA0(177)    Select ALS_VIS_ADC_GAIN register in RAM
bus.write_byte_data(0x60, 0x18, (0x11 | 0xA0))
time.sleep(0.01)
# SI1132 address, 0x60(96)
# Read data back from 0x2E(46), 1 byte
response = bus.read_byte_data(0x60, 0x2E)

# SI1132 address, 0x60(96)
# Select PARAM_WR register, 0x17(23)
#		0x20(32)	High Signal Range
bus.write_byte_data(0x60, 0x17, 0x20)
# SI1132 address, 0x60(96)
# Select COMMAND register, 0x18(24)
#		0x1F | 0xA0(191)    Select ALS_IR_ADC_MISC register in RAM
bus.write_byte_data(0x60, 0x18, (0x1F | 0xA0))
time.sleep(0.01)
# SI1132 address, 0x60(96)
# Read data back from 0x2E(46), 1 byte
response = bus.read_byte_data(0x60, 0x2E)

# SI1132 address, 0x60(96)
# Select PARAM_WR register, 0x17(23)
# 		0x70(112)	Set 511 ADC Clock
bus.write_byte_data(0x60, 0x17, 0x70)
# SI1132 address, 0x60(96)
# Select COMMAND register, 0x18(24)
#		0x10 | 0xA0(176)    Select ALS_VIS_ADC_COUNTER register in RAM
bus.write_byte_data(0x60, 0x18, (0x10 | 0xA0))
time.sleep(0.01)
# SI1132 address, 0x60(96)
# Read data back from 0x2E(46), 1 byte
response = bus.read_byte_data(0x60, 0x2E)

# SI1132 address, 0x60(96)
# Select PARAM_WR register, 0x17(23)
#		0x20(32)	High Signal Range
bus.write_byte_data(0x60, 0x17, 0x20)
# SI1132 address, 0x60(96)
# Select COMMAND register, 0x18(24)
#		0x12 | 0xA0(178)    Select ALS_VIS_ADC_MISC register in RAM
bus.write_byte_data(0x60, 0x18, (0x12 | 0xA0))
time.sleep(0.01)
# SI1132 address, 0x60(96)
# Read data back from 0x2E(46), 1 byte
response = bus.read_byte_data(0x60, 0x2E)

# SI1132 address, 0x60(96)
# Select COMMAND register, 0x18(24)
#		0x0E(14)	Start ALS conversion
bus.write_byte_data(0x60, 0x18, 0x0E)
time.sleep(0.5)

# SI1132 address, 0x60(96)
# Read data back from 0x22(34), 4 bytes
# visible lsb, visible msb, ir lsb, ir msb
data = bus.read_i2c_block_data(0x60, 0x22, 4)

# Convert the data
visible = data[1] * 256 + data[0]
ir = data[3] * 256 + data[2]

# SI1132 address, 0x60(96)
# Read data back from 0x2C(44), 2 bytes
# uv lsb, uv msb
data = bus.read_i2c_block_data(0x60, 0x2C, 2)

# Convert the data
uv = data[1] * 256 + data[0]

# Output data to screen
print "Visible Light of Source : %d lux" %visible
print "IR Of Source : %d lux" %ir
print "UV Of the Source : %d lux" %uv


#SI1132 process
#U8 ReadFromRegister(U8 reg)          returns byte from I2C Register reg
#void WriteToRegister(U8 reg,U8 Val)  Writes Value into I2C Register reg
#void ParamSet(U8 Addr,U8 Val)        Writes Value to Parameter Address

#Send hardware key
#I2C register 0x07 = 0x17
#WriteToRegister(Reg_HW_Key, HW_Key_Val0)

#Initialize LED Current
#I2C Register 0x0f = OxFF
#I2C Register 0x10 = 0x0F
#WriteToRegister(Reg_PS_LED21,(Max_LED_Current<<4) + Max_LED_Current)
#WriteToRegister(Reg_PS_LED3, Max_LED_Current

#Parameter 0x01 = 0x37
#ParamSet(Param_CH_List,ALS_IR_TASK + ALS_VIS_TASK + PS1_TASK + PS2_TASK + PS3_TASK)

#I2C Register 0x18 = 0x07
#WriteToRegister(REG_Command,0x07)

#Once measurement complete, here is how to reconstruct them
#Note that 16-bit register are in 'Little Endian' byte order
# May be more efficien tto perform block I2C Reads, but this example shows individual register reads

#ALS_VIS = ReadFromRegister(REG_ALS_VIS_DATA0) + 256 * ReadFromRegister(REG_ALS_VIS_DATA1)
#ALS_IR = ReadFromRegister(REG_ALS_IR_DATA0) + 256 * ReadFromRegister(REG_ALS_IR_DATA1)
#ALS_PS1 = ReadFromRegister(REG_ALS_PS1_DATA0) + 256 * ReadFromRegister(REG_ALS_PS1_DATA1)
#ALS_PS2 = ReadFromRegister(REG_ALS_PS2_DATA0) + 256 * ReadFromRegister(REG_ALS_PS2_DATA1)
#ALS_PS3 = ReadFromRegister(REG_ALS_PS3_DATA0) + 256 * ReadFromRegister(REG_ALS_PS3_DATA1)

#If using autonomous read mode, pause autonomous operation before modifying parameters to avoid ADC overflow or errors
#void pauseMeasurement(void)
#{
#   if (measurementPaused)
#      return;
#   WriteToRegister(Reg_IRQ_CFG,0); Tri-state INT pin to stop interrupts (We're not using Int pin anyways)
#   /Need to make sure machine paused 
#   While(1)
#   {
#      if (GetResponse() ==0)
#         break;
#      else
#         Nop();
#   }
#   //Pause device
#   PsAlsPause();
#// Wait for response
#while(1)
#{
#if (GetResponse() != 0)
#break;
#}
#// When the PsAlsPause() response is good, we expect it to be a '1'.
#if (GetResponse() == 1)
#break; // otherwise, start over.
#}
#measurementPaused = 1;

#resume autonomous measurements
#void resumeMeasurement(void)
#{
#   if (!measurementPaused)
#      return;
#   ClearIrqStatus(IE_ALL);
#   WriteToRegister(REG_IRQ_CFG, ICG_INTOE); // re-enables INT pin
#   PsAlsAuto();
#   measurementPaused = 0;
#}

#will finish more later

#Set MEAS_RATE = 0 (Forced Measurement Mode) for lowest power consumption
#Set CHLIST to enable all 3 channels, ALS_VIS, ALS-IR, AUX(UV)
