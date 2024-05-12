@echo on

rmdir /s/q dist
python -m build

cd docs
call make markdown
copy /Y build\markdown\index.md ..\README.md
cd ..

