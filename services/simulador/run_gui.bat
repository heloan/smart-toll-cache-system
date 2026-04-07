@echo off
REM Script para iniciar o simulador com interface gráfica

cd /d "%~dp0"

REM Ativar ambiente virtual se existir
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

REM Executar interface gráfica
python gui.py
pause
