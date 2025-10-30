# -*- coding: utf-8 -*-

import os
import time
import datetime
import threading


# RAM
MLX90614_I2CADDR = 0x5A
MLX90614_RAWIR1 = 0x04
MLX90614_RAWIR2 = 0x05
MLX90614_TA = 0x06
MLX90614_TOBJ1 = 0x07
MLX90614_TOBJ2 = 0x08

# EEPROM
MLX90614_TOMAX = 0x20
MLX90614_TOMIN = 0x21
MLX90614_PWMCTRL = 0x22
MLX90614_TARANGE = 0x23
MLX90614_EMISS = 0x24
MLX90614_CONFIG = 0x25
MLX90614_ADDR = 0x0E
MLX90614_ID1 = 0x3C
MLX90614_ID2 = 0x3D
MLX90614_ID3 = 0x3E
MLX90614_ID4 = 0x3F

RETRY_TIMES = 5

class TemperatureException(Exception):
    def __init__(self, err_str):
        self.err_reason = '%s.' % (err_str)

    def __str__(self):
        return self.err_reason

class Temperature(object):
    '''
    Temperature class provide to read temperature class.

    Args:
        dev_addr:   hexmial,             I2C device address of AD56X7R.
        i2c_bus:   instance(I2C)/None,  Class instance of I2C bus
        slot:  
    Examples:
        Temperature = Temperature(i2c,0x5A,1)
    '''

    rpc_public_api = ['read_ObjectTempF','read_AmbientTempF', 'read_ObjectTempC', 'read_AmbientTempC', 'read_start', 'read_stop']

    def __init__(self, i2c_bus, dev_addr, slot):
        self.i2c_bus = i2c_bus
        self.slot = slot
        self.dev_addr = dev_addr
        self.read_start_detect = False
        self.loop_read_thread = threading.Thread(target=self.read_loop).start()


    def read_ObjectTempF(self):
        return self.read(MLX90614_TOBJ1,'ram')*9 / 5 +32

    def read_AmbientTempF(self):
        return self.read(MLX90614_TA,'ram')* 9 / 5 + 32

    def read_ObjectTempC(self):
        return self.read(MLX90614_TOBJ1,'ram')

    def read_AmbientTempC(self):
        return self.read(MLX90614_TA,'ram')

    def read(self, reg_addr, regType):
        data = -999
        for i in range(RETRY_TIMES):
            try:
                if regType == "ram": 
                    reg_addr = reg_addr & 0x1F
                if regType == "eeprom":
                    reg_addr = (reg_addr & 0x1F) | 0x20
                datal, datah, pec = self.i2c_bus.write_and_read(self.dev_addr,[reg_addr],3)
                data = int(datah) << 8 | int(datal)
                data = data * 0.02 - 273.15
                break
            except Exception as e:
                continue
            time.sleep(1)
        return data

        # assert isinstance(devAddr, int)
        # assert isinstance(subAddr, int)
        # data = 0
        # try:
        #     read_data = self.temp.write_and_read(devAddr, [subAddr], 2)
        #     l_data = read_data[0]
        #     h_data = read_data[1]
        #     data = int(h_data) << 8 | int(l_data)
        #     data = data * 0.02 - 273.15
        # except Exception as e:
        #     data = -999
        # return data

    def timeStamp(self):
        current_time = "[ "+str(datetime.datetime.now())[:-7]+ " ]\t"
        return current_time

    def read_loop(self):
        while True:
            if self.read_start_detect:
                print(self.timeStamp() +'slot'+ str(self.slot) +': '+str(self.get_obj_temp()))
                time.sleep(1)
            else:
                time.sleep(1)
                continue

    def get_obj_temp(self):
        current_temp = self.read_ObjectTempC()
        print(self.timeStamp() +'slot'+ str(self.slot) +'before: '+str(current_temp))
        if current_temp > 82:
            current_temp = current_temp - 6
        elif current_temp > 60:
            current_temp = current_temp - 4.5
        elif current_temp > 40:
            current_temp = current_temp - 2
        return current_temp

    def read_start(self):
        self.read_start_detect = True
        return 'start read--->'

    def read_stop(self):
        self.read_start_detect = False
        return 'stop read--->'