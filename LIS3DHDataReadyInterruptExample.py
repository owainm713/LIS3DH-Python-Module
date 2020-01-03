#!/usr/bin/python3
"""LIS3DHDAtaReadyInterruptExample, file containing example for using the LIS3DH accelerometer
data ready interrupt

created May 22, 2018 OM
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

""" I tried using GPIO add event/remove event with callback but the pi didn't
like that above ODR of 50 and it used a lot of CPU% (30-50%) using SPI

With SPI using GPIO wait for edge the # of readings for an ODR of 200 or less are
almost exaclty the ODR, the # of readings for an ODR above 200 becomes a fraction of
the ODR rate depending on what else the pi is up to I suppose.

With i2C using GPIO wait for edge the # of readings for an ODR of 100 or less are
almost exactly the ODR, at an ODR of 200 the # of readings are less than the ODR
and with an ODR larger than 200 almost no readings were obtained"""

import LIS3DH
import time, spidev,sys
import RPi.GPIO as GPIO

#accel = LIS3DH.Accelerometer('i2c',i2cAddress = 0x19)   # i2c connection alternative
accel = LIS3DH.Accelerometer('spi', spiPort = 0, spiCS = 1) # spi connection alternative
accel.set_ODR(odr=10, powerMode='normal')
accel.axis_enable(x='on',y='on', z='on')
accel.interrupt_high_low('high')
accel.latch_interrupt('on')
accel.set_BDU('on')
accel.set_scale()

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)  # uses numbering outside circles

numSeconds = 5
odrRate = 10

try:
    intPin = input('Which  Pi pin is the interrupt connected to? ')
    GPIO.setup(intPin,GPIO.IN)   # set interrupt pin to input
except:
    print("Something didn't work with interrupt pin setup")
    sys.exit()
        
while True:
    print('1. Set ODR (output data rate)')
    print('2. Set # of seconds to run examples ')
    print('3. Run example')    
    print('9. Quit')
    option = input('Pick option: ')    

    if option == 1:

        odrRate = input('Choose ODR rate (1,10,50,100,200,400,1250)(hz): ')
        accel.set_ODR(odr=odrRate, powerMode='normal')

    elif option == 2:

        numSeconds = input('Enter # of seconds(s): ')

    elif option == 3:

        print('\nPress Ctrl-C to stop')
        print('Starting run...')
        print('Example is set up to print out x values above abs(50)\n')
       
        passCount = 0
        failCount = 0
        xList = []
        yList = []
        zList = []
        readingCount = 0
        readingCountList = []

        # to implement in a program, below should probably be placed
        # in a thread

        # turn on data ready interrupt    
        accel.set_int1_pin(click=0,aoi1=0, aoi2=0, drdy1=1, drdy2=0, wtm=0, overrun=0)

        try:
            loopStart = time.time()
            startTime = time.time()
            while (time.time()-loopStart) < numSeconds:
                GPIO.wait_for_edge(intPin,GPIO.RISING, timeout=500)
                x = accel.x_axis_reading()   
                y = accel.y_axis_reading()
                z = accel.z_axis_reading()

                # this is where you would add your own
                # code to do whatever it is you are trying
                # to do

                xList.append(accel.x_axis_reading())                
                yList.append(accel.y_axis_reading())                
                zList.append(accel.z_axis_reading())
                readingCount +=1

                if abs(x) >50:
                    print(x,y,z)
                    
                if (time.time()- startTime) > 1:            
                    readingCountList.append(readingCount)            
                    startTime = time.time()
                    readingCount = 0

        except:
            pass

        # turn off data ready interrupt    
        accel.set_int1_pin(click=0,aoi1=0, aoi2=0, drdy1=0, drdy2=0, wtm=0, overrun=0)

        readingAverage = 0

        for item in readingCountList:
            if item < (odrRate*0.8):
                failCount+=1
            else:
                passCount+=1
            readingAverage = readingAverage + item

        readingAverage = readingAverage/len(readingCountList)

        xList.sort()
        yList.sort()
        zList.sort()

        print('\nThe ODR rate used: '+str(odrRate))
        print('The average number of readings taken per second: '+
              str(readingAverage))
        print("Number of records: "+str(len(zList)))        

        print("x min: "+str(xList[0])+" x max: "+str(xList[len(xList)-1]))
        print("y min: "+str(yList[0])+" y max: "+str(yList[len(yList)-1]))
        print("z min: "+str(zList[0])+" z max: "+str(zList[len(zList)-1])+'\n')
        

    elif option == 9:
        accel.set_ODR(odr=50, powerMode='off') # put the accel in power down mode
        break

#---- exiting section-----------
    
del(accel)
GPIO.cleanup()
sys.exit()
    
