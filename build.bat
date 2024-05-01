@echo on

python -m build

cd docs
call make markdown
copy /Y build\markdown\index.md ..\README.md

