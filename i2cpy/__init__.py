"""I2C is a two-wire protocol for communicating between devices. At the
physical level it consists of 2 wires: SCL and SDA, the clock and data lines
respectively.

I2C objects are created attached to a specific bus. They can be initialised
when created, or initialised later on.

This library is designed to support different I2C driver implementations.
It's interface is similar to MicroPython's ``machine.I2C`` as well as CircuitPython's
``board.I2C`` classes.

Example usage:

.. code-block:: python

    from i2cpy import I2C

    i2c = I2C()                      # create I2C peripheral

    i2c.writeto(42, b'123')          # write 3 bytes to peripheral with 7-bit address 42
    i2c.readfrom(42, 4)              # read 4 bytes from peripheral with 7-bit address 42

    i2c.readfrom_mem(42, 8, 3)       # read 3 bytes from memory of peripheral 42,
                                     #   starting at memory address 8 in the peripheral
    i2c.writeto_mem(42, 2, b'\\x10') # write 1 byte to memory of peripheral 42,
                                     #   starting at memory address 2 in the peripheral


"""

from __future__ import annotations

import os
import logging
from importlib import import_module
from typing import List, Optional

try:
    from collections.abc import Buffer
except ImportError:
    from typing_extensions import Buffer

from i2cpy.driver.abc import i2c_addr_byte, to_buffer
from i2cpy.errors import *


__version__ = "0.1.0b1"


log = logging.getLogger(__name__)


class I2C:
    def __init__(
        self,
        id: int = 0,
        *,
        driver: Optional[str] = None,
        freq: int = 400000,
        auto_init: bool = True,
        **kwargs,
    ):
        """Constructor.

        :param id: Device id number, defaults to 0. How this is used depends on
            driver implementation.
        :param freq: I2C bus baudrate, defaults to 400000
        :param driver: I2C driver name. It corresponds to the I2C driver sub
            module name shipped with this library. For example "foo" means module
            "i2cpy.driver.foo".
            If not specified, it looks at environment variable "I2CPY_DRIVER".
            And if that's not defined or empty, it finally falls back to "ch341".
        :param auto_init: Call `init()` on object initialization, defaults to True
        """
        self.index = id
        self.baudrate = freq
        self.driver_name = (driver or os.getenv("I2CPY_DRIVER") or "ch341").lower()
        driver_module_name = "i2cpy.driver.{}".format(self.driver_name)
        try:
            self.driver_module = import_module(driver_module_name)
        except (ModuleNotFoundError, ImportError) as exc:
            raise I2CInvalidDriverError(self.driver_name) from exc

        self.driver = self.driver_module.driver_class()(id, freq=freq, **kwargs)

        if auto_init:
            self.init()

    def init(self):
        """Initialise the I2C bus."""
        self.driver.init()

    def deinit(self):
        """Close the I2C bus."""
        self.driver.deinit()

    def readfrom(self, addr: int | Buffer, nbytes: int, /) -> bytes:
        """Read nbytes from the peripheral specified by addr.

        :param addr: I2C peripheral device address
        :param nbytes: number of bytes to read
        :return: the bytes read
        """
        return self.driver.readfrom(addr, nbytes)

    def readfrom_into(self, addr: int | Buffer, buf: bytearray, /):
        """Read into buf from the peripheral specified by addr.
        The number of bytes read will be the length of buf.

        :param addr: I2C peripheral device address
        :param buf: buffer to store the bytes read
        """
        return self.driver.readfrom_into(addr, buf)

    def writeto(self, addr: int | Buffer, buf: Buffer, /):
        """Write the bytes from buf to the peripheral specified by addr.

        :param addr: I2C peripheral deivce address
        :param buf: bytes to write
        """
        return self.driver.writeto(addr, buf)

    def readfrom_mem_into(
        self,
        addr: int | Buffer,
        memaddr: int | Buffer,
        buf: bytearray,
        *,
        addrsize: int = 8,
    ):
        """Read into buf from the peripheral specified by addr starting from the
        memory address specified by memaddr. The number of bytes read is the
        length of buf.

        :param addr: I2C peripheral device address
        :param memaddr: memory address
        :param buf: buffer to store the bytes read
        :param addrsize: _description_, defaults to 8
        """
        return self.driver.readfrom_mem_into(addr, memaddr, buf, addrsize=addrsize)

    def readfrom_mem(
        self,
        addr: int | Buffer,
        memaddr: int | Buffer,
        nbytes: int,
        *,
        addrsize: int = 8,
    ) -> bytes:
        """Read *nbytes* from the peripheral specified by *addr* starting from
        the memory address specified by *memaddr*.

        :param addr: I2C peripheral device address
        :param memaddr: memory address
        :param nbytes: number of bytes to read
        :param addrsize: _description_, defaults to 8
        :return: the bytes read
        """
        buf = bytearray(nbytes)
        self.readfrom_mem_into(addr, memaddr, buf, addrsize=addrsize)
        return bytes(buf)

    def writeto_mem(
        self,
        addr: int | Buffer,
        memaddr: int | Buffer,
        buf: Buffer,
        *,
        addrsize: int = 8,
    ):
        """Write buf to the peripheral specified by addr starting from the
        memory address specified by memaddr.

        :param addr: I2C peripheral device address
        :param memaddr: memory address
        :param buf: bytes to write
        :param addrsize: _description_, defaults to 8
        """
        wbuf = bytes(to_buffer(memaddr)) + buf
        self.writeto(addr, wbuf)

    def scan(self, start: int = 0x08, stop: int = 0x77) -> List[int]:
        """Scan all I2C addresses between `start` and `stop` inclusive
        and return a list of those that respond.
        A device responds if it pulls the SDA line low after its address
        (including a write bit) is sent on the bus.

        :param start: start address, defaults to 0x08
        :param stop: stop address, defaults to 0x77
        :return: a list of addresses that respond to scan
        """
        return [a for a in range(start, stop + 1) if self.driver.check_device(a)]
