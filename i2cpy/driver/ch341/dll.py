import sys
import os
from ctypes import c_byte, windll, cdll, CDLL


def load() -> CDLL:
    dll_name = os.getenv("CH341DLL")
    if dll_name is None:
        if os.name == "nt":
            dll_name = "CH341DLLA64.dll" if sys.maxsize > 2147483647 else "CH341DLL.dll"
        else:
            dll_name = "libch347.so"

    if os.name == "nt":
        return windll.LoadLibrary(dll_name)
    else:
        return cdll.LoadLibrary(dll_name)


ch341dll = load()
