#!/bin/bash

# Script para limpar dados do banco de dados

BASE_URL="http://localhost:9080/api"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}======================================"
echo "  Limpando Banco de Dados"
echo "======================================${NC}"
echo ""

echo -e "${YELLOW}Buscando e removendo dados existentes...${NC}"

# Função para deletar todos os registros de um endpoint
delete_all() {
    local endpoint=$1
    local entity_name=$2
    
    echo -e "${YELLOW}Removendo $entity_name...${NC}"
    
    # Busca todos os registros
    response=$(curl -s -X GET "$BASE_URL/$endpoint")
    
    # Extrai os IDs usando jq
    ids=$(echo "$response" | jq -r '.[].id' 2>/dev/null)
    
    if [ -z "$ids" ]; then
        echo -e "${GREEN}  Nenhum registro encontrado${NC}"
        return
    fi
    
    # Deleta cada registro
    count=0
    for id in $ids; do
        status=$(curl -s -o /dev/null -w "%{http_code}" -X DELETE "$BASE_URL/$endpoint/$id")
        if [ "$status" = "204" ] || [ "$status" = "200" ]; then
            ((count++))
        fi
    done
    
    echo -e "${GREEN}  $count registros removidos${NC}"
}

# Ordem de remoção respeitando dependências
delete_all "transacoes" "Transações"
delete_all "correcoes" "Correções"
delete_all "pistas" "Pistas"
delete_all "pracas" "Praças"
delete_all "rodovias" "Rodovias"
delete_all "tarifas" "Tarifas"
delete_all "concessionarias" "Concessionárias"
delete_all "operadores" "Operadores"

echo ""
echo -e "${GREEN}======================================"
echo "  Banco de Dados Limpo!"
echo "======================================${NC}"
echo ""
echo "Agora você pode inserir dados novos com:"
echo "  ./insert-sample-data.sh"
