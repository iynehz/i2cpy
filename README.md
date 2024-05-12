# Python I2C library supporting multiple driver implementations

<div>
   <img src="https://img.shields.io/badge/python-3.7+-blue.svg" alt="python"/>
   <a href="https://pypi.org/project/i2cpy/"><img src="https://img.shields.io/pypi/v/i2cpy.svg" alt="pypi"/></a>
   <a href="https://github.com/iynehz/i2cpy/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-green" alt="license"/></a>
   <img src="https://img.shields.io/badge/code%20style-black-black.svg" alt="Code style: black"/>
   <img src="https://img.shields.io/badge/mypy-checked-green.svg" alt="mypy"/>
</div>

## Introduction

I2C is a two-wire protocol for communicating between devices. At the
physical level it consists of 2 wires: SCL and SDA, the clock and data lines
respectively.

I2C objects are created attached to a specific bus. They can be initialized
when created, or initialized later on.

This library is designed to support different I2C driver implementations.
It’s interface is similar to MicroPython’s `machine.I2C` as well as CircuitPython’s
`board.I2C` classes.

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

## Class I2C

### Constructor

#### I2C.\_\_init_\_(\*, id=None, driver=None, freq=400000, auto_init=True, \*\*kwargs)

Constructor.

* **Parameters:**
  * **id** (`Union`[`int`, `str`, `None`]) – Identifies a particular I2C peripheral. Allowed values depend
    on the particular driver implementation.
  * **freq** (`int`) – I2C bus baudrate, defaults to 400000
  * **driver** (`Optional`[`str`]) – I2C driver name. It corresponds to the I2C driver sub
    module name shipped with this library. For example “foo” means module
    “i2cpy.driver.foo”.
    If not specified, it looks at environment variable “I2CPY_DRIVER”.
    And if that’s not defined or empty, it finally falls back to “ch341”.
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

* **Parameters:**
  * **start** (`int`) – start address, defaults to 0x08
  * **stop** (`int`) – stop address, defaults to 0x77
* **Return type:**
  `List`[`int`]
* **Returns:**
  a list of addresses that respond to scan

### Standard bus operations

#### I2C.writeto(addr, buf, /)

Write the bytes from buf to the peripheral specified by addr.

* **Parameters:**
  * **addr** (`int` | `Buffer`) – I2C peripheral deivce address
  * **buf** (`Buffer`) – bytes to write

#### I2C.readfrom(addr, nbytes, /)

Read nbytes from the peripheral specified by addr.

* **Parameters:**
  * **addr** (`int` | `Buffer`) – I2C peripheral device address
  * **nbytes** (`int`) – number of bytes to read
* **Return type:**
  `bytes`
* **Returns:**
  the bytes read

### Memory operations

#### I2C.writeto_mem(addr, memaddr, buf, \*, addrsize=8)

Write buf to the peripheral specified by addr starting from the
memory address specified by memaddr.

* **Parameters:**
  * **addr** (`int` | `Buffer`) – I2C peripheral device address
  * **memaddr** (`int` | `Buffer`) – memory address
  * **buf** (`Buffer`) – bytes to write
  * **addrsize** (`int`) – \_description_, defaults to 8

#### I2C.readfrom_mem(addr, memaddr, nbytes, \*, addrsize=8)

Read *nbytes* from the peripheral specified by *addr* starting from
the memory address specified by *memaddr*.

* **Parameters:**
  * **addr** (`int` | `Buffer`) – I2C peripheral device address
  * **memaddr** (`int` | `Buffer`) – memory address
  * **nbytes** (`int`) – number of bytes to read
  * **addrsize** (`int`) – \_description_, defaults to 8
* **Return type:**
  `bytes`
* **Returns:**
  the bytes read

#### I2C.readfrom_mem_into(addr, memaddr, buf, \*, addrsize=8)

Read into buf from the peripheral specified by addr starting from the
memory address specified by memaddr. The number of bytes read is the
length of buf.

* **Parameters:**
  * **addr** (`int` | `Buffer`) – I2C peripheral device address
  * **memaddr** (`int` | `Buffer`) – memory address
  * **buf** (`bytearray`) – buffer to store the bytes read
  * **addrsize** (`int`) – \_description_, defaults to 8

## Supported I2C drivers

### ch341

The CH341 series chip (like CH341A) is USB bus converter which converts USB to UART, parallel
port, and common synchronous serial communication interfaces (I2C, SPI).
The chip is manufactured by the company [Qinheng Microelectronics](https://wch-ic.com/).

The ch341 driver shipped with this library is a Python interface to CH341’s
official DLLs.

You need the driver DLL files, which are downloadable from Qinheng’s website.

Windows: [https://www.wch-ic.com/downloads/CH341PAR_ZIP.html](https://www.wch-ic.com/downloads/CH341PAR_ZIP.html)

On Windows it’s recommended to place them
under Windows System32 folder. Or if you place them under a different directory,
you can add that directory to PATH environment variable.

Linux: [https://www.wch-ic.com/downloads/CH341PAR_LINUX_ZIP.html](https://www.wch-ic.com/downloads/CH341PAR_LINUX_ZIP.html)

On Linux you need to build the kernel module from source under the downloaded
zipball’s driver sub-directory like,

```bash
$ cd driver
$ sudo make && sudo make install
```

Also you need to either place the libch347.so file for your platform to system
supported path like /usr/local/lib, or you make the so file loadable by adding
its directory to LD_LIBRARY_PATH environment variable.

MacOS: [https://www.wch-ic.com/download/CH341SER_MAC_ZIP.html](https://www.wch-ic.com/download/CH341SER_MAC_ZIP.html)

I don’t use this library on Mac myself. But let me know if it does not work, and
I can give it a try on Mac.

Example usage:

```python
from i2cpy import I2C

i2c = I2C(driver="ch341")                       # explicitly specify driver

i2c = I2C(0, driver="ch341")                    # override usb id on Windows

i2c = I2C("/dev/ch34x_pis0", driver="ch341")    # override usb device on Linux
```
