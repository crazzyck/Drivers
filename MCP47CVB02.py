# -*- coding: utf-8 -*-
from mix.driver.core.bus.axi4_lite_def import PLI2CDef
from mix.driver.smartgiant.common.bus.i2c_bus_emulator import I2CBusEmulator


class MCP47CVB02def:
    # command
    WRITE_REG = 0x00
    READ_REG = 0x11
    ENABLE_CONFIG = 0x10
    DISABLE_CONFIG = 0x01

    # mode
    POWER_MODE_NORMAL = 0x00
    POWER_MODE_1KOHM = 0x01
    POWER_MODE_100KOHM = 0x02
    OPEN_CIRCUIT = 0x03

    # Gain register
    REG_GAIN_1 = 0x00
    REG_GAIN_2 = 0x01

    # memory map address
    POWER_DOWN_REG = 0x09
    GAIN_SETUP_REGISTER = 0x0A
    WIPERLOCK_REG = 0x0B


class MCP47CVB02Exception(Exception):
    def __init__(self, dev_name, err_str):
        self._err_reason = '[%s]: %s.' % (dev_name, err_str)

    def __str__(self):
        return self._err_reason


class MCP47CVB02(object):
    rpc_public_api = ['set_all_gain', 'set_single_gain', 'output_volt_dc', 'output_reset']

    def __init__(self, dev_addr, i2c_bus=None, mvref=5000.0, dac_gain=1):
        # assert dev_addr & (~0x01) == 0x60
        self._dev_addr = dev_addr
        self._mvref = float(mvref)
        if i2c_bus is None:
            ######
            self._i2c_bus = I2CBusEmulator('MCP47CVB02_emulator', PLI2CDef.REG_SIZE)
            ######
        else:
            self._i2c_bus = i2c_bus
        self._dac_gain = dac_gain
        self.set_all_gain(1)

    def _write_register(self, command, address, high_byte, low_byte):
        self._i2c_bus.write(self._dev_addr, [(command << 1) | (address << 3), high_byte, low_byte])

    def set_all_gain(self, gain):
        '''
        MCP47CVB02 set all channel gain

        Args:
            gain:       int, [1, 2]
        Examples:
            MCP47CVB02.set_all_gain(1)

        '''
        assert gain in [1, 2]
        if gain == 1:
            self._gain_register = MCP47CVB02def.REG_GAIN_1 & 0x00  # 0b00000000
        else:
            self._gain_register = MCP47CVB02def.REG_GAIN_2 | 0xFF  # 0b11111111
        # self._gain_register = (MCP47CVB02def.REG_GAIN_1 if gain == 1 else MCP47CVB02def.REG_GAIN_2)
        self._write_register(MCP47CVB02def.WRITE_REG, MCP47CVB02def.GAIN_SETUP_REGISTER,
                             (self._gain_register >> 8) & 0xFF, self._gain_register & 0xFF)

    def set_single_gain(self, gain):
        '''
        MCP47CVB02 set specific gain

        Args:
            gain:       int, [1, 2]
        Examples:
            MCP47CVB02.set_single_gain(1)

        '''
        assert gain in [1, 2]
        if gain == 1:
            self._gain_register = MCP47CVB02def.REG_GAIN_1
        else:
            self._gain_register = MCP47CVB02def.REG_GAIN_2

        self._write_register(MCP47CVB02def.WRITE_REG, MCP47CVB02def.GAIN_SETUP_REGISTER,
                             (self._gain_register >> 8) & 0xFF, self._gain_register & 0xFF)

    def output_volt_dc(self, channel, volt):
        '''
        MCP47CVB02 output dc voltage

        Args:
            channel:    int, [0~1], channel id.
            volt:       float, output voltage value.

        Examples:
            MCP47CVB02.output_volt_dc(0, 1000)

        '''
        assert channel in [0, 1]
        assert isinstance(volt, (int, float)) and 0 <= volt <= self._mvref
        # mode = MCP47CVB02def.POWER_MODE_NORMAL
        # Output Voltage resolution is 8-bit
        dac_code = int(volt * float(255) / self._mvref * self._dac_gain)
        high_byte = (dac_code >> 8) & 0xFF
        low_byte = dac_code & 0xFF
        self._write_register(MCP47CVB02def.WRITE_REG, channel, high_byte, low_byte)

    def output_reset(self):
        # self._write_operation([0x0, 0x0])
        self._i2c_bus.write(self._dev_addr, [0x0, 0x0])

    '''
    def _read_operation(self, len):
        self._i2c_bus.read(self._dev_addr, len)

    def _write_operation(self, data):
        assert isinstance(data, list)
        assert all(isinstance(x, int) and x >= 0 for x in data)
        self.i2c_bus.write(self.dev_addr, data)
    '''
