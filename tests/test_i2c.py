# I have a single-byte-addr I2C flash mem for the test.

import pytest

import os
from i2cpy import I2C
from i2cpy.errors import *


addr = 0x17


def test_driver():
    with pytest.raises(I2CInvalidDriverError):
        i2c = I2C(driver="somethingbad")

    if os.name == "posix":
        i2c_by_device_id = I2C(0)
        i2c_by_device_file = I2C("/dev/ch34x_pis0")


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


def test_i2c_user_wrapper_funcs():
    i2c = I2C(freq=100e3)

    def i2c_write(addr: int, memaddr: int, *args):
        print(bytes(args))
        i2c.writeto_mem(addr, memaddr, bytes(args))

    def i2c_read(addr: int, memaddr: int, nbytes: int) -> list[int]:
        got = i2c.readfrom_mem(addr, memaddr, nbytes)
        print(got)
        return list(got)

    memaddr = 0x20
    for data in ([0x55, 0xAA, 0xAA, 0x55], [0x00, 0x00, 0x00, 0x00]):
        i2c_write(addr, memaddr, *data)
        assert i2c_read(addr, memaddr, 4) == data
