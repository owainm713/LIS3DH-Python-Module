#!/usr/bin/env python
"""LIS3DHpractice, program to practice communication with a
LIS3DH accelerometer

created Mar 6, 2017 OM
work in progress - Mar 24, 2017 OM"""

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

mode = 'i2c'

if mode == 'spi':
    spi=spidev.SpiDev()
    spi.open(0,1)  # open spi port 0, device (CS) 1

else:  #i2C
    bus = smbus.SMBus(1)
    addr = 0x19

def single_access_read(reg=0x00):
    """single_access_read, function to read a single data register
    of the LIS3DH"""

    rwBit = 0b1  # read/write bit set to read
    msBit = 0b1  # multiple read/write address increment select bit set to auto increment

    if mode == 'spi':
        dataTransfer=spi.xfer2([(rwBit<<7)+(msBit<<6)+reg,0])

        # for testing
        #print(hex(reg), hex(dataTransfer[1]),bin(dataTransfer[1]))
        
        return dataTransfer[1]
    
    else: #i2c
        dataTransfer=bus.read_byte_data(addr,reg)
        return dataTransfer
   

def single_access_write(reg=0x00, regValue=0x0):
    """single_access_write, function to write a single data register
    of the LIS3DH"""

    rwBit = 0b0  # read/write bit set to write
    msBit = 0b1  # multiple read/write address increment select bit set to auto increment

    if mode == 'spi':
        dataTransfer=spi.xfer2([(rwBit<<7)+(msBit<<6)+reg,regValue])
        # for testing
        #print(bin((rwBit<<7)+(msBit<<6)+reg),hex(reg), hex(regValue), hex(dataTransfer[1]))
        
    else: #i2c
        bus.write_byte_data(addr, reg, regValue)    

    return

def twos_complement_conversion(msb, lsb):
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

def x_axis_reading():
    """x_axis_reading, function to read the x axis accelerometer value"""

    # output in 2s complement
    xH = single_access_read(0x29)
    xL = single_access_read(0x28)

    xTotal = twos_complement_conversion(xH, xL)

    #print (bin(xH),bin(xL),bin(xTotal), xTotal)
    
    return xTotal

def y_axis_reading():
    """y_axis_reading, function to read the y axis accelerometer value"""

    # output in 2s complement
    yH = single_access_read(0x2B)
    yL = single_access_read(0x2A)

    yTotal = twos_complement_conversion(yH, yL)

    #print (bin(yH),bin(yL),bin(yTotal), yTotal)
    
    return yTotal

def z_axis_reading():
    """z_axis_reading, function to read the z axis accelerometer value"""

    # output in 2s complement
    zH = single_access_read(0x2D)
    zL = single_access_read(0x2C)

    zTotal = twos_complement_conversion(zH, zL)

    #print (bin(zH),bin(zL),bin(zTotal), zTotal)
    
    return zTotal

def enable_temperature():
    """enable_temperature, function to enable the on board temperature
    sensor"""

    single_access_write(0x1F, 0xC0) # enable adc's and enable temp sensor

    return

def disable_temperature():
    """disable_temperature, function to disable the on board temperature
    sensor"""

    single_access_write(0x1F, 0x00) # enable adc's and enable temp sensor

    return

def get_temperature():
    """get_temperature, function to read the accelerometer's onboard
    temperature sensor""" 
    
    tempH = single_access_read(0x0D)
    tempL = single_access_read(0x0C)

    tempTotal = twos_complement_conversion(tempH, tempL)    

    return tempTotal

def set_scale(scale=2):
    """set_scale, function to set the scale used by the
    accelerometer; +-2g, 4g, 8g, 16g"""

    CTRL_REG4 = single_access_read(0x23)

    scaleBits = 0b00  # default value

    if scale == 4:
        scaleBits = 0b01
    elif scale == 8:
        scaleBits = 0b10
    elif scale == 16:
        scaleBits = 0b11

    CTRL_REG4 = CTRL_REG4 & 0b11001111
    CTRL_REG4 = CTRL_REG4 | (scaleBits<<4)

    #print (bin(CTRL_REG4)) # for testing

    single_access_write(0x23, CTRL_REG4)

    return

