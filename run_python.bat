@echo off
setlocal enabledelayedexpansion
set DISK=%1


REM === Construir los parámetros dinámicamente ignorando los "" ===
set "PY_ARGS="
if "%~2" NEQ "" set "PY_ARGS=!PY_ARGS! %2"
if "%~3" NEQ "" set "PY_ARGS=!PY_ARGS! %3"
if "%~4" NEQ "" set "PY_ARGS=!PY_ARGS! %4"
if "%~5" NEQ "" set "PY_ARGS=!PY_ARGS! %5"
if "%~6" NEQ "" set "PY_ARGS=!PY_ARGS! %6"


REM === (1) Forzar UTF-8 en consola/IO ===
chcp 65001 >nul
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"


REM === (2) Rutas (ruta fija) ===
set "PROJECT_DIR=%DISK%:\Proyectos\analisis-comercial-efectividad"
set "LOG_DIR=%PROJECT_DIR%\logs"
set "OUTFILE=%LOG_DIR%\py_out_logs.txt"
set "ERRFILE=%LOG_DIR%\logs.txt"


REM === (3) Empezar siempre en blanco ===
type nul > "%OUTFILE%"
type nul > "%ERRFILE%"


REM === (4) Carpeta de trabajo ===
cd /d "%PROJECT_DIR%"


REM === (5) Ejecutar Python ===
"%PROJECT_DIR%\venv\Scripts\python.exe" ".\src\main.py" !PY_ARGS! 1>"%OUTFILE%" 2>"%ERRFILE%"


REM === (6) Propagar el exit code a Power Automate ===
exit /b %ERRORLEVEL%
