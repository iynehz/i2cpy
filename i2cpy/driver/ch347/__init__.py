from __future__ import annotations

import sys
from ctypes import c_byte, c_ulong, c_uint8, create_string_buffer
from enum import Enum
from typing import List, Optional, Type

try:
    from collections.abc import Buffer
except ImportError:
    from typing_extensions import Buffer

from .dll import ch347dll
from .constants import (
    mCH347_PACKET_LENGTH,
    mCH347A_CMD_I2C_STREAM,
    mCH347A_CMD_I2C_STM_STA,
    mCH347A_CMD_I2C_STM_STO,
    mCH347A_CMD_I2C_STM_OUT,
    mCH347A_CMD_I2C_STM_MAX,
    mCH347A_CMD_I2C_STM_END,
)

from ..abc import I2CDriverBase, i2c_addr_byte, to_buffer, memaddr_to_bytes
from ...errors import I2COperationFailedError


class BaudRate(Enum):
    BAUD20K = 0
    BAUD100K = 1
    BAUD400K = 2
    BAUD750K = 3

    @classmethod
    def from_number(cls, freq: int | float) -> BaudRate:
        if freq >= 750e3:
            return BaudRate.BAUD750K
        if freq >= 400e3:
            return BaudRate.BAUD400K
        if freq >= 100e3:
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
            #ret = ch347dll.CH347SetStream(self._fd, self.baudrate.value)
            #self._check_ret(ret, "CH341SetStream")
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
                ret = ch347dll.CH34x_GetChipVersion(self._fd, chip_ver)

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
        #ret = ch347dll.CH347StreamI2CRetAck(self._fd, len(ibuf), ibuf, nbytes, obuf, cc)
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

    def _start(self):
        """Generate a START condition on the bus
        (SDA transitions to low while SCL is high).
        """
        buf = (c_byte * 3)(
            mCH347A_CMD_I2C_STREAM, mCH347A_CMD_I2C_STM_STA, mCH347A_CMD_I2C_STM_END
        )
        iolength = (c_ulong * 1)(len(buf))
        ret = ch347dll.CH347WriteData(self._fd, buf, iolength)
        self._check_ret(ret, "CH347WriteData")

    def _stop(self):
        """Generate a STOP condition on the bus
        (SDA transitions to high while SCL is high).
        """
        buf = (c_byte * 3)(
            mCH347A_CMD_I2C_STREAM, mCH347A_CMD_I2C_STM_STO, mCH347A_CMD_I2C_STM_END
        )
        iolength = (c_ulong * 1)(len(buf))
        ret = ch347dll.CH347WriteData(self._fd, buf, iolength)
        self._check_ret(ret, "CH347WriteData")

    def _out_byte_check_ack(self, obyte: int) -> bool:
        buf = (c_byte * 4)(
            mCH347A_CMD_I2C_STREAM,
            mCH347A_CMD_I2C_STM_OUT,
            obyte,
            mCH347A_CMD_I2C_STM_END,
        )
        ibuf = (c_byte * mCH347_PACKET_LENGTH)()
        ilen = (c_ulong * 1)(0)
        ret = ch347dll.CH347WriteRead(
            self._fd, len(buf), buf, mCH347A_CMD_I2C_STM_MAX, 1, ilen, ibuf
        )
        self._check_ret(ret, "CH347WriteRead")
        return ilen[0] > 0 and ibuf[ilen[0] - 1] & 0x80 == 0

    def check_device(self, addr: int | Buffer) -> bool:
        self._start()
        try:
            obyte = i2c_addr_byte(addr)[0]
            return self._out_byte_check_ack(obyte)
        finally:
            self._stop()

    @classmethod
    def _check_ret(cls, result: int, operation: str):
        #print("pippo")
        #print(result)
        if not result:
            raise I2COperationFailedError(operation)
            #print("raise")
        #else:
            #print("ok")
            #print(not result)

def driver_class() -> Type[I2CDriverBase]:
    return CH347
