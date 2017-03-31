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
- Pi CE1 to LIS3DH CS
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

