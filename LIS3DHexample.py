#!/usr/bin/env python3
"""LIS3DHexample, file containing example for using LIS3DH accelerometer
module

created Mar 27, 2017 OM
work in progress - Jan 3, 2020 OM"""

"""
Copyright 2020 Owain Martin

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

import LIS3DH
import time, spidev, sys, smbus

accel = LIS3DH.Accelerometer('i2c',i2cAddress = 0x19)
#accel = LIS3DH.Accelerometer('spi', i2cAddress = 0x0, spiPort = 0, spiCS = 1)  # spi connection alternative
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
    print('6. Double Click')
    print('7. Get Temperature')
    print('9. Quit')
    exampleType = int(input('Pick example set up type: '))

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

    #--------- Double Click (Z) --------------------------
    # CLICK interrupt output to pin INT1

    elif exampleType == 6:
        # CLICK is the interrupt required for single click
        # double tap by the accelerometer to see the interrupt status change
        
        accel.set_int1_pin(click=1,aoi1=0, aoi2=0, drdy1=0, drdy2=0, wtm=0, overrun=0) # turn on CLICK interrupt
        accel.set_click_config(zd=1, zs=0, yd=0, ys=0, xd=0, xs=0) # enable Z double click on CLICK_CFG
        accel.set_click_threshold(1088)       # set CLICK_THS to 1088 mg
        accel.set_click_timelimit(120)        # set TIME_LIMIT to 120ms
        accel.set_click_timelatency(320)      # set TIME_LATENCY to 320ms
        accel.set_click_timewindow(400)       # set TIME_WINDOW to 512ms

        print('\nPress Ctrl-C to stop')
        print('Starting Double Click')

        try:
            while True:            
                z = accel.z_axis_reading()
                interrupt1 = accel.get_clickInt_status()
                print ('z: '+str(z)+ ' Click Interrupt Status  '+str(bin(interrupt1)))
                time.sleep(.25)
                
        except:
            print('Stopping Double Click')
            accel.set_int1_pin(click=0,aoi1=0, aoi2=0, drdy1=0, drdy2=0, wtm=0, overrun=0) # turn off CLICK interrupt
            accel.set_click_config(zd=0, zs=0, yd=0, ys=0, xd=0, xs=0) # disable Z single click on CLICK_CFG


    #--------- Get temperature ---------------------------

    elif exampleType == 7:
       
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
        accel.set_ODR(odr=50, powerMode='off') # put the accel in power down mode
        break

#---- exiting section-----------
    
del(accel)


