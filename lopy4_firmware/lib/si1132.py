# downloaded from https://github.com/JuniorJPDJ/micropython-si1132 on 2020-03-11 Dan Near
import time

SI1132_I2C_ADDR = 0x60
SI1132_PARTID = 0x32

cmds = {
        'Si1132_PARAM_QUERY'    : 0x80,
        'Si1132_PARAM_SET'      : 0xA0,
        'Si1132_NOP'            : 0x00,
        'Si1132_RESET'          : 0x01,
        'Si1132_BUSADDR'        : 0x02,
        'Si1132_GET_CAL'        : 0x12,
        'Si1132_ALS_FORCE'      : 0x06,
        'Si1132_ALS_PAUSE'      : 0x0A,
        'Si1132_ALS_AUTO'       : 0x0E,
}

params = {
        'Si1132_PARAM_I2CADDR'              : 0x00,
        'Si1132_PARAM_CHLIST'               : 0x01,
        'Si1132_PARAM_CHLIST_ENUV'          : 0x80,
        'Si1132_PARAM_CHLIST_ENAUX'         : 0x40,
        'Si1132_PARAM_CHLIST_ENALSIR'       : 0x20,
        'Si1132_PARAM_CHLIST_ENALSVIS'      : 0x10,
        'Si1132_PARAM_ALSENCODING'          : 0x06,
        'Si1132_PARAM_ALSIRADCMUX'          : 0x0E,
        'Si1132_PARAM_AUXADCMUX'            : 0x0F,
        'Si1132_PARAM_ALSVISADCCOUNTER'     : 0x10,
        'Si1132_PARAM_ALSVISADCGAIN'        : 0x11,
        'Si1132_PARAM_ALSVISADCMISC'        : 0x12,
        'Si1132_PARAM_ALSVISADCMISC_VISRANGE' : 0x20,
        'Si1132_PARAM_ALSIRADCCOUNTER'      : 0x1D,
        'Si1132_PARAM_ALSIRADCGAIN'         : 0x1E,
        'Si1132_PARAM_ALSIRADCMISC'         : 0x1F,
        'Si1132_PARAM_ALSIRADCMISC_RANGE'   : 0x20,
        'Si1132_PARAM_ADCCOUNTER_511CLK'    : 0x70,
        'Si1132_PARAM_ADCMUX_SMALLIR'       : 0x00,
        'Si1132_PARAM_ADCMUX_LARGEIR'       : 0x03,
}

regs = {
        'Si1132_REG_PARTID'         : 0x00,
        'Si1132_REG_REVID'          : 0x01,
        'Si1132_REG_SEQID'          : 0x02,
        'Si1132_REG_INTCFG'         : 0x03,
        'Si1132_REG_INTCFG_INTOE'   : 0x01,
        'Si1132_REG_IRQEN'          : 0x04,
        'Si1132_REG_IRQEN_ALSEVERYSAMPLE' : 0x01,
        'Si1132_REG_IRQMODE1'       : 0x05,
        'Si1132_REG_IRQMODE2'       : 0x06,
        'Si1132_REG_HWKEY'          : 0x07,
        'Si1132_REG_MEASRATE0'      : 0x08,
        'Si1132_REG_MEASRATE1'      : 0x09,
        'Si1132_REG_UCOEF0'         : 0x13,
        'Si1132_REG_UCOEF1'         : 0x14,
        'Si1132_REG_UCOEF2'         : 0x15,
        'Si1132_REG_UCOEF3'         : 0x16,
        'Si1132_REG_PARAMWR'        : 0x17,
        'Si1132_REG_COMMAND'        : 0x18,
        'Si1132_REG_RESPONSE'       : 0x20,
        'Si1132_REG_IRQSTAT'        : 0x21,
        'Si1132_REG_ALSVISDATA0'    : 0x22,
        'Si1132_REG_ALSVISDATA1'    : 0x23,
        'Si1132_REG_ALSIRDATA0'     : 0x24,
        'Si1132_REG_ALSIRDATA1'     : 0x25,
        'Si1132_REG_UVINDEX0'       : 0x2C,
        'Si1132_REG_UVINDEX1'       : 0x2D,
        'Si1132_REG_PARAMRD'        : 0x2E,
        'Si1132_REG_CHIPSTAT'       : 0x30,
}


