@echo off
@chcp 65001
title build TagPDF
cd /d %~dp0

if exist dist RMDIR /S /Q dist

if not exist .venv (
    uv venv
)
uv sync --default-index https://mirrors.aliyun.com/pypi/simple/

uv run pyinstaller main.spec

if exist dist start dist
pause