def latch_interrupt(latch='on'):
    """latch_interrupt, function to turn the latch feature on interrupt1
    on or off"""

    CTRL_REG5 = single_access_read(0x24)

    if latch == 'off':
        latchBit = 0b0
    else:
        latchBit = 0b1

    CTRL_REG5 = CTRL_REG5 & 0b11110111
    CTRL_REG5 = CTRL_REG5 | (latchBit<<3)

    #print (bin(CTRL_REG5)) # for testing

    single_access_write(0x24, CTRL_REG5)

    return

def interrupt_high_low(level='high'):
    """interrupt_high_low, function to set the interrupt ins to either
    active high or active low"""

    CTRL_REG6 = single_access_read(0x25)

    if level == 'low':
        highlowBit = 0b1
    else:
        highlowBit = 0b0

    CTRL_REG6 = CTRL_REG6 & 0b11111101
    CTRL_REG6 = CTRL_REG6 | (highlowBit<<1)

    #print (bin(CTRL_REG6)) # for testing

    single_access_write(0x25, CTRL_REG6)

    return

  

def show_interrupt_status():
    """show_interrupt_status, function to show the contents of the
    various interrupt status and status registers"""

    #auxStatus = single_access_read(0x07)
    #status = single_access_read(0x27)
    #fifoStatus = single_access_read(0x2F)
    #interrupt1Status = single_access_read(0x31)
    interrupt1Status = 0
    clickStatus = single_access_read(0x39)

    #print('Status '+str(bin(status))+' Aux Status '+str(bin(auxStatus))
    #      +' Fifo Status '+str(bin(fifoStatus)))
    print('Interrupt Status '+str(bin(interrupt1Status))+' Click Status '
          +str(bin(clickStatus)))

    return interrupt1Status
    

#------- testing area -----------

mode = 5

single_access_write(0x20,0x47)  # take the accel out of power down mode
time.sleep(1)

interrupt_high_low('high')
latch_interrupt('on')
enable_temperature()            # enable adc's and enble temp sensor
single_access_write(0x23, 0x80) # enable BDU (block data update)
set_scale()

#----- testing area 1 -----

if mode == 1:

    for reg in range(31,62):  
        regValue = single_access_read(reg)
        print(hex(reg), hex(regValue), bin(regValue))    

    for i in range(0,31):
              
        x = x_axis_reading()   
        y = y_axis_reading()
        z = z_axis_reading()
        temp = get_temperature()
        print ('x: '+str(x)+' y: '+str(y)+' z: '+str(z)+' temp:'+str(temp))    

        time.sleep(.5)

    show_interrupt_status()

#---- inertial wake up testing area ------

# inertial wake up on XH and YH using OR combination
# inertial wake up on XH and YH using AND combination
# free fall wake up on XL and YL using AND combination

# interrupt is generated when the X,Y or Z value goes above the
# threshold value with XH, YH and ZH enabled in OR combination

# interrupt is generated when the X,Y and Z values all goe above the
# threshold value with XH, YH and ZH enabled in AND combination

# XL, YL and ZL combos similiar to above only using X, Y and Z values
# below the threshold

elif mode == 2:

    #AOI1 is the interrupt required for inertial/free fall wake up

    single_access_write(0x22, 0xE6) # turn on click, AOI1, AOI2, WTM and Overrun interrupts
    single_access_write(0x32, 0x10) # set INT1_THS to 250mg
    #single_access_write(0x32, 0x18) # set INT1_THS to 384mg
    single_access_write(0x33, 0x00) # set INT1_DURATION  to 0
    #single_access_write(0x33, 0x18) # set INT1_DURATION  to 480ms??    
    single_access_write(0x30, 0x0A) # on INT1_CFG enable XH and YH OR interrupt generation
    #single_access_write(0x30, 0x8A) # on INT1_CFG enable XH and YH AND interrupt generation
    #single_access_write(0x30, 0x85) # on INT1_CFG enable XL and YL AND interrupt generation

    try:
        while True:
            x = x_axis_reading()   
            y = y_axis_reading()            
            print ('x: '+str(x)+' y: '+str(y))            
            show_interrupt_status()
            time.sleep(.5)
    except:
        pass
   

