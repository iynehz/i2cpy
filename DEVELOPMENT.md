# Development Notes

To ease test across multiple python versions, we use [tox](https://tox.wiki/)
and [pyenv](https://github.com/pyenv/pyenv).

Install pyenv, and then install python versions used in tox.ini, via pyenv
for example,

```
pyenv install py3.13
pyenv install py3.11
pyenv install py3.9
```
