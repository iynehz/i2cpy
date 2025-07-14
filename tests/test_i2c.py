# See board/eeprom_board for my test board
import pytest

import os
import time
from typing import List

from i2cpy import I2C
from i2cpy.errors import *


addr_1byte_mem = 0x51
addr_2byte_mem = 0x52


def test_driver():
    with pytest.raises(I2CInvalidDriverError):
        I2C(driver="somethingbad")

    if os.name == "posix":
        I2C(0)
        I2C("/dev/ch34x_pis0")


def test_invalid_device():
    with pytest.raises(I2COperationFailedError):
        I2C(999)

    if os.name == "posix":
        with pytest.raises(I2COperationFailedError):
            I2C("/dev/null")


def test_scan():
    i2c = I2C()

    if not i2c.driver.supports_scan():
        pytest.skip("Skipping as scan() not supported")

    assert i2c.scan() == [addr_1byte_mem, addr_2byte_mem]

    # now close device and it should error on rest operations
    i2c.deinit()
    with pytest.raises(I2COperationFailedError):
        i2c.scan()


@pytest.mark.parametrize(
    "memaddr,buf,expected",
    [
        (0x10, b"\x55\xaa\x55\xaa", b"\x55\xaa\x55\xaa"),
        (0x10, b"\xaa\x55\xaa\x55", b"\xaa\x55\xaa\x55"),
        (0x10, bytearray(b"\x55\xaa\x55\xaa"), b"\x55\xaa\x55\xaa"),
        (0x10, bytearray(b"\xaa\x55\xaa\x55"), b"\xaa\x55\xaa\x55"),
        (0x10, b"\x00\x00\x00\x00", b"\x00\x00\x00\x00"),
    ],
)
def test_i2c_mem_1byte_addr(memaddr, buf, expected):
    i2c = I2C(freq=100e3)

    i2c.writeto_mem(addr_1byte_mem, memaddr, buf)
    time.sleep(0.01)
    assert i2c.readfrom_mem(addr_1byte_mem, memaddr, len(expected)) == expected


@pytest.mark.parametrize(
    "memaddr,buf,expected",
    [
        (0x0110, b"\x55\xaa\x55\xaa", b"\x55\xaa\x55\xaa"),
        (0x0110, b"\xaa\x55\xaa\x55", b"\xaa\x55\xaa\x55"),
        (0x0110, bytearray(b"\x55\xaa\x55\xaa"), b"\x55\xaa\x55\xaa"),
        (0x0110, bytearray(b"\xaa\x55\xaa\x55"), b"\xaa\x55\xaa\x55"),
        (0x0110, b"\x00\x00\x00\x00", b"\x00\x00\x00\x00"),
    ],
)
def test_i2c_mem_2byte_addr(memaddr, buf, expected):
    i2c = I2C(freq=100e3)

    i2c.writeto_mem(addr_2byte_mem, memaddr, buf, addrsize=16)
    time.sleep(0.01)
    assert (
        i2c.readfrom_mem(addr_2byte_mem, memaddr, len(expected), addrsize=16)
        == expected
    )


def test_i2c_user_wrapper_funcs():
    i2c = I2C(freq=100e3)

    def i2c_write(addr: int, memaddr: int, *args):
        i2c.writeto_mem(addr, memaddr, bytes(args))
        time.sleep(0.01)

    def i2c_read(addr: int, memaddr: int, nbytes: int) -> List[int]:
        got = i2c.readfrom_mem(addr, memaddr, nbytes)
        return list(got)

    memaddr = 0x20
    for data in ([0x55, 0xAA, 0xAA, 0x55], [0x00, 0x00, 0x00, 0x00]):
        i2c_write(addr_1byte_mem, memaddr, *data)
        assert i2c_read(addr_1byte_mem, memaddr, 4) == data