#---- 6D positioning testing area ----------

elif mode == 3:

    #AOI1 is the interrupt required for 6D positioning

    single_access_write(0x22, 0xE6) # turn on click, AOI1, AOI2, WTM and Overrun interrupts
    single_access_write(0x32, 0x10) # set INT1_THS to 250mg    
    single_access_write(0x33, 0x00) # set INT1_DURATION  to 0
    single_access_write(0x30, 0xFF) # on INT1_CFG enable 6D positioning, X, Y & Z (H & L)
    #single_access_write(0x30, 0xEA) # on INT1_CFG enable 6D positioning, X, Y & Z (H only)

    try:
        while True:
            x = x_axis_reading()   
            y = y_axis_reading()
            z = z_axis_reading()
            print ('x: '+str(x)+' y: '+str(y)+' z: '+str(z))            
            interruptStatus = show_interrupt_status()
            if interruptStatus == 0x44:
                print('YL interrupt')
            elif interruptStatus == 0x42:
                print('XH interrupt')
            elif interruptStatus == 0x41:
                print('XL interrupt')
            elif interruptStatus == 0x48:
                print('YH interrupt')
            elif interruptStatus == 0x60:
                print('ZH interrupt')
            elif interruptStatus == 0x50:
                print('ZL interrupt')
            time.sleep(.5)
            
    except:
        pass

    # does threshold affect the 6D positioning feature - yes
    # try disabling some of YL, ZL etc in INT1_CFG - no interrupt generated on
    # the positions disabled - INT1_SRC will still show that position as detected
    # (i.e. YL) but IA will stay low

#----- 6D motion testing area ---------------

elif mode == 4:

    #AOI1 is the interrupt required for 6D movement

    single_access_write(0x22, 0x40) # turn on AOI1 interrupt
    single_access_write(0x32, 0x10) # set INT1_THS to 250mg    
    single_access_write(0x33, 0x00) # set INT1_DURATION  to 0
    single_access_write(0x30, 0x7F) # on INT1_CFG enable 6D movement, X, Y & Z (H & L)

    try:
        while True:
            x = x_axis_reading()   
            y = y_axis_reading()
            z = z_axis_reading()
            print ('x: '+str(x)+' y: '+str(y)+' z: '+str(z))            
            interruptStatus = show_interrupt_status()
            if interruptStatus == 0x44:
                print('YL interrupt')
            elif interruptStatus == 0x42:
                print('XH interrupt')
            elif interruptStatus == 0x41:
                print('XL interrupt')
            elif interruptStatus == 0x48:
                print('YH interrupt')
            elif interruptStatus == 0x60:
                print('ZH interrupt')
            elif interruptStatus == 0x50:
                print('ZL interrupt')
            time.sleep(.5)
    except:
        pass

#---- single click testing area ------

elif mode == 5:

    # CLICK is the interrupt required for click    

    single_access_write(0x22, 0x80) # turn on CLICK interrupt
    single_access_write(0x38, 0x10) # enable Z single click on CLICK_CFG
    single_access_write(0x3A, 0x44) # set CLICK_THS to 1152 mg ?
    #single_access_write(0x3A, 0x43) # set CLICK_THS to 1088 mg ?
    single_access_write(0x3B, 0x06) # set TIME_LIMIT to 120ms ?
    #single_access_write(0x3B, 0x0C) # set TIME_LIMIT to 240ms ?
    #single_access_write(0x3C, 0x03) # set TIME_LATENCY to 60ms ?
    single_access_write(0x3C, 0x10) # set TIME_LATENCY to 320ms ?

    try:
        while True:            
            z = z_axis_reading()
            print ('z: '+str(z))
            show_interrupt_status()
            time.sleep(.25)
            
    except:
        pass

    single_access_write(0x22, 0x00) # turn off CLICK interrupt
    single_access_write(0x38, 0x00) # disable Z single click on CLICK_CFG




#---- exiting section-----------
    
disable_temperature()          # disable adc's and enble temp sensor
single_access_write(0x20,0x07) # put the accel in power down mode

if mode == 'spi':    
    spi.close()
else:  #i2C    
    bus.close()

    
    

