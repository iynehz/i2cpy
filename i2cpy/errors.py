class I2CError(Exception):
    """Base exception for errors raised from i2cpy."""


class I2CInvalidDriverError(I2CError):
    def __init__(self, driver_name: str):
        self.driver_name = driver_name.lower()
        msg = "Cannot load i2cpy dirver: '{}'".format(self.driver_name)
        super().__init__(msg)


class I2COperationFailedError(I2CError):
    pass


class I2CMemoryAddressSizeError(I2CError):
    def __init__(self, addrsize):
        msg = "Bad I2C memory address size: {}".format(addrsize)
        super().__init__(msg)
