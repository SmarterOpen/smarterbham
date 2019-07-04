# Don't store or commit keys here.  This file shown for others to know what it should contain to make this work.
import struct
import ubinascii
#abp keys - not in use.. TTN prefers OTAA
#dev_addr = struct.unpack(">l", ubinascii.unhexlify('00000000'))[0]
#nwk_swkey = ubinascii.unhexlify('00000000000000000000000000000000')
#app_swkey = ubinascii.unhexlify('00000000000000000000000000000000')
# create an OTAA authentication parameters
_dev_eui = ubinascii.unhexlify('0000000000000000')
_app_eui = ubinascii.unhexlify('0000000000000000')#70B3D57ED0011AF7')
_app_key = ubinascii.unhexlify('00000000000000000000000000000000')
