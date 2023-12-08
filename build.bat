@echo off
setlocal EnableDelayedExpansion

title build TagPDF
cd /d %~dp0
if exist dist RMDIR /S /Q dist
if exist venv (
    call venv/scripts/activate
) else (
    python -m venv venv --clear
    call venv/scripts/activate
    python -m pip install -U pip
    pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
)

pyinstaller main.spec
if exist dist start dist
pause
