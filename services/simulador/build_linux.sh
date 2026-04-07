#!/bin/bash
# Script para gerar executável no Linux

echo "=== Gerando Executável do Simulador de Pedágio ==="
echo ""

# Ativar ambiente virtual se existir
if [ -d "venv" ]; then
    echo "Ativando ambiente virtual..."
    source venv/bin/activate
fi

# Instalar PyInstaller se necessário
echo "Verificando PyInstaller..."
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
