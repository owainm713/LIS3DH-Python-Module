# LIS3DH-Python-Module
Python 2.x module to use with the LIS3DH accelerometer. Testing done on a adafruit LIS3DH breakout board and a Raspberry Pi3.  Other LIS3DH breakout boards,  i.e. sparkfun should work as well, just be careful on your voltage levels on the various pins.

This supports both SPI and i2C. SPI requires py-spidev and python-dev modules. i2C requires smbus

Also included is an example file that when run has some example accelerometer uses. I connected an LED up to INT1 (with appropriate current limiting resistor) to demonstrate the int1 pin use.

SPI connections to the LIS3DH board from the Pi are as follows:
- Pi 3.3V to LIS3DH Vin
- LIS3DH 3Vo - not connected
- Pi Gnd to LIS3DH Gnd
- Pi SCLK to LIS3DH SCL
- Pi MOSI to LIS3DH SDA
- Pi MISO to LIS3DH SDO
- Pi CE0 or CE1 to LIS3DH CS
- LIS3DH INT - not connected

i2c connections to the LIS3DH board from the Pi are as follows:
- Pi 3.3V to LIS3DH Vin
- LIS3DH 3Vo - not connected
- Pi Gnd to LIS3DH Gnd
- Pi SCL to LIS3DH SCL
- Pi SDA to LIS3DH SDA
- Pi 3.3V to LIS3DH SDO
- Pi 3.3V to LIS3DH CS
- LIS3DH INT - not connected

i2C address of 0x19

Together the LIS3DH data sheet and LIS3DH app note are useful for figuring out how to config the accelerometer for the various applications.  I recommend using them.
Both can be downloaded from either the st, adafruit or sparkfun websites.

Current functions include

- adc_reading(self, channel)
- axis_enable(x='on',y='on',z='on')
- disable_temperature(adcOn='on')
- enable_temperature()
- interrupt_high_low(level='high')
- get_aux_status(show=False)
- get_clickInt_status(show=False)
- get_fifo_status(show=False)
- get_int1_status(show=False)
- get_status(show=False)
- get_temperature()
- latch_interrupt(latch='on')
- set_4D(enable='on')
- set_adcOn(adcOn='off')
- set_BDU(bdu='off')
- set_click_config(zd=0, zs=1, yd=0, ys=0, xd=0, xs=0)
- set_click_threshold(threshold)
- set_click_timelimit(duration)
- set_click_timelatency(duration)
- set_click_timewindow(duration)
- set_fifo_mode(mode='bypass')
- set_fifo_threshold(threshold)
- set_highpass_filter(mode, freq, FDS, hpClick, hpIS2, hpIS1)
- set_int1_config(aoi=1, d6=0, zh=0, zl=0, yh=0, yl=0, xh=0, xl=0)
- set_int1_duration(duration)
- set_int1_pin(click=0,aoi1=0, aoi2=0, drdy1=0, drdy2=0, wtm=0, overrun=0)
- set_int1_threshold(threshold)
- set_ODR(odr=50, powerMode='normal')
- set_resolution(res='low')
- set_scale(scale=2)
- set_temperature_offset(offset)
- x_axis_reading()
- y_axis_reading()
- z_axis_reading()

Updates

Dec 15, 2018
Made correction to max time limit in set_click_timelatency and set_click_timewindow functions

May 22 2018
Added LIS3DHDataReadyInterruptExample to demonstrate the use of the data ready interrupt (drdy1) of the sensor.
This example requires the use of the RPi.GPIO module. Lower ODR rates (<200) work better for this.
 