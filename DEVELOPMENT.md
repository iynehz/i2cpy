# Development Notes

[tox](https://tox.wiki/) and [pyenv](https://github.com/pyenv/pyenv) are used in
this project to ease testing across multiple Python versions.

Install pyenv, and then install python versions used in tox.ini, via pyenv
for example,

```
pyenv install py3.13
pyenv install py3.11
pyenv install py3.9
```

To run tox and test against the default ch341 driver, simply,

```
tox
```

To test a specific driver, set the I2CPY_DRIVER environment variable.
For example on Windows,

```
set I2CPY_DRIVER=ch347
tox
```
