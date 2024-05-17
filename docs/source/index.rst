-------------------------------------------------------------
Python I2C library supporting multiple driver implementations
-------------------------------------------------------------

.. only:: html

   .. contents::


.. raw:: html

   <div>
      <img src="https://img.shields.io/badge/python-3.7+-blue.svg" alt="python"/>
      <a href="https://pypi.org/project/i2cpy/"><img src="https://img.shields.io/pypi/v/i2cpy.svg" alt="pypi"/></a>
      <a href="https://github.com/iynehz/i2cpy/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-green" alt="license"/></a>
      <img src="https://readthedocs.org/projects/i2cpy/badge/?version=latest" alt="docs"/>
      <img src="https://github.com/iynehz/i2cpy/actions/workflows/lint.yml/badge.svg" alt="lint"/>
   </div>


Introduction
============

.. automodule:: i2cpy

Class I2C
=========


Constructor
-----------

.. automethod:: i2cpy.I2C.__init__

General methods
---------------

.. automethod:: i2cpy.I2C.init
.. automethod:: i2cpy.I2C.deinit
.. automethod:: i2cpy.I2C.scan


Standard bus operations
-----------------------

.. automethod:: i2cpy.I2C.writeto
.. automethod:: i2cpy.I2C.readfrom

Memory operations
-----------------

.. automethod:: i2cpy.I2C.writeto_mem
.. automethod:: i2cpy.I2C.readfrom_mem
.. automethod:: i2cpy.I2C.readfrom_mem_into


Supported I2C drivers
=====================

ch341
-----

The CH341 series chip (like CH341A) is USB bus converter which converts USB to UART, parallel
port, and common synchronous serial communication interfaces (I2C, SPI).
The chip is manufactured by the company `Qinheng Microelectronics <https://wch-ic.com/>`_.

The ch341 driver shipped with this library is a Python interface to CH341's
official DLLs.

You need the driver DLL files, which are downloadable from Qinheng's website.

Windows: `<https://www.wch-ic.com/downloads/CH341PAR_ZIP.html>`_

On Windows it's recommended to place them
under Windows System32 folder. Or if you place them under a different directory,
you can add that directory to `PATH` environment variable.

Linux: `<https://www.wch-ic.com/downloads/CH341PAR_LINUX_ZIP.html>`_

On Linux you need to build the kernel module from source under the downloaded
zipball's `driver` sub-directory like,

.. code-block:: bash

   $ cd driver
   $ sudo make && sudo make install

Also you need to either place the `libch347.so` file for your platform to system
supported path like `/usr/local/lib`, or you make the so file loadable by adding
its directory to `LD_LIBRARY_PATH` environment variable.

MacOS: `<https://www.wch-ic.com/download/CH341SER_MAC_ZIP.html>`_

I don't use this library on Mac myself. But let me know if it does not work, and
I can give it a try on Mac.

Example usage:

.. code-block:: python

   from i2cpy import I2C

   i2c = I2C(driver="ch341")                       # explicitly specify driver

   i2c = I2C(0, driver="ch341")                    # override usb id on Windows

   i2c = I2C("/dev/ch34x_pis0", driver="ch341")    # override usb device on Linux
   