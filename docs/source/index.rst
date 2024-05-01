-------------------------------------------------------------
Python I2C library supporting multiple driver implementations
-------------------------------------------------------------

.. contents::

.. raw:: html

   <div>
      <img src="https://img.shields.io/badge/python-3.7+-blue.svg" alt="python"/>
      <a href="https://img.shields.io/github/license/iynehz/i2cpy.svg">
         <img src="https://img.shields.io/github/license/iynehz/i2cpy.svg" alt="license"/>
      </a>
      <a href="https://img.shields.io/pypi/v/i2cpy.svg">
         <img src="https://img.shields.io/pypi/v/i2cpy.svg" alt="pypi"/>
      </a>
      <img src="https://img.shields.io/badge/code%20style-black-black.svg" alt="Code style: black"/>
      <img src="https://img.shields.io/badge/mypy-checked-green.svg" alt="mypy"/>
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

You need the driver DLL files, which are downloadable from Qinheng's website.

* Windows: `<https://www.wch-ic.com/downloads/CH341PAR_ZIP.html>`_

* Linux: `<https://www.wch-ic.com/downloads/CH341PAR_LINUX_ZIP.html>`_

On Windows it's recommended to place them
under Windows System32 folder. Or if you place them under a different directory,
you can add that directory to `PATH` environment variable.

Example usage:

.. code-block:: python

   from i2cpy import I2C

   i2c = I2C(0, driver="ch341")                    # explicitly specify driver

   # override dll name on Windows
   i2c = I2C(0, driver="ch341", dll="CH341DLL")

   # override dll name on Linux
   i2c = I2C(0, driver="ch341", dll="libch347.so")          # so filename
   i2c = I2C(0, driver="ch341", dll="/path/to/libch347.so") # full so file path
   