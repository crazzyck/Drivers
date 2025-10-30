# -*- coding: utf-8 -*-
from mix.driver.core.bus.axi4_lite_def import PLI2CDef
from mix.driver.smartgiant.common.bus.i2c_bus_emulator import I2CBusEmulator

class MCP4728def:
    # command
    CHANNEL_CMD = [0x40, 0x42, 0x44, 0x46]
    WRITE_GAIN_CMD = 0xc0
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
    CHANNELS = [id for id in range(3)]
    POWER_DOWN_REG = 0x09
    GAIN_SETUP_REGISTER = 0x0A
    WIPERLOCK_REG = 0x0B
    

class MCP4728Exception(Exception):
    def __init__(self, dev_name, err_str):
        self._err_reason = '[%s]: %s.' % (dev_name, err_str)

    def __str__(self):
        return self._err_reason

class MCP4728(object):
    rpc_public_api = ["output_volt_dc"]

    def __init__(self, dev_addr, i2c_bus = None, mvref = 5000, dac_gain = 1):
        # assert dev_addr & (~0x01) == 0x60
        self._dev_addr = dev_addr
        self._mvref = float(mvref)
        if i2c_bus is None:
            ######
            self._i2c_bus = I2CBusEmulator('mcp4725_emulator', PLI2CDef.REG_SIZE)
            ######
        else:
            self._i2c_bus = i2c_bus
        self._dac_gain = dac_gain
        self.set_all_gain(1)

    def _write_register(self, command, high_byte, low_byte):
        print(high_byte, low_byte)
        self._i2c_bus.write(self._dev_addr, [command, high_byte, low_byte])


    def set_all_gain(self, gain):
        '''
        MCP4728 set all channel gain

        Args:
            gain:       int, [1, 2]
        Examples:
            MCP4728.set_all_gain(1)

        '''
        assert gain in [1, 2]
        if gain == 1:
            self._gain_register = MCP4728def.REG_GAIN_1 & 0x0  # 0b0000
        else:
            self._gain_register = MCP4728def.REG_GAIN_2 | 0xF  # 0b1111
        write_data = MCP4728def.WRITE_GAIN_CMD | self._gain_register
        self._i2c_bus.write(self._dev_addr, [write_data])

    def set_single_gain(self, channel, gain):
        '''
        MCP4728 set specific channel gain

        Args:
            channel:    int, [0~7], channel id.
            gain:       int, [1, 2]
        Examples:
            MCP4728.set_single_gain(0, 1)

        '''
        assert channel in MCP4728def.CHANNELS
        assert gain in [1, 2]
        if gain == 1:
            self._gain_register = MCP4728def.REG_GAIN_1
        else:
            self._gain_register = MCP4728def.REG_GAIN_2
        self._gain_register = self._gain_register << (3 - channel)
        write_data = MCP4728def.WRITE_GAIN_CMD | self._gain_register
        self._i2c_bus.write(self._dev_addr, [write_data])
        # self._write_register(MCP4728def.WRITE_REG, MCP4728def.GAIN_SETUP_REGISTER,
        #                      (self._gain_register >> 8) & 0xFF, self._gain_register & 0xFF)

    def output_volt_dc(self, channel, volt):
        '''
        MCP4728 output dc voltage

        Args:
            channel:    int, [0~7], channel id.
            volt:       float, output voltage value.

        Examples:
            MCP4728.output_volt_dc(0, 1000)

        '''
        assert channel in MCP4728def.CHANNELS
        assert isinstance(volt, (int, float)) and volt >= 0 and volt <= self._mvref
        # mode = MCP4728def.POWER_MODE_NORMAL
        # Output Voltage resolution is 8-bit
        dac_code = int(volt * float(4096) / self._mvref * self._dac_gain)
        if dac_code == 4096:
            dac_code = 4095
        high_byte = (dac_code >> 8) & 0xFF
        low_byte = dac_code & 0xFF
        channel = MCP4728def.CHANNEL_CMD[int(channel)]
        self._write_register(channel, high_byte, low_byte)

    
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
