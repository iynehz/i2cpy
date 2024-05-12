import pytest

import os
from i2cpy import I2C
from i2cpy.errors import *


addr = 0x17


def test_driver():
    with pytest.raises(I2CInvalidDriverError):
        i2c = I2C(driver="somethingbad")


def test_scan():
    i2c = I2C()
    assert i2c.scan() == [addr]


@pytest.mark.parametrize(
    "memaddr,buf,expected",
    [
        (0x10, b"\x55\xaa\x55\xaa", b"\x55\xaa\x55\xaa"),
        (0x10, b"\xaa\x55\xaa\x55", b"\xaa\x55\xaa\x55"),
        (0x10, bytearray(b"\x55\xaa\x55\xaa"), b"\x55\xaa\x55\xaa"),
        (0x10, bytearray(b"\xaa\x55\xaa\x55"), b"\xaa\x55\xaa\x55"),
    ],
)
def test_i2c_mem(memaddr, buf, expected):
    i2c = I2C(freq=100e3)

    i2c.writeto_mem(addr, memaddr, buf)
    assert i2c.readfrom_mem(addr, memaddr, len(expected)) == expected
