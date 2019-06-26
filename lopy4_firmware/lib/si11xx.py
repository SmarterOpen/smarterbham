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

#will finish more later

#Set MEAS_RATE = 0 (Forced Measurement Mode) for lowest power consumption
#Set CHLIST to enable all 3 channels, ALS_VIS, ALS-IR, AUX(UV)
