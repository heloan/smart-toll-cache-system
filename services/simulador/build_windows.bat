@echo off
REM Script para gerar executável no Windows

echo === Gerando Executavel do Simulador de Pedagio ===
echo.

REM Ativar ambiente virtual se existir
if exist venv\Scripts\activate.bat (
    echo Ativando ambiente virtual...
    call venv\Scripts\activate.bat
)

REM Instalar PyInstaller se necessário
echo Verificando PyInstaller...
pip install pyinstaller

REM Limpar builds anteriores
echo Limpando builds anteriores...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
del /q *.spec 2>nul

REM Gerar executável
echo Gerando executavel...
pyinstaller --name="Simulador-Pedagio" ^
    --onefile ^
    --windowed ^
    --add-data="config.py;." ^
    --add-data=".env;." ^
    --icon=none ^
    --hidden-import=tkinter ^
    --hidden-import=kafka ^
    --hidden-import=faker ^
    gui.py

if %errorlevel% equ 0 (
    echo.
    echo [OK] Executavel gerado com sucesso!
    echo   Localizacao: dist\Simulador-Pedagio.exe
    echo.
    echo Para executar:
    echo   dist\Simulador-Pedagio.exe
) else (
    echo.
    echo [ERRO] Erro ao gerar executavel
    exit /b 1
)
