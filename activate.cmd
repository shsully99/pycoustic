@echo off
echo Activating pycoustic virtual environment...
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
    echo Virtual environment activated: pycoustic-py3.13
) else (
    echo Error: Virtual environment not found!
    echo Run: poetry install
)