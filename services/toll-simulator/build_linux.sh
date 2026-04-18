#!/bin/bash
# Script para gerar executável no Linux

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== Gerando Executável do Simulador de Pedágio ==="
echo ""

# Criar ambiente virtual se não existir
if [ ! -d "venv" ]; then
    echo "Criando ambiente virtual..."
    python3 -m venv venv
fi

# Ativar ambiente virtual
echo "Ativando ambiente virtual..."
source venv/bin/activate

# Instalar dependências + PyInstaller
echo "Instalando dependências..."
pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

# Limpar builds anteriores
echo "Limpando builds anteriores..."
rm -rf build dist *.spec

# Gerar executável
echo "Gerando executável..."
pyinstaller --name="Simulador-Pedagio" \
    --onefile \
    --windowed \
    --add-data="config.py:." \
    --add-data=".env:." \
    --icon=none \
    --hidden-import=tkinter \
    --hidden-import=kafka \
    --hidden-import=faker \
    gui.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Executável gerado com sucesso!"
    echo "  Localização: dist/Simulador-Pedagio"
    echo ""
    echo "Para executar:"
    echo "  ./dist/Simulador-Pedagio"
else
    echo ""
    echo "✗ Erro ao gerar executável"
    exit 1
fi