class SI1132:
    def __init__(self, i2c):
        self.i2c = i2c  # type: machine.I2C
        self.id = self.read_reg8(0x00)
        if self.id != SI1132_PARTID:
            print("Wrong Device ID [", hex(self.id), "]")
            exit()

        self.reset()

        self.write_reg(regs['Si1132_REG_UCOEF0'], b'\x7B')
        self.write_reg(regs['Si1132_REG_UCOEF1'], b'\x6B')
        self.write_reg(regs['Si1132_REG_UCOEF2'], b'\x01')
        self.write_reg(regs['Si1132_REG_UCOEF3'], b'\x00')

        param = params['Si1132_PARAM_CHLIST_ENUV'] | params['Si1132_PARAM_CHLIST_ENALSIR'] | params['Si1132_PARAM_CHLIST_ENALSVIS']
        self.write_param(params['Si1132_PARAM_CHLIST'], param)

        self.write_reg(regs['Si1132_REG_INTCFG'], bytes([regs['Si1132_REG_INTCFG_INTOE']]))
        self.write_reg(regs['Si1132_REG_IRQEN'], bytes([regs['Si1132_REG_IRQEN_ALSEVERYSAMPLE']]))

        self.write_param(params['Si1132_PARAM_ALSIRADCMUX'], params['Si1132_PARAM_ADCMUX_SMALLIR'])
        time.sleep(0.01)
        self.write_param(params['Si1132_PARAM_ALSIRADCGAIN'], 0)
        time.sleep(0.01)
        self.write_param(params['Si1132_PARAM_ALSIRADCCOUNTER'], params['Si1132_PARAM_ADCCOUNTER_511CLK'])
        self.write_param(params['Si1132_PARAM_ALSIRADCMISC'], params['Si1132_PARAM_ALSIRADCMISC_RANGE'])
        time.sleep(0.01)
        self.write_param(params['Si1132_PARAM_ALSIRADCGAIN'], 0)
        time.sleep(0.01)
        self.write_param(params['Si1132_PARAM_ALSIRADCCOUNTER'], params['Si1132_PARAM_ADCCOUNTER_511CLK'])
        self.write_param(params['Si1132_PARAM_ALSVISADCMISC'], params['Si1132_PARAM_ALSVISADCMISC_VISRANGE'])
        time.sleep(0.01)
        self.write_reg(regs['Si1132_REG_MEASRATE0'], b'\xFF')
        self.write_reg(regs['Si1132_REG_COMMAND'], bytes([cmds['Si1132_ALS_AUTO']]))
        time.sleep(0.01)

    def reset(self):
        self.write_reg(regs['Si1132_REG_MEASRATE0'], b'\x00')
        self.write_reg(regs['Si1132_REG_MEASRATE1'], b'\x00')
        self.write_reg(regs['Si1132_REG_IRQEN'], b'\x00')
        self.write_reg(regs['Si1132_REG_IRQMODE1'], b'\x00')
        self.write_reg(regs['Si1132_REG_IRQMODE2'], b'\x00')
        self.write_reg(regs['Si1132_REG_INTCFG'], b'\x00')
        self.write_reg(regs['Si1132_REG_IRQSTAT'], b'\xFF')
        self.write_reg(regs['Si1132_REG_COMMAND'], bytes([cmds['Si1132_RESET']]))
        time.sleep(0.01)
        self.write_reg(regs['Si1132_REG_HWKEY'], b'\x17')
        time.sleep(0.01)

    def read_reg8(self, reg):
        return int.from_bytes(self.i2c.readfrom_mem(SI1132_I2C_ADDR, reg, 1), 'little')

    def read_reg16(self, reg):
        return int.from_bytes(self.i2c.readfrom_mem(SI1132_I2C_ADDR, reg, 2), 'little')

    def write_reg(self, reg, val):
        self.i2c.writeto_mem(SI1132_I2C_ADDR, reg, val)

    def write_param(self, param, val):
        self.write_reg(regs['Si1132_REG_PARAMWR'], bytes([val]))
        self.write_reg(regs['Si1132_REG_COMMAND'], bytes([param | cmds['Si1132_PARAM_SET']]))

    def read_visible(self):
        return ((self.read_reg16(0x22) - 256) / 0.282) * 14.5

    def read_IR(self):
        return ((self.read_reg16(0x24) - 250) / 2.44) * 14.5

    def read_UV(self):
        return self.read_reg16(0x2c)
