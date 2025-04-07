from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, TypeVar

try:
    from collections.abc import Buffer
except ImportError:
    from typing_extensions import Buffer

from ..errors import I2CMemoryAddressSizeError


def i2c_addr_byte(addr: int | Buffer, is_read: bool = False) -> bytes:
    """Convert 7-bit I2C peripheral address to bytes.

    :param addr: 7-bit peripheral address
    :param is_read: True for read
    :return: 1-byte `bytes` that can be written to I2C bus
    """
    if isinstance(addr, int):
        addr = addr << 1
    else:
        addr = int(memoryview(addr)[0]) << 1

    if is_read:
        addr |= 1

    return addr.to_bytes(1, "big")


def to_buffer(x: Buffer | List[int] | int) -> Buffer:
    """Convert input data to `Buffer` (`bytes`).

    :param x: input data
    :return: x if x is `Buffer`, otherwise `bytes` converted from x
    """
    if isinstance(x, Buffer):
        return x
    if isinstance(x, list):
        return bytes(x)
    return bytes([x])


def memaddr_to_bytes(memaddr: int, addrsize: int = 8) -> bytes:
    """Convert memory address to `bytes`.

    :param memaddr: memory address in integer.
    :param addrsize: must be one of 8, 16, 24, 32. Default is 8.
    :return: memory address in `bytes`
    """
    if addrsize & 0x7 != 0 or addrsize > 32 or addrsize < 8:
        raise I2CMemoryAddressSizeError(addrsize)
    return bytes(
        to_buffer([(memaddr >> i) & 0xFF for i in range(addrsize - 8, -1, -8)])
    )


class I2CDriverBase(ABC):
    @abstractmethod
    def __init__(
        self,
        id: int = 0,
        *,
        freq: int = 400000,
        **kwargs,
    ):
        """_summary_

        :param id: device id number, defaults to 0
        :param freq: I2C bus baudrate, defaults to 400000
        :param auto_init: Call `init()` on object initialization, defaults to True
        """

    @abstractmethod
    def init(self):
        """Initialise the I2C bus."""

    @abstractmethod
    def deinit(self):
        """Close the I2C bus."""

    def readfrom(self, addr: int, nbytes: int) -> bytes:
        """Read nbytes from the peripheral specified by addr.

        :param addr: I2C peripheral device address
        :param nbytes: number of bytes to read
        :return: the data read
        """
        buf = bytearray(nbytes)
        self.readfrom_into(addr, buf)
        return bytes(buf)

    @abstractmethod
    def readfrom_into(self, addr: int, buf: bytearray):
        """Read into buf from the peripheral specified by addr.
        The number of bytes read will be the length of buf.

        :param addr: I2C peripheral device address
        :param buf: buffer to store the bytes read
        """

    @abstractmethod
    def writeto(self, addr: int, buf: Buffer):
        """Write the bytes from buf to the peripheral specified by addr.

        :param addr: I2C peripheral deivce address
        :param buf: bytes to write
        """

    @abstractmethod
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
        """

    @abstractmethod
    def check_device(self, addr: int) -> bool:
        """Checks if I2C peripheral device exists at given address.

        :param addr: I2C peripheral device address
        :return: True if device responds.
        """


I2CDriver = TypeVar("I2CDriver", bound=I2CDriverBase)
