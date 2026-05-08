@echo off
title build TagPDF
cd /d %~dp0

if exist dist RMDIR /S /Q dist

:: 使用uv创建虚拟环境并同步依赖（基于pyproject.toml + uv.lock）
if not exist .venv (
    uv venv
)
uv sync --default-index https://mirrors.aliyun.com/pypi/simple/

:: 使用PyInstaller打包
uv run pyinstaller main.spec

if exist dist start dist
pause
