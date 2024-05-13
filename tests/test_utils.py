import pytest

from i2cpy.driver.abc import to_buffer, memaddr_to_bytes
from i2cpy.errors import *


@pytest.mark.parametrize(
    "addrsize",
    [
        (9,),
        (-8,),
        (64,),
    ],
)
def test_memaddr_to_bytes_error(addrsize):
    with pytest.raises(I2CMemoryAddressSizeError):
        memaddr_to_bytes(0x10, addrsize)


@pytest.mark.parametrize(
    "memaddr,addrsize,expected",
    [
        (0x2A, 8, b"\x2a"),
        (0xC52A, 8, b"\x2a"),
        (0xC52A, 16, b"\xc5\x2a"),
        (0xC52A, 32, b"\x00\x00\xc5\x2a"),
        (0x7B3EC52A, 24, b"\x3e\xc5\x2a"),
        (0x7B3EC52A, 32, b"\x7b\x3e\xc5\x2a"),
    ],
)
def test_memaddr_to_bytes_error(memaddr, addrsize, expected):
    assert memaddr_to_bytes(memaddr, addrsize) == expected
