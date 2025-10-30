# -*- coding: utf-8 -*-
from mix.driver.core.bus.axi4_lite_def import PLI2CDef
from mix.driver.smartgiant.common.bus.i2c_bus_emulator import I2CBusEmulator


class MCP3221Def:
    max_12bit = 4095
    address = 0x4E
    ref_voltage = 5000
    WRITE_REG = 0x0
    READ_REG = 0x1


class MCP3221Exception(Exception):
    def __init__(self, err_str):
        self.err_reason = '%s.' % (err_str)

    def __str__(self):
        return self.err_reason


class MCP3221(object):
    rpc_public_api = ['read']

    def __init__(self, dev_addr=MCP3221Def.address, i2c_bus=None, mvref=MCP3221Def.ref_voltage):
        self._dev_addr = dev_addr
        self._mvref = float(mvref)
        if i2c_bus is None:
            self._i2c_bus = I2CBusEmulator('mcp3221_emulator', PLI2CDef.REG_SIZE)
        else:
            self._i2c_bus = i2c_bus

    def read(self):
        # getinfo = bytearray(2)
        getinfo = self._i2c_bus.read(self._dev_addr, 2)  # getinfo = [high_byte,low_byte]
        code = (getinfo[0] << 8) | getinfo[1]  # convert hex to int
        value_adc = code * self._mvref / MCP3221Def.max_12bit
        return value_adc
