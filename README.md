# Python I2C library supporting multiple driver implementations

<div>
   <img src="https://img.shields.io/badge/python-3.9+-blue.svg" alt="python"/>
   <a href="https://pypi.org/project/i2cpy/"><img src="https://img.shields.io/pypi/v/i2cpy.svg" alt="pypi"/></a>
   <a href="https://github.com/iynehz/i2cpy/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-green" alt="license"/></a>
   <img src="https://readthedocs.org/projects/i2cpy/badge/?version=latest" alt="docs"/>
   <img src="https://github.com/iynehz/i2cpy/actions/workflows/lint.yml/badge.svg" alt="lint"/>
</div>

## Introduction

I2C is a two-wire protocol for communicating between devices. At the
physical level it consists of 2 wires: SCL and SDA, the clock and data lines
respectively.

I2C objects are created attached to a specific bus. They can be initialized
when created, or initialized later on.

This library is designed to support different I2C driver implementations.
At present below drivers are supported:

* [CH341](https://www.wch-ic.com/downloads/CH341DS1_PDF.html)
* [CH347](https://www.wch-ic.com/downloads/CH347DS1_PDF.html)

The interface is similar to that of MicroPython’s [machine.I2C](https://docs.micropython.org/en/latest/library/machine.I2C.html)

Example usage:

```python
from i2cpy import I2C

i2c = I2C()                      # create I2C peripheral

i2c.writeto(42, b'123')          # write 3 bytes to peripheral with 7-bit address 42
i2c.readfrom(42, 4)              # read 4 bytes from peripheral with 7-bit address 42

i2c.readfrom_mem(42, 8, 3)       # read 3 bytes from memory of peripheral 42,
                                 #   starting at memory address 8 in the peripheral
i2c.writeto_mem(42, 2, b'\x10')  # write 1 byte to memory of peripheral 42,
                                 #   starting at memory address 2 in the peripheral
```

If you prefer an “int” interface to the “bytes” interface, you can easily write
wrapper functions youself. For example,

```python
# assume you already have a gloal i2c object

def i2c_write(addr: int, memaddr: int, *args):
    i2c.writeto_mem(addr, memaddr, bytes(args))

def i2c_read(addr: int, memaddr: int, nbytes: int) -> list[int]:
    got = i2c.readfrom_mem(addr, memaddr, nbytes)
    return list(got)
```

## Installation

The i2cpy Python module itself can be simply pip installed,

```default
pip intall i2cpy
```

And for the underlying I2C implementations you still need to install their
corresponding drivers.

### ch341

The CH341 series chip (like CH341A) is USB bus converter which converts USB to UART, parallel
port, and common synchronous serial communication interfaces (I2C, SPI).
The chip is manufactured by the company [Qinheng Microelectronics](https://wch-ic.com/).

The “ch341” driver shipped with this library is a Python interface to CH341’s
official DLLs.

You need the driver DLL files, which are downloadable from Qinheng’s website.

* **Windows**: [https://www.wch-ic.com/downloads/CH341PAR_EXE.html](https://www.wch-ic.com/downloads/CH341PAR_EXE.html)

  They also have a zipball [https://www.wch-ic.com/downloads/CH341PAR_ZIP.html](https://www.wch-ic.com/downloads/CH341PAR_ZIP.html) .
  If you use the zipball on Windows it’s recommended to place the DLL files,
  CH341DLLA64.DLL and/or CH341DLL.DLL depending on the bitness, under Windows
  System32/SysWOW64 folder. Or if you place them under a different directory,
  you can add that directory to PATH environment variable.
* **Linux**: [https://www.wch-ic.com/downloads/CH341PAR_LINUX_ZIP.html](https://www.wch-ic.com/downloads/CH341PAR_LINUX_ZIP.html)

  On Linux you need to build the kernel module from source under the downloaded
  zipball’s driver sub-directory like below.
  ```bash
  $ cd driver
  $ sudo rmmod ch34x_pis
  $ make && sudo make install
  ```

  Also you need to either place the libch347.so file for your platform to system
  supported path like /usr/local/lib, or you make the so file loadable by adding
  its directory to LD_LIBRARY_PATH environment variable.

  And because Qinheng sometimes updates their Linux driver and breaks backward
  compatibility, be careful when you upgrade their Linux CH341PAR driver version,
  and make sure your effective libch347.so file and your compiled kernel module
  come from the same driver version.

  Still on Linux there could be more details like, system package
  linux-headers-$(uname -r) being a prerequisite of making the kernel module,
  and permissioning of /dev/ch34x_pis\*, etc..
  Those are beyond scope of this doc though.
* **macOS** is not supported. See also [this ticket](https://github.com/iynehz/i2cpy/issues/3).

Example usage:

```python
from i2cpy import I2C

i2c = I2C()                                     # ch341 is the default driver
i2c = I2C(driver="ch341")                       # explicitly specify driver

i2c = I2C(0)                                    # override usb id

i2c = I2C("/dev/ch34x_pis0")                    # override device path on Linux
```

### ch347

The CH347 series chip (like CH347T) is also USB bus converter manufactured by
The chip is manufactured by the Qinheng Microelectronics.

The “ch347” driver shipped with this library is a Python interface to CH347’s
official DLLs.

You need the driver DLL files, which are downloadable from Qinheng’s website.
As they are actually the same downloadable files as that of CH341, see
[ch341](#id1) section above for how to install.

Example usage:

```python
from i2cpy import I2C

i2c = I2C(driver="ch347")                       # specify ch347 driver

i2c = I2C(0, driver="ch347")                    # override usb id

i2c = I2C("/dev/ch34x_pis0", driver="ch347")    # override device path on Linux
```

## Class I2C

### Constructor

#### I2C.\_\_init_\_(id=None, , driver=None, freq=400000, auto_init=True, \*\*kwargs)

Constructor.

* **Parameters:**
  * **id** (`Union`[`str`, `int`, `None`]) – Identifies a particular I2C peripheral. Allowed values depend
    on the particular driver implementation.
  * **freq** (`int`) – I2C bus baudrate, defaults to 400000
  * **driver** (`Optional`[`str`]) – I2C driver name. It corresponds to the I2C driver sub
    module name shipped with this library. For example “foo” means module
    “i2cpy.driver.foo”.
    If not specified, it looks at environment variable “I2CPY_DRIVER”.
    And if that’s not defined or is empty, it finally falls back to “ch341”.
  * **auto_init** (`bool`) – Call init() on object initialization, defaults to True

### General methods

#### I2C.init()

Initialize the I2C bus.

#### I2C.deinit()

Close the I2C bus.

#### I2C.scan(start=8, stop=119)

Scan all I2C addresses between start and stop inclusive
and return a list of those that respond.
A device responds if it pulls the SDA line low after its address
(including a write bit) is sent on the bus.

Depending on the specific driver and OS platform, scan() may or may not
work.

* **Parameters:**
  * **start** (`int`) – start address, defaults to 0x08
  * **stop** (`int`) – stop address, defaults to 0x77
* **Return type:**
  `List`[`int`]
* **Returns:**
  a list of addresses that respond to scan

### Standard bus operations

#### I2C.writeto(addr, buf,)

Write the bytes from buf to the peripheral specified by addr.

* **Parameters:**
  * **addr** (`int`) – I2C peripheral deivce address
  * **buf** (`Buffer`) – bytes to write

#### I2C.readfrom(addr, nbytes,)

Read nbytes from the peripheral specified by addr.

* **Parameters:**
  * **addr** (`int`) – I2C peripheral device address
  * **nbytes** (`int`) – number of bytes to read
* **Return type:**
  `bytes`
* **Returns:**
  the bytes read

### Memory operations

#### I2C.writeto_mem(addr, memaddr, buf, , addrsize=8)

Write buf to the peripheral specified by addr starting from the
memory address specified by memaddr.

* **Parameters:**
  * **addr** (`int`) – I2C peripheral device address
  * **memaddr** (`int`) – memory address
  * **buf** (`Buffer`) – bytes to write
  * **addrsize** (`int`) – address size in bits, defaults to 8

#### I2C.readfrom_mem(addr, memaddr, nbytes, , addrsize=8)

Read *nbytes* from the peripheral specified by *addr* starting from
the memory address specified by *memaddr*.

* **Parameters:**
  * **addr** (`int`) – I2C peripheral device address
  * **memaddr** (`int`) – memory address
  * **nbytes** (`int`) – number of bytes to read
  * **addrsize** (`int`) – address size in bits, defaults to 8
* **Return type:**
  `bytes`
* **Returns:**
  the bytes read

#### I2C.readfrom_mem_into(addr, memaddr, buf, , addrsize=8)

Read into buf from the peripheral specified by addr starting from the
memory address specified by memaddr. The number of bytes read is the
length of buf.

* **Parameters:**
  * **addr** (`int`) – I2C peripheral device address
  * **memaddr** (`int`) – memory address
  * **buf** (`bytearray`) – buffer to store the bytes read
  * **addrsize** (`int`) – address size in bits, defaults to 8

## Nuitka

If you use [Nuitka](https://nuitka.net/) to package your Python code that uses
i2cpy, you need to specify the implicit-imported module, as otherwise Nuitka
won’t be able to find by itself. For example you can use a
nuitka-package.config.yml file with below content.

```yaml
- module-name: 'i2cpy'
  implicit-imports:
    - depends:
      - 'i2cpy.driver.ch341'
```

And run the nuitka command like,

```cmd
nuitka --standalone --onefile --user-package-configuration-file=nuitka-package.config.yml your_script.py
```

For other packaging tools like Pyinstaller, etc., the idea is similar.
