import sys
import os
import re

if sys.platform == "win32":
    from ctypes import windll, CDLL
else:
    from ctypes import cdll, CDLL, c_char_p, c_int32, c_uint8


def load() -> CDLL:
    dll_name = os.getenv("CH347DLL")
    if dll_name is None:
        if sys.platform == "win32":
            dll_name = "CH347DLLA64.dll" if sys.maxsize > 2147483647 else "CH347DLL.dll"
        else:
            dll_name = "libch347.so"

    if sys.platform == "win32":
        return windll.LoadLibrary(dll_name)
    else:
        dll = cdll.LoadLibrary(dll_name)

        # Unfortunately QingHeng does not well align their API names across OS platforms...
        dll.CH347StreamI2C_RetACK = dll.CH347StreamI2C_RetAck

        return dll


ch347dll = load()
