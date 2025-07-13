"""I2C is a two-wire protocol for communicating between devices. At the
physical level it consists of 2 wires: SCL and SDA, the clock and data lines
respectively.

I2C objects are created attached to a specific bus. They can be initialized
when created, or initialized later on.

This library is designed to support different I2C driver implementations.
At present below drivers are supported:

* `CH341 <https://www.wch-ic.com/downloads/CH341DS1_PDF.html>`_
* `CH347 <https://www.wch-ic.com/downloads/CH344DS1_PDF.html>`_

The interface is similar to that of MicroPython's `machine.I2C
<https://docs.micropython.org/en/latest/library/machine.I2C.html>`_

Example usage:

.. code-block:: python

    from i2cpy import I2C

    i2c = I2C()                      # create I2C peripheral

    i2c.writeto(42, b'123')          # write 3 bytes to peripheral with 7-bit address 42
    i2c.readfrom(42, 4)              # read 4 bytes from peripheral with 7-bit address 42

    i2c.readfrom_mem(42, 8, 3)       # read 3 bytes from memory of peripheral 42,
                                     #   starting at memory address 8 in the peripheral
    i2c.writeto_mem(42, 2, b'\\x10')  # write 1 byte to memory of peripheral 42,
                                     #   starting at memory address 2 in the peripheral

If you prefer an "int" interface to the "bytes" interface, you can easily write
wrapper functions youself. For example,

.. code-block:: python

    # assume you already have a gloal i2c object

    def i2c_write(addr: int, memaddr: int, *args):
        i2c.writeto_mem(addr, memaddr, bytes(args))

    def i2c_read(addr: int, memaddr: int, nbytes: int) -> list[int]:
        got = i2c.readfrom_mem(addr, memaddr, nbytes)
        return list(got)

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

from i2cpy.driver.abc import memaddr_to_bytes
from i2cpy.errors import I2CInvalidDriverError, I2CUnsupportedError


from i2cpy._version import __version__  # noqa: F401


log = logging.getLogger(__name__)


class I2C:
    def __init__(
        self,
        id: Optional[int | str] = None,
        *,
        driver: Optional[str] = None,
        freq: int = 400000,
        auto_init: bool = True,
        **kwargs,
    ):
        """Constructor.

        :param id: Identifies a particular I2C peripheral. Allowed values depend
            on the particular driver implementation.
        :param freq: I2C bus baudrate, defaults to 400000
        :param driver: I2C driver name. It corresponds to the I2C driver sub
            module name shipped with this library. For example "foo" means module
            "i2cpy.driver.foo".
            If not specified, it looks at environment variable "I2CPY_DRIVER".
            And if that's not defined or is empty, it finally falls back to "ch341".
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

        self.driver = self.driver_module.driver_class()(id=id, freq=freq, **kwargs)

        if auto_init:
            self.init()

    def init(self):
        """Initialize the I2C bus."""
        self.driver.init()

    def deinit(self):
        """Close the I2C bus."""
        self.driver.deinit()

    def readfrom(self, addr: int, nbytes: int, /) -> bytes:
        """Read nbytes from the peripheral specified by addr.

        :param addr: I2C peripheral device address
        :param nbytes: number of bytes to read
        :return: the bytes read
        """
        return self.driver.readfrom(addr, nbytes)

    def readfrom_into(self, addr: int, buf: bytearray, /):
        """Read into buf from the peripheral specified by addr.
        The number of bytes read will be the length of buf.

        :param addr: I2C peripheral device address
        :param buf: buffer to store the bytes read
        """
        return self.driver.readfrom_into(addr, buf)

    def writeto(self, addr: int, buf: Buffer, /):
        """Write the bytes from buf to the peripheral specified by addr.

        :param addr: I2C peripheral deivce address
        :param buf: bytes to write
        """
        return self.driver.writeto(addr, buf)

    def readfrom_mem_into(
        self,
        addr: int,
        memaddr: int,
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
        :param addrsize: address size in bits, defaults to 8
        """
        return self.driver.readfrom_mem_into(addr, memaddr, buf, addrsize=addrsize)

    def readfrom_mem(
        self,
        addr: int,
        memaddr: int,
        nbytes: int,
        *,
        addrsize: int = 8,
    ) -> bytes:
        """Read *nbytes* from the peripheral specified by *addr* starting from
        the memory address specified by *memaddr*.

        :param addr: I2C peripheral device address
        :param memaddr: memory address
        :param nbytes: number of bytes to read
        :param addrsize: address size in bits, defaults to 8
        :return: the bytes read
        """
        buf = bytearray(nbytes)
        self.readfrom_mem_into(addr, memaddr, buf, addrsize=addrsize)
        return bytes(buf)

    def writeto_mem(
        self,
        addr: int,
        memaddr: int,
        buf: Buffer,
        *,
        addrsize: int = 8,
    ):
        """Write buf to the peripheral specified by addr starting from the
        memory address specified by memaddr.

        :param addr: I2C peripheral device address
        :param memaddr: memory address
        :param buf: bytes to write
        :param addrsize: address size in bits, defaults to 8
        """
        wbuf = memaddr_to_bytes(memaddr, addrsize) + buf
        self.writeto(addr, wbuf)

    def scan(self, start: int = 0x08, stop: int = 0x77) -> List[int]:
        """Scan all I2C addresses between `start` and `stop` inclusive
        and return a list of those that respond.
        A device responds if it pulls the SDA line low after its address
        (including a write bit) is sent on the bus.

        Depending on the specific driver and OS platform, scan() may or may not
        work.

        :param start: start address, defaults to 0x08
        :param stop: stop address, defaults to 0x77
        :return: a list of addresses that respond to scan
        """
        if not self.driver.supports_scan():
            raise I2CUnsupportedError(
                f'Driver "{self.driver_name}" does not support scan() on this OS platform'
            )

        return [a for a in range(start, stop + 1) if self.driver.check_device(a)]
