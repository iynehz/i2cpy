import sys
import os
import re

if os.name == "nt":
    from ctypes import windll, CDLL
else:
    from ctypes import cdll, CDLL, c_char_p


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
        dll = cdll.LoadLibrary(dll_name)

        funcs = [
            "CH341OpenDevice",
            "CH341CloseDevice",
            "CH341SetStream",
            "CH341StreamI2C",
            "CH341WriteData",
            "CH341WriteRead"
        ]

        for fname in funcs:
            if not getattr(dll, fname, None):
                fname2 = re.sub(r"^CH341", "CH34x", fname)
                f = getattr(dll, fname2)
                setattr(dll, fname, f)

        dll.CH341OpenDevice.argtypes = c_char_p,

        return dll


ch341dll = load()
