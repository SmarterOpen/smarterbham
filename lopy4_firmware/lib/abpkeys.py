# Don't store or commit keys here.  This file shown for others to know what it should contain to make this work.
import struct
import ubinascii
dev_addr = struct.unpack(">l", ubinascii.unhexlify('00000000'))[0]
nwk_swkey = ubinascii.unhexlify('00000000000000000000000000000000')
app_swkey = ubinascii.unhexlify('00000000000000000000000000000000')
