#!/usr/bin/env python
"""LIS3DH, module for use with a LIS3DH accelerometer

created Mar 27, 2017 OM
work in progress - Mar 30, 2017 OM"""

"""
Copyright 2017 Owain Martin

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import time, spidev, sys, smbus

class Accelerometer:

    def __init__(self, mode, i2cAddress = 0x0, spiPort = 0, spiCS = 0):

        self.mode = mode
        self.scale = 2
        self.odr = 50
        self.temperatureOffset = 0        

        if self.mode == 'spi':
            self.spi=spidev.SpiDev()
            self.spi.open(spiPort,spiCS)
        else:  #i2C
            self.bus = smbus.SMBus(1)
            self.addr = i2cAddress

    def single_access_read(self, reg=0x00):
        """single_access_read, function to read a single data register
        of the LIS3DH"""

        rwBit = 0b1  # read/write bit set to read
        msBit = 0b1  # multiple read/write address increment select bit set to auto increment

        if self.mode == 'spi':
            dataTransfer=self.spi.xfer2([(rwBit<<7)+(msBit<<6)+reg,0])

            # for testing
            #print(hex(reg), hex(dataTransfer[1]),bin(dataTransfer[1]))
            
            return dataTransfer[1]
        
        else: #i2c
            dataTransfer=self.bus.read_byte_data(self.addr,reg)
            return dataTransfer
       

    def single_access_write(self, reg=0x00, regValue=0x0):
        """single_access_write, function to write a single data register
        of the LIS3DH"""

        rwBit = 0b0  # read/write bit set to write
        msBit = 0b1  # multiple read/write address increment select bit set to auto increment

        if self.mode == 'spi':
            dataTransfer=self.spi.xfer2([(rwBit<<7)+(msBit<<6)+reg,regValue])
            # for testing
            #print(bin((rwBit<<7)+(msBit<<6)+reg),hex(reg), hex(regValue), hex(dataTransfer[1]))
            
        else: #i2c
            self.bus.write_byte_data(self.addr, reg, regValue)    

        return

    def twos_complement_conversion(self, msb, lsb):
        """twos_complement_conversion, function to change the 10 bit value
        split across 2 bytes from 2s complement to normal binary/decimal. Also
        the left justification of the 10 bits is removed.

        msb = most significant byte
        lsb = least significant byte"""

        signBit= (msb & 0b10000000)>>7
        msb = msb & 0x7F  # strip off sign bit
        #print('signBit',signBit)

        if signBit == 1:  # negative number        
            x = (msb<<8) + lsb
            x = x^0x7FFF
            x = -(x + 1)
        else: # positive number        
            x = (msb<<8) + lsb

        x = x>>6  # remove left justification of data    

        return x

    def axis_enable(self, x='on',y='on',z='on'):
        """axis_enable, function to enable/disable the x, y and z axis"""

        xBit = 0b1   # default value - 'on'
        yBit = 0b1   # default value - 'on'
        zBit = 0b1   # default value - 'on'

        CTRL_REG1 = self.single_access_read(0x20)

        if x == 'off':
            xBit = 0b0

        if y == 'off':
            yBit = 0b0

        if z == 'off':
            zBit = 0b0

        CTRL_REG1 = CTRL_REG1 & 0b11111000
        CTRL_REG1 = CTRL_REG1 | ((zBit<<2) + (yBit<<1) + xBit)

        #print (bin(CTRL_REG1)) # for testing

        self.single_access_write(0x20, CTRL_REG1)

        return 

    def disable_temperature(self, adcOn='on'):
        """disable_temperature, function to disable the on board temperature
        sensor. This sets bit 6 and optionally bit 7 of TEMP_CFG_REG (0x1F)"""       

        TEMP_CFG_REG = self.single_access_read(0x1F)

        adcBit = 0b1  # default value

        if adcOn == 'off':
            adcBit = 0b0

        TEMP_CFG_REG = TEMP_CFG_REG & 0b00111111
        TEMP_CFG_REG = TEMP_CFG_REG | (adcBit<<7)

        #print (bin(TEMP_CFG_REG)) # for testing

        self.single_access_write(0x1F, TEMP_CFG_REG)

        return

    def enable_temperature(self):
        """enable_temperature, function to enable the on board temperature
        sensor. This sets bits 6&7 of TEMP_CFG_REG (0x1F)"""

        self.single_access_write(0x1F, 0xC0) # enable adc's and enable temp sensor

        return

    def interrupt_high_low(self, level='high'):
        """interrupt_high_low, function to set the interrupt ins to either
        active high or active low"""

        CTRL_REG6 = self.single_access_read(0x25)

        if level == 'low':
            highlowBit = 0b1
        else:
            highlowBit = 0b0

        CTRL_REG6 = CTRL_REG6 & 0b11111101
        CTRL_REG6 = CTRL_REG6 | (highlowBit<<1)

        #print (bin(CTRL_REG6)) # for testing

        self.single_access_write(0x25, CTRL_REG6)

        return

    def get_aux_status(self, show=False):
        """get_aux_status, function to return the contents of the
        aux status register (0x07)"""
        
        auxStatus = self.single_access_read(0x07)

        if show == True:
            print('Aux Status (0x07) '+str(bin(auxStatus)))

        return auxStatus

    def get_clickInt_status(self, show=False):
        """get_clickInt_status, function to return the contents of the
        click interrupt status register (0x39)"""
        
        clickInterruptStatus = self.single_access_read(0x39)

        if show == True:
            print('Click Interrupt Status (0x39) '+str(bin(clickInterruptStatus)))

        return clickInterruptStatus

    def get_fifo_status(self, show=False):
        """get_fifo_status, function to return the contents of the
        fifo register (0x2F)"""
        
        fifoStatus = self.single_access_read(0x2F)

        if show == True:
            print('FIFO Status (0x2F) '+str(bin(fifoStatus)))

        return fifoStatus
      

    def get_int1_status(self, show=False):
        """get_int1_status, function to return the contents of the
        interrupt1 status register (0x31)"""
        
        interrupt1Status = self.single_access_read(0x31)

        if show == True:
            print('Interrupt Status (0x31) '+str(bin(interrupt1Status)))

        return interrupt1Status

    def get_status(self, show=False):
        """get_status, function to return the contents of the
        status register (0x27)"""
        
        status = self.single_access_read(0x27)

        if show == True:
            print('Status (0x27) '+str(bin(status)))

        return status

    def get_temperature(self):
        """get_temperature, function to read the accelerometer's onboard
        temperature sensor""" 
        
        tempH = self.single_access_read(0x0D)
        tempL = self.single_access_read(0x0C)

        tempTotal = self.twos_complement_conversion(tempH, tempL)
        tempTotal = tempTotal + self.temperatureOffset

        return tempTotal

    def latch_interrupt(self, latch='on'):
        """latch_interrupt, function to turn the latch feature on interrupt1
        on or off"""

        CTRL_REG5 = self.single_access_read(0x24)

        if latch == 'off':
            latchBit = 0b0
        else:
            latchBit = 0b1

        CTRL_REG5 = CTRL_REG5 & 0b11110111
        CTRL_REG5 = CTRL_REG5 | (latchBit<<3)

        #print (bin(CTRL_REG5)) # for testing

        self.single_access_write(0x24, CTRL_REG5)

        return

    def set_adcOn(self, adcOn='off'):
        """set_adcOn, function to enable/disable the aux 10 bit adc
        converter feature.  This sets bit 7 of TEMP_CFG_REG (0x1F)"""

        TEMP_CFG_REG = self.single_access_read(0x1F)

        adcBit = 0b0  # default value

        if adcOn == 'on':
            adcBit = 0b1

        TEMP_CFG_REG = TEMP_CFG_REG & 0b01111111
        TEMP_CFG_REG = TEMP_CFG_REG | (adcBit<<7)

        #print (bin(TEMP_CFG_REG)) # for testing

        self.single_access_write(0x1F, TEMP_CFG_REG)

        return

    def set_BDU(self, bdu='off'):
        """set_BDU, function to enable/disable the block data update
        feature.  This sets bit 7 of CTRL_REG4 (0x23)"""

        CTRL_REG4 = self.single_access_read(0x23)

        bduBit = 0b0  # default value

        if bdu == 'on':
            bduBit = 0b1

        CTRL_REG4 = CTRL_REG4 & 0b01111111
        CTRL_REG4 = CTRL_REG4 | (bduBit<<7)

        #print (bin(CTRL_REG4)) # for testing

        self.single_access_write(0x23, CTRL_REG4)

        return

    def set_click_config(self, zd=0, zs=1, yd=0, ys=0, xd=0, xs=0):
        """set_click_config, function to set the CLICK_CFG regisiter
        (0x38) options"""

        CLICK_CFG = ((zd<<5) + (zs<<4) +(yd<<3) + (ys<<2) + (xd<<1)
                     + xs)

        #print(hex(CLICK_CFG),bin(CLICK_CFG))  # for testing

        self.single_access_write(0x38, CLICK_CFG)

        return

    def set_click_threshold(self, threshold):
        """set_click_threshold, function to set the click threshold (mg).
        This sets CLICK_THS (0x3A)"""

        threshold = abs(threshold)
        thresholdBits = 0b0      

        if self.scale == 2:
            scaleOffset = 4
        elif self.scale == 4:
            scaleOffset = 5
        elif self.scale == 8:
            scaleOffset = 6
        else: # self.scale == 16
            scaleOffset = 7

        for i in range (6,-1,-1):           

            if threshold >= 2**(i+scaleOffset):
                thresholdBits = thresholdBits | (1<<i)
                threshold = threshold - 2**(i+scaleOffset)

        #print(hex(thresholdBits),bin(thresholdBits)) # for testing

        self.single_access_write(0x3A, thresholdBits)

        return

    def set_click_timelimit(self, duration):
        """set_click_timelimit, function to set the click time limit
        duration (ms). This sets TIME_LIMIT (0x3B)"""

        duration = abs(duration)

        if duration > (float(127000)/float(self.odr)):
            durationBits = 0b01111111

        else:
            durationBits = int((float(duration) / float(1000)) * self.odr)
            durationBits = durationBits & 0b01111111

        #print(bin(durationBits))  # for testing

        self.single_access_write(0x3B, durationBits)

        return

    def set_click_timelatency(self, duration):
        """set_click_timelatency, function to set the click time latency
        duration (ms). This sets TIME_LATENCY (0x3C)"""

        duration = abs(duration)

        if duration > (float(255000)/float(self.odr)):
            durationBits = 0b01111111

        else:
            durationBits = int((float(duration) / float(1000)) * self.odr)
            durationBits = durationBits & 0b01111111

        #print(bin(durationBits))  # for testing

        self.single_access_write(0x3C, durationBits)

        return

    def set_click_timewindow(self, duration):
        """set_click_timewindow, function to set the click time window
        duration (ms). This sets TIME_WINDOW (0x3D)"""

        duration = abs(duration)

        if duration > (float(255000)/float(self.odr)):
            durationBits = 0b01111111

        else:
            durationBits = int((float(duration) / float(1000)) * self.odr)
            durationBits = durationBits & 0b01111111

        #print(bin(durationBits))  # for testing

        self.single_access_write(0x3D, durationBits)

        return

    def set_int1_config(self, aoi=1, d6=0, zh=0, zl=0, yh=0, yl=0, xh=0, xl=0):
        """set_int1_config, function to set the INT1_CFG regisiter (0x30) options"""

        INT1_CFG = ((aoi<<7) + (d6<<6) + (zh<<5) + (zl<<4) +(yh<<3) +
                (yl<<2) + (xh<<1) + xl)

        #print(hex(INT1_CFG),bin(INT1_CFG))  # for testing

        self.single_access_write(0x30, INT1_CFG)

        return

    def set_int1_duration(self, duration):
        """set_int1_duration, function to set the minimum interrupt 1 duration (ms).
        This sets INT1_DURATION(0x33)"""

        duration = abs(duration)

        if duration > (float(127000)/float(self.odr)):
            durationBits = 0b01111111

        else:
            durationBits = int((float(duration) / float(1000)) * self.odr)
            durationBits = durationBits & 0b01111111

        #print(bin(durationBits))  # for testing

        self.single_access_write(0x33, durationBits)

        return

        

    def set_int1_pin(self, click=0,aoi1=0, aoi2=0, drdy1=0, drdy2=0, wtm=0, overrun=0):
        """set_int1, function to which interrupt signals get pushed to
        the int1 pin. This sets CTRL_REG3 (0x22)"""

        CTRL_REG3 = ((click<<7) + (aoi1<<6) + (aoi2<<5) + (drdy1<<4) +(drdy2<<3) +
                (wtm<<2) + (overrun<<1))

        #print (bin(CTRL_REG3)) # for testing

        self.single_access_write(0x22, CTRL_REG3)

        return
    
    def set_int1_threshold(self, threshold):
        """set_int1_threshold, function to set the interrupt1 threshold (mg).
        This sets INT1_THS (0x32)"""

        threshold = abs(threshold)
        thresholdBits = 0b0      

        if self.scale == 2:
            scaleOffset = 4
        elif self.scale == 4:
            scaleOffset = 5
        elif self.scale == 8:
            scaleOffset = 6
        else: # self.scale == 16
            scaleOffset = 7

        for i in range (6,-1,-1):

            if threshold >= 2**(i+scaleOffset):
                thresholdBits = thresholdBits | (1<<i)
                threshold = threshold - 2**(i+scaleOffset)

        #print(hex(thresholdBits),bin(thresholdBits)) # for testing

        self.single_access_write(0x32, thresholdBits)

        return
        
       

    def set_ODR(self, odr=50, powerMode='normal'):
        """set_ODR, function to set the output data rate (ODR) and the power
        mode (normal, low, or off). This sets bits 3-7 of CTRL_REG1 (0x20)"""

        CTRL_REG1 = self.single_access_read(0x20)

        odrBits = 0b0100  # default value 50Hz
        self.odr = 50     # default value 50Hz
        lowPowerBit = 0b0 # default value 'normal' power mode        

        odrOptions = [(1,0b0001),(10,0b0010),(25,0b0011),(50,0b0100),
                      (100,0b0101),(200,0b0110),(400,0b0111),(1600,0b1000),
                      (1250,0b1001),(5000,0b1001)]

        for dataRate in odrOptions:
            if dataRate[0] == odr:
                odrBits = dataRate[1]
                self.odr = dataRate[0]

        if powerMode == 'off':
            odrBits = 0b0000

        elif powerMode == 'low':
            lowPowerBit = 0b1

        CTRL_REG1 = CTRL_REG1 & 0b00000111
        CTRL_REG1 = CTRL_REG1 | ((odrBits<<4) + (lowPowerBit<<3))

        #print (bin(CTRL_REG1)) # for testing

        self.single_access_write(0x20, CTRL_REG1)

        return

    def set_scale(self, scale=2):
        """set_scale, function to set the scale used by the
        accelerometer; +-2g, 4g, 8g, 16g"""

        CTRL_REG4 = self.single_access_read(0x23)

        scaleBits = 0b00  # default value
        self.scale = 2

        if scale == 4:
            scaleBits = 0b01
            self.scale = 4
        elif scale == 8:
            scaleBits = 0b10
            self.scale = 8
        elif scale == 16:
            scaleBits = 0b11
            self.scale = 16

        CTRL_REG4 = CTRL_REG4 & 0b11001111
        CTRL_REG4 = CTRL_REG4 | (scaleBits<<4)

        #print (bin(CTRL_REG4)) # for testing

        self.single_access_write(0x23, CTRL_REG4)

        return

    def x_axis_reading(self):
        """x_axis_reading, function to read the x axis accelerometer value"""

        # output in 2s complement
        xH = self.single_access_read(0x29)
        xL = self.single_access_read(0x28)

        xTotal = self.twos_complement_conversion(xH, xL)

        #print (bin(xH),bin(xL),bin(xTotal), xTotal)
        
        return xTotal

    def y_axis_reading(self):
        """y_axis_reading, function to read the y axis accelerometer value"""

        # output in 2s complement
        yH = self.single_access_read(0x2B)
        yL = self.single_access_read(0x2A)

        yTotal = self.twos_complement_conversion(yH, yL)

        #print (bin(yH),bin(yL),bin(yTotal), yTotal)
        
        return yTotal

    def z_axis_reading(self):
        """z_axis_reading, function to read the z axis accelerometer value"""

        # output in 2s complement
        zH = self.single_access_read(0x2D)
        zL = self.single_access_read(0x2C)

        zTotal = self.twos_complement_conversion(zH, zL)

        #print (bin(zH),bin(zL),bin(zTotal), zTotal)
        
        return zTotal



    # need a clean up function
    # do threshold, duration etc functions even if just simple single_access_write based
    # add adc enable/disable functions


if __name__ == "__main__":


    accel = Accelerometer('i2c',i2cAddress = 0x19)
    accel.set_ODR(odr=50, powerMode='normal')
    accel.axis_enable(x='on',y='on',z='on')
    accel.interrupt_high_low('high')
    accel.latch_interrupt('on')
    accel.set_BDU('on')
    accel.set_scale()
    
    
    
    while True:
        print('1. Raw X,Y & Z Data Output')
        print('2. Inertial Threshold Wake-up')
        print('3. 6D Positioning')
        print('4. 6D Movement')
        print('5. Single Click')
        print('6. Get Temperature')
        print('9. Quit')
        exampleType = input('Pick example set up type: ')

        #----------  Raw X,Y, Z data output -----------------

        if exampleType == 1:

            print('\nPress Ctrl-C to stop')
            print('Starting Raw X,Y, & Z data output')

            try:
                while True:                  
                    x = accel.x_axis_reading()   
                    y = accel.y_axis_reading()
                    z = accel.z_axis_reading()                    
                    print ('x: '+str(x)+' y: '+str(y)+' z: '+str(z)) 
                    time.sleep(.25)
            except:
                print('Stopping Raw X,Y, & Z data output \n')

        #---------- Inertial Threshold Wake-up --------------
        # AOI1 interrupt output to pin INT1

        elif exampleType == 2:
            #AOI1 is the interrupt required for inertial/free fall wake up
            accel.set_int1_pin(click=0,aoi1=1, aoi2=0, drdy1=0, drdy2=0, wtm=0, overrun=0) # turn on AOI1 interrupt
            accel.set_int1_threshold(256)   # set INT1_THS to 256mg            
            accel.set_int1_duration(0)      # set INT1_DURATION  to 0ms
            accel.set_int1_config(aoi=0, d6=0, zh=0, zl=0, yh=1, yl=0, xh=1, xl=0) # on INT1_CFG enable XH and YH OR interrupt generation
            
            print('\nPress Ctrl-C to stop')
            print('Starting Inertial Threshold Wake-up (XH & YH)')

            try:
                while True:
                    x = accel.x_axis_reading()   
                    y = accel.y_axis_reading()
                    interrupt1 = accel.get_int1_status()
                    print ('x: '+str(x)+' y: '+str(y)+ ' Interrupt Status  '
                           +str(bin(interrupt1)))                   
                    time.sleep(.25)
            except:
                print('Stopping Inertial Threshold Wake-up \n')
                accel.set_int1_pin(click=0,aoi1=0, aoi2=0, drdy1=0, drdy2=0, wtm=0, overrun=0) # turn off AOI1 interrupt
                accel.set_int1_config(0,0,0,0,0,0,0,0) # on INT1_CFG disable XH and YH OR interrupt generation

        #---------- 6D Positioning ---------------------------
        # AOI1 interrupt output to pin INT1

        elif exampleType == 3:
            #AOI1 is the interrupt required for 6D positioning

            accel.set_int1_pin(click=0,aoi1=1, aoi2=0, drdy1=0, drdy2=0, wtm=0, overrun=0) # turn on AOI1 interrupt
            accel.set_int1_threshold(256)   # set INT1_THS to 256mg            
            accel.set_int1_duration(0)      # set INT1_DURATION  to 0ms
            accel.set_int1_config(aoi=1, d6=1, zh=1, zl=1, yh=1, yl=1, xh=1, xl=1)  # on INT1_CFG enable 6D positioning, X, Y & Z (H & L)

            print('\nPress Ctrl-C to stop')
            print('Starting 6D Positioning')

            try:
                while True:
                    x = accel.x_axis_reading()   
                    y = accel.y_axis_reading()
                    z = accel.z_axis_reading()
                    interrupt1 = accel.get_int1_status()
                    print ('x: '+str(x)+' y: '+str(y)+' z: '+str(z)+ ' Interrupt Status  '
                           +str(bin(interrupt1)))                    
                    if interrupt1 == 0x44:
                        print('YL interrupt') # Position (a)
                    elif interrupt1 == 0x42:
                        print('XH interrupt') # Position (b)
                    elif interrupt1 == 0x41:
                        print('XL interrupt') # Position (c)
                    elif interrupt1 == 0x48:
                        print('YH interrupt') # Position (d)
                    elif interrupt1 == 0x60:
                        print('ZH interrupt') # Position (e)
                    elif interrupt1 == 0x50:
                        print('ZL interrupt') # Position (f)
                    time.sleep(.25)
                    
            except:
                print('Stopping 6D Positioning')
                accel.set_int1_pin(click=0,aoi1=0, aoi2=0, drdy1=0, drdy2=0, wtm=0, overrun=0) # turn off AOI1 interrupt
                accel.set_int1_config(0,0,0,0,0,0,0,0) # on INT1_CFG disable 6D positioning, X, Y & Z (H & L)

        #---------- 6D Movement ------------------------------
        # AOI1 interrupt output to pin INT1

        elif exampleType == 4:
            #AOI1 is the interrupt required for 6D movement

            accel.set_int1_pin(click=0,aoi1=1, aoi2=0, drdy1=0, drdy2=0, wtm=0, overrun=0) # turn on AOI1 interrupt
            accel.set_int1_threshold(256)   # set INT1_THS to 256mg            
            accel.set_int1_duration(0)      # set INT1_DURATION  to 0ms
            accel.set_int1_config(aoi=0, d6=1, zh=1, zl=1, yh=1, yl=1, xh=1, xl=1)  # on INT1_CFG enable 6D movement, X, Y & Z (H & L)

            print('\nPress Ctrl-C to stop')
            print('Starting 6D Movement')

            try:
                while True:
                    x = accel.x_axis_reading()   
                    y = accel.y_axis_reading()
                    z = accel.z_axis_reading()
                    interrupt1 = accel.get_int1_status()
                    print ('x: '+str(x)+' y: '+str(y)+' z: '+str(z)+ ' Interrupt Status  '
                           +str(bin(interrupt1)))                    
                    if interrupt1 == 0x44:
                        print('YL interrupt') # Position (a)
                    elif interrupt1 == 0x42:
                        print('XH interrupt') # Position (b)
                    elif interrupt1 == 0x41:
                        print('XL interrupt') # Position (c)
                    elif interrupt1 == 0x48:
                        print('YH interrupt') # Position (d)
                    elif interrupt1 == 0x60:
                        print('ZH interrupt') # Position (e)
                    elif interrupt1 == 0x50:
                        print('ZL interrupt') # Position (f)
                    time.sleep(.25)
                    
            except:
                print('Stopping 6D Movement')
                accel.set_int1_pin(click=0,aoi1=0, aoi2=0, drdy1=0, drdy2=0, wtm=0, overrun=0) # turn off AOI1 interrupt
                accel.set_int1_config(0,0,0,0,0,0,0,0) # on INT1_CFG disable 6D Movement, X, Y & Z (H & L)

        #--------- Single Click (Z) --------------------------
        # CLICK interrupt output to pin INT1

        elif exampleType == 5:
            # CLICK is the interrupt required for single click
            # tap by the accelerometer to see the interrupt status change
            
            accel.set_int1_pin(click=1,aoi1=0, aoi2=0, drdy1=0, drdy2=0, wtm=0, overrun=0) # turn on CLICK interrupt
            accel.set_click_config(zd=0, zs=1, yd=0, ys=0, xd=0, xs=0) # enable Z single click on CLICK_CFG
            accel.set_click_threshold(1088)       # set CLICK_THS to 1088 mg
            accel.set_click_timelimit(120)        # set TIME_LIMIT to 120ms
            accel.set_click_timelatency(320)      # set TIME_LATENCY to 320ms            

            print('\nPress Ctrl-C to stop')
            print('Starting Single Click')

            try:
                while True:            
                    z = accel.z_axis_reading()
                    interrupt1 = accel.get_clickInt_status()
                    print ('z: '+str(z)+ ' Click Interrupt Status  '+str(bin(interrupt1)))
                    time.sleep(.25)
                    
            except:
                print('Stopping Single Click')
                accel.set_int1_pin(click=0,aoi1=0, aoi2=0, drdy1=0, drdy2=0, wtm=0, overrun=0) # turn off CLICK interrupt
                accel.set_click_config(zd=0, zs=0, yd=0, ys=0, xd=0, xs=0) # disable Z single click on CLICK_CFG

        #--------- Get temperature ---------------------------

        elif exampleType == 6:
           
            accel.enable_temperature()

            print('\nPress Ctrl-C to stop')
            print('Getting Temperature')

            try:
                while True:
                    print(str(accel.get_temperature())+' C')
                    time.sleep(0.5)

            except:
                print('Stopping Temperature')
                accel.disable_temperature('off')        
                   

        elif exampleType == 9:
            break

    #---- exiting section-----------        
    
    accel.set_ODR(odr=50, powerMode='off') # put the accel in power down mode

    if accel.mode == 'spi':    
        accel.spi.close()
    else:  #i2C    
        accel.bus.close()

    
    
