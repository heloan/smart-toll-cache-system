#!/bin/bash
# Script para iniciar o simulador com interface gráfica

cd "$(dirname "$0")"

# Ativar ambiente virtual se existir
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Executar interface gráfica
python3 gui.py
