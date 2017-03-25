# LIS3DH-Python-Module
Python 2.x module to use with the LIS3DH accelerometer. Testing done on a adafruit LIS3DH breakout board and a Raspberry Pi3
This supports both SPI and i2C. SPI requires py-spidev and python-dev modules. i2C requires smbus

I will add a nicer module in the near future.  For now I've included a practice file and not alot of explanation.

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

