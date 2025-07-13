from __future__ import annotations

import sys
from ctypes import c_byte, c_ulong, c_uint8, create_string_buffer, byref
from enum import Enum
from typing import List, Optional, Type


try:
    from collections.abc import Buffer
except ImportError:
    from typing_extensions import Buffer

from .dll import ch347dll

from ..abc import I2CDriverBase, i2c_addr_byte, to_buffer, memaddr_to_bytes
from ...errors import I2COperationFailedError

class BaudRate(Enum):
    BAUD20K = 0
    BAUD100K = 1
    BAUD400K = 2
    BAUD750K = 3
    BAUD50K = 4
    BAUD200K = 5
    BAUD1M = 6

    @classmethod
    def from_number(cls, freq: int | float) -> BaudRate:
        if freq >= 1000e3:
            return BaudRate.BAUD1M
        if freq >= 750e3:
            return BaudRate.BAUD750K
        if freq >= 400e3:
            return BaudRate.BAUD400K
        if freq >= 100e3:
            return BaudRate.BAUD200K
        if freq >= 200e3:
            return BaudRate.BAUD100K
        if freq >= 100e3:
            return BaudRate.BAUD50K
        if freq >= 50e3:
            return BaudRate.BAUD100K
        return BaudRate.BAUD20K

class CH347(I2CDriverBase):
    def __init__(self, id: Optional[int | str] = None, *, freq: int | float = 400000):
        """Initializes the CH347 I2C driver.

        :param id: CH341 device index number.
            On Windows it's an integer and default is 0.
            On posix systems it can be either a string like "/dev/ch34x_pis0"
            or an integer like 0 that would be internally mapped to the string
            form "/dev/ch34x_pis0", default is "/dev/ch34x_pis0".
        :param freq: I2C bus baudrate, defaults to 400000
        :param dll: CH347 DLL name
        """
        if id is None:
            id = 0

        if sys.platform == "win32":
            self._fd = id
        else:
            if isinstance(id, int):
                self.device_path = f"/dev/ch34x_pis{id}"
            else:
                self.device_path = str(id)
            self._fd = None
        self.baudrate = BaudRate.from_number(freq)

    def init(self):
        """Initialize the I2C bus."""
        if sys.platform == "win32":
            self._init_nt()
        else:
            self._init_posix()

    def _init_nt(self):
        if ch347dll.CH347OpenDevice(self._fd) != -1:
            ret = ch347dll.CH347I2C_Set(self._fd, self.baudrate.value)
            self._check_ret(ret, "CH347I2C_Set")
            # ret = ch347dll.CH347SetStream(self._fd, self.baudrate.value)
            # self._check_ret(ret, "CH341SetStream")
            pass
        else:
            raise I2COperationFailedError("CH347OpenDevice")

    def _init_posix(self):
        buf = create_string_buffer(bytes(self.device_path, "utf-8"))
        fd = ch347dll.CH347OpenDevice(buf)
        if fd > 0:
            self._fd = fd

            # It's not needed for CH34x Linux driver versions like 1.6.
            # But for older versions of CH34x Linux driver like 1.4, below
            # has to be called to get CH34xSetStream() work.
            get_chip_version = getattr(ch347dll, "CH34x_GetChipVersion")
            if get_chip_version:
                chip_ver = (c_uint8 * 1)()
                ch347dll.CH34x_GetChipVersion(self._fd, chip_ver)

        #            ret = ch347dll.CH34xSetStream(self._fd, self.baudrate.value)
        #            self._check_ret(ret, "CH34xSetStream")
        else:
            raise I2COperationFailedError(
                "CH347OpenDevice(%s) failed!" % self.device_path
            )

    def deinit(self):
        """Close the I2C bus."""
        ret = ch347dll.CH347CloseDevice(self._fd)
        self._check_ret(ret, "CH347CloseDevice")

    def _writeread_into(self, buf: Buffer, rbuf: Optional[bytearray]):
        try:
            ibuf = (c_byte * len(memoryview(buf))).from_buffer(buf)
        except TypeError:
            # When buf is bytes, above gets "TypeError: underlying buffer is not writable".
            # In this case we retry with from_buffer_copy()
            ibuf = (c_byte * len(memoryview(buf))).from_buffer_copy(buf)

        if rbuf is None:
            nbytes = 0
            obuf = None
        else:
            nbytes = len(rbuf)
            obuf = (c_byte * nbytes).from_buffer(rbuf)
        ret = ch347dll.CH347StreamI2C(self._fd, len(ibuf), ibuf, nbytes, obuf)
        self._check_ret(ret, "CH347StreamI2C")

    def _write(self, buf: Buffer):
        self._writeread_into(buf, None)

    def readfrom_into(self, addr: int, buf: bytearray):
        wbuf = i2c_addr_byte(addr)
        self._writeread_into(wbuf, buf)

    def writeto(self, addr: int, buf: Buffer | List[int]):
        wbuf = bytes(i2c_addr_byte(addr)) + to_buffer(buf)
        self._write(wbuf)

    def readfrom_mem_into(
        self,
        addr: int,
        memaddr: int,
        buf: bytearray,
        *,
        addrsize: int = 8,
    ):
        wbuf = bytes(i2c_addr_byte(addr)) + memaddr_to_bytes(memaddr, addrsize)
        self._writeread_into(wbuf, buf)

    def _out_byte_check_ack(self, obyte: int) -> bool:
        buf = [obyte]
        write_buffer = create_string_buffer(bytes(buf))
        ack_count = c_ulong(0)
        ret = ch347dll.CH347StreamI2C_RetACK(
            self._fd, 1, write_buffer, None, None, byref(ack_count)
        )
        self._check_ret(ret, "CH347StreamI2C_RetACK")
        return ack_count.value > 0

    def check_device(self, addr: int | Buffer) -> bool:
        obyte = i2c_addr_byte(addr)[0]
        return self._out_byte_check_ack(obyte)

    @classmethod
    def _check_ret(cls, result: int, operation: str):
        if not result:
            raise I2COperationFailedError(operation)


def driver_class() -> Type[I2CDriverBase]:
    return CH347
