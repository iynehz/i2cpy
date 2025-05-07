-------------------------------------------------------------
Python I2C library supporting multiple driver implementations
-------------------------------------------------------------

.. only:: html

   .. contents::


.. raw:: html

   <div>
      <img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="python"/>
      <a href="https://pypi.org/project/i2cpy/"><img src="https://img.shields.io/pypi/v/i2cpy.svg" alt="pypi"/></a>
      <a href="https://github.com/iynehz/i2cpy/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-green" alt="license"/></a>
      <img src="https://readthedocs.org/projects/i2cpy/badge/?version=latest" alt="docs"/>
      <img src="https://github.com/iynehz/i2cpy/actions/workflows/lint.yml/badge.svg" alt="lint"/>
   </div>


Introduction
============

.. automodule:: i2cpy

Installation
============

The i2cpy Python module itself can be simply pip installed,

.. code-block::

   pip intall i2cpy

And for the underlying I2C implementations you still need to install their
corresponding drivers. 

ch341
-----

The CH341 series chip (like CH341A) is USB bus converter which converts USB to UART, parallel
port, and common synchronous serial communication interfaces (I2C, SPI).
The chip is manufactured by the company `Qinheng Microelectronics <https://wch-ic.com/>`_.

The ch341 driver shipped with this library is a Python interface to CH341's
official DLLs.

You need the driver DLL files, which are downloadable from Qinheng's website.

* **Windows**: `<https://www.wch-ic.com/downloads/CH341PAR_EXE.html>`_

  They also have a zipball `<https://www.wch-ic.com/downloads/CH341PAR_ZIP.html>`_ .
  If you use the zipball on Windows it's recommended to place the DLL files,
  CH341DLLA64.DLL and/or CH341DLL.DLL depending on the bitness, under Windows
  System32/SysWOW64 folder. Or if you place them under a different directory,
  you can add that directory to PATH environment variable.

* **Linux**: `<https://www.wch-ic.com/downloads/CH341PAR_LINUX_ZIP.html>`_

  On Linux you need to build the kernel module from source under the downloaded
  zipball's `driver` sub-directory like below.

  .. code-block:: bash

   $ cd driver
   $ sudo rmmod ch34x_pis
   $ make && sudo make install

  Also you need to either place the `libch347.so` file for your platform to system
  supported path like `/usr/local/lib`, or you make the so file loadable by adding
  its directory to `LD_LIBRARY_PATH` environment variable.

  And because Qinheng sometimes updates their Linux driver and breaks backward
  compatibility, be careful when you upgrade their Linux CH341PAR driver version,
  and make sure your effective `libch347.so` file and your compiled kernel module
  come from the same driver version.

  Still on Linux there could be more details like, system package
  `linux-headers-$(uname -r)` being a prerequisite of making the kernel module,
  and permissioning of `/dev/ch34x_pis*`, etc..
  Those are beyond scope of this doc though.

* **macOS** is not supported. See also `this ticket <https://github.com/iynehz/i2cpy/issues/3>`_.

Example usage:

.. code-block:: python

  from i2cpy import I2C

  i2c = I2C()                                     # ch341 is the default driver
  i2c = I2C(driver="ch341")                       # explicitly specify driver

  i2c = I2C(0)                                    # override usb id

  i2c = I2C("/dev/ch34x_pis0")                    # override usb device on Linux
   

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
