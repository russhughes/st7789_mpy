# The MIT License (MIT)
#
# Copyright (c) 2017 ladyada for adafruit industries
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
"""
`adafruit_focaltouch`
====================================================

CircuitPython driver for common low-cost FocalTech capacitive touch chips.
Currently supports FT6206 & FT6236.

* Author(s): ladyada

* adopted for micropython => franz schaefer (mond)

Implementation Notes
--------------------

**Hardware:**

* Adafruit `2.8" TFT LCD with Cap Touch Breakout Board w/MicroSD Socket
  <http://www.adafruit.com/product/2090>`_ (Product ID: 2090)

* Adafruit `2.8" TFT Touch Shield for Arduino w/Capacitive Touch
  <http://www.adafruit.com/product/1947>`_ (Product ID: 1947)

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the ESP8622 and M0-based boards:
  https://github.com/adafruit/circuitpython/releases
* Adafruit's Bus Device library (when using I2C/SPI):
  https://github.com/adafruit/Adafruit_CircuitPython_BusDevice
"""

# imports

try:
    import struct
except ImportError:
    import ustruct as struct

from machine import SoftI2C
from micropython import const


_FT6206_DEFAULT_I2C_ADDR = 0x38

_FT6XXX_REG_DATA = const(0x00)
_FT6XXX_REG_NUMTOUCHES = const(0x02)
_FT6XXX_REG_THRESHHOLD = const(0x80)
_FT6XXX_REG_POINTRATE = const(0x88)
_FT6XXX_REG_LIBH = const(0xA1)
_FT6XXX_REG_LIBL = const(0xA2)
_FT6XXX_REG_CHIPID = const(0xA3)
_FT6XXX_REG_FIRMVERS = const(0xA6)
_FT6XXX_REG_VENDID = const(0xA8)
_FT6XXX_REG_RELEASE = const(0xAF)


class FocalTouch:
    """
    A driver for the FocalTech capacitive touch sensor.
    """

    _debug = False
    chip = None

    def __init__(self, i2c, address=_FT6206_DEFAULT_I2C_ADDR, debug=False):
        self.bus = i2c
        self.address = address
        self._debug = debug

        chip_data = self._read(_FT6XXX_REG_LIBH, 8)
        lib_ver, chip_id, _, _, firm_id, _, vend_id = struct.unpack(
            ">HBBBBBB", chip_data
        )

        if debug:
            print("Vendor ID %02x" % vend_id)

        self.vend_id=vend_id
        if chip_id == 0x06:
            self.chip = "FT6206"
        elif chip_id == 0x64:
            self.chip = "FT6236"
        elif debug:
            print("Chip Id: %02x" % chip_id)

        if debug:
            print("Library vers %04X" % lib_ver)
            print("Firmware ID %02X" % firm_id)
            print("Point rate %d Hz" % self._read(_FT6XXX_REG_POINTRATE, 1)[0])
            print("Thresh %d" % self._read(_FT6XXX_REG_THRESHHOLD, 1)[0])


    @property
    def touched(self):
        """ Returns the number of touches currently detected """
        return self._read(_FT6XXX_REG_NUMTOUCHES, 1)[0]

    # pylint: disable=unused-variable
    @property
    def touches(self):
        """
        Returns a list of touchpoint dicts, with 'x' and 'y' containing the
        touch coordinates, and 'id' as the touch # for multitouch tracking
        """
        touchpoints = []
        data = self._read(_FT6XXX_REG_DATA, 32)

        for i in range(2):
            point_data = data[i * 6 + 3 : i * 6 + 9]
            if all([i == 0xFF for i in point_data]):
                continue
            # print([hex(i) for i in point_data])
            x, y, weight, misc = struct.unpack(">HHBB", point_data)
            # print(x, y, weight, misc)
            touch_id = y >> 12
            x &= 0xFFF
            y &= 0xFFF
            point = {"x": x, "y": y, "id": touch_id}
            touchpoints.append(point)
        return touchpoints

    def _read(self, reg, length):
        """Returns an array of 'length' bytes from the 'register'"""
        result = bytearray(length)
        self.bus.readfrom_mem_into(self.address, reg, result)
        if self._debug:
            print("\t$%02X => %s" % (reg, [hex(i) for i in result]))
        return result

    def _write(self, reg, values):
        """Writes an array of 'length' bytes to the 'register'"""
        values = [(v & 0xFF) for v in values]
        self.bus.writeto_mem(self.address,reg,bytes(values))
        if self._debug:
            print("\t$%02X <= %s" % (reg, [hex(i) for i in values]))
