# I have a single-byte-addr I2C flash mem for the test.

import pytest

import os
from typing import List
from i2cpy import I2C
from i2cpy.errors import *


addr = 0x17


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

    assert i2c.scan() == [addr]

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
def test_i2c_mem(memaddr, buf, expected):
    i2c = I2C(freq=100e3)

    i2c.writeto_mem(addr, memaddr, buf)
    assert i2c.readfrom_mem(addr, memaddr, len(expected)) == expected


def test_i2c_user_wrapper_funcs():
    i2c = I2C(freq=100e3)

    def i2c_write(addr: int, memaddr: int, *args):
        i2c.writeto_mem(addr, memaddr, bytes(args))

    def i2c_read(addr: int, memaddr: int, nbytes: int) -> List[int]:
        got = i2c.readfrom_mem(addr, memaddr, nbytes)
        return list(got)

    memaddr = 0x20
    for data in ([0x55, 0xAA, 0xAA, 0x55], [0x00, 0x00, 0x00, 0x00]):
        i2c_write(addr, memaddr, *data)
        assert i2c_read(addr, memaddr, 4) == data
