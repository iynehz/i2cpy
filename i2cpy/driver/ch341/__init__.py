from __future__ import annotations

import os
from ctypes import c_byte, c_int32, c_ulong, c_uint8, create_string_buffer
from enum import Enum
from typing import List, Optional, Type

try:
    from collections.abc import Buffer
except ImportError:
    from typing_extensions import Buffer

from .dll import ch341dll
from .constants import *

from ..abc import I2CDriverBase, i2c_addr_byte, to_buffer
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


class CH341(I2CDriverBase):
    def __init__(
        self,
        id: Optional[int | str] = None,
        *,
        freq: int | float = 400000
    ):
        """Initializes the CH341 I2C driver.

        :param id: CH341 device index number, defaults to 0 on Windows and
            /etc/ch34x_pis0 on posix systems.
        :param freq: I2C bus baudrate, defaults to 400000
        :param dll: CH341 DLL name
        """
        if id is None:
            if os.name == "nt":
                id = 0
            else:
                id = "/dev/ch34x_pis0"

        if os.name == "nt":
            self._fd = id
        else:
            self.device_path = id
            self._fd = -1
        self.baudrate = BaudRate.from_number(freq)

    def init(self):
        """Initialise the I2C bus."""
        if os.name == "nt":
            self._init_nt()
        else:
            self._init_posix()

    def _init_nt(self):
        if ch341dll.CH341OpenDevice(self._fd) != -1:
            ret = ch341dll.CH341SetStream(self._fd, self.baudrate.value)
            self._check_ret(ret)
        else:
            raise OSError("CH341OpenDevice(%s) failed!" % self._fd)

    def _init_posix(self):
        buf = create_string_buffer(b'/dev/ch34x_pis0')
        fd = ch341dll.CH341OpenDevice(buf)
        if fd > 0:
            self._fd = fd

            # Must call this api. Without it later api calls like CH34xSetStream() won't work.
            chip_ver = (c_uint8 * 1)()
            ret = ch341dll.CH34x_GetChipVersion(self._fd, chip_ver)

            ch341dll.CH34xSetStream.argtypes = (c_int32, c_uint8)
            ret = ch341dll.CH34xSetStream(self._fd, self.baudrate.value)
            self._check_ret(ret)
        else:
            raise OSError("CH341OpenDevice(%s) failed!" % self.device_path)

    def deinit(self):
        """Close the I2C bus."""
        ret = ch341dll.CH341CloseDevice(self._fd)
        self._check_ret(ret)

    def _writeread_into(self, buf: Buffer, rbuf: Optional[bytearray]):
        """Write the bytes from `buf` to the bus, and read bytes from the bus
        and stores into `rbuf`. The number of bytes read is the length of buf.
        """
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
        ret = ch341dll.CH341StreamI2C(self._fd, len(ibuf), ibuf, nbytes, obuf)
        self._check_ret(ret)

    def _write(self, buf: Buffer):
        """Write the bytes from buf to the bus."""
        self._writeread_into(buf, None)

    def readfrom_into(self, addr: int | Buffer, buf: bytearray):
        """Read into buf from the peripheral specified by addr.
        The number of bytes read will be the length of buf.

        :param addr: I2C peripheral device address
        :param buf: _description_
        """
        wbuf = i2c_addr_byte(addr)
        self._writeread_into(wbuf, buf)

    def writeto(self, addr: int | Buffer, buf: Buffer | List[int]):
        """Write the bytes from buf to the peripheral specified by addr.

        :param addr: I2C peripheral deivce address
        :param buf: _description_
        """
        wbuf = bytes(i2c_addr_byte(addr)) + to_buffer(buf)
        self._write(wbuf)

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
        wbuf = bytes(i2c_addr_byte(addr)) + to_buffer(memaddr)
        self._writeread_into(wbuf, buf)

    def _start(self):
        """Generate a START condition on the bus
        (SDA transitions to low while SCL is high).
        """
        buf = (c_byte * 3)(
            mCH341A_CMD_I2C_STREAM, mCH341A_CMD_I2C_STM_STA, mCH341A_CMD_I2C_STM_END
        )
        iolength = (c_ulong * 1)(len(buf))
        ret = ch341dll.CH341WriteData(self._fd, buf, iolength)
        self._check_ret(ret)

    def _stop(self):
        """Generate a STOP condition on the bus
        (SDA transitions to high while SCL is high).
        """
        buf = (c_byte * 3)(
            mCH341A_CMD_I2C_STREAM, mCH341A_CMD_I2C_STM_STO, mCH341A_CMD_I2C_STM_END
        )
        iolength = (c_ulong * 1)(len(buf))
        ret = ch341dll.CH341WriteData(self._fd, buf, iolength)
        self._check_ret(ret)

    def _out_byte_check_ack(self, obyte: int) -> bool:
        buf = (c_byte * 4)(
            mCH341A_CMD_I2C_STREAM,
            mCH341A_CMD_I2C_STM_OUT,
            obyte,
            mCH341A_CMD_I2C_STM_END,
        )
        ibuf = (c_byte * mCH341_PACKET_LENGTH)()
        ilen = (c_ulong * 1)(0)
        ret = ch341dll.CH341WriteRead(
            self._fd, len(buf), buf, mCH341A_CMD_I2C_STM_MAX, 1, ilen, ibuf
        )
        self._check_ret(ret)
        return ilen[0] > 0 and ibuf[ilen[0] - 1] & 0x80 == 0

    def check_device(self, addr: int | Buffer) -> bool:
        self._start()
        try:
            obyte = i2c_addr_byte(addr)[0]
            return self._out_byte_check_ack(obyte)
        finally:
            self._stop()

    @classmethod
    def _check_ret(cls, result: int):
        if not result:
            raise I2COperationFailedError()


def driver_class() -> Type[I2CDriverBase]:
    return CH341
