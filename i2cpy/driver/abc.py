from abc import ABC, abstractmethod
from typing import List, TypeVar

try:
    from collections.abc import Buffer
except ImportError:
    from typing_extensions import Buffer


def i2c_addr_byte(addr: int | Buffer, is_read: bool = False) -> bytes:
    """Convert 7-bit I2C peripheral address to bytes.

    :param addr: 7-bit peripheral address
    :param is_read: True for read
    :return: 1-byte `bytes` that can be written to I2C bus
    """
    if isinstance(addr, int):
        addr = addr << 1
    else:
        addr = int(addr[0]) << 1

    if is_read:
        addr |= 1

    return addr.to_bytes(1)


def to_buffer(x: Buffer | List[int]) -> Buffer:
    """Convert input data to `Buffer` (`bytes`).

    :param x: input data
    :return: x if x is `Buffer`, otherwise `bytes` converted from x
    """
    if isinstance(x, Buffer):
        return x

    return bytes(x)


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
        self.id = id
        self.baudrate = freq

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
    def readfrom_into(self, addr: int | Buffer, buf: bytearray):
        """Read into buf from the peripheral specified by addr.
        The number of bytes read will be the length of buf.

        :param addr: I2C peripheral device address
        :param buf: buffer to store the bytes read
        """

    @abstractmethod
    def writeto(self, addr: int | Buffer, buf: Buffer):
        """Write the bytes from buf to the peripheral specified by addr.

        :param addr: I2C peripheral deivce address
        :param buf: bytes to write
        """

    @abstractmethod
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
        """

    @abstractmethod
    def check_device(self, addr: int | Buffer) -> bool:
        """Checks if I2C peripheral device exists at given address.

        :param addr: I2C peripheral device address
        :return: True if device responds.
        """


I2CDriver = TypeVar("I2CDriver", bound=I2CDriverBase)
