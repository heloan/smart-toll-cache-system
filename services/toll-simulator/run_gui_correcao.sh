#!/bin/bash
# Script para iniciar o simulador de correções com interface gráfica

cd "$(dirname "$0")"

# Usar python do ambiente virtual se existir, senão python3 do sistema
if [ -f "venv/bin/python3" ]; then
    exec venv/bin/python3 gui_correcao.py
else
    exec python3 gui_correcao.py
fi
