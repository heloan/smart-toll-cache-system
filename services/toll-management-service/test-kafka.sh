#!/bin/bash

# Script para testar a API de transações com Kafka

BASE_URL="http://localhost:9080/api/transacoes"

echo "======================================"
echo "  Teste de Mensageria com Kafka"
echo "======================================"
echo ""

# Cores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Função para enviar transação
enviar_transacao() {
    local endpoint=$1
    local placa=$2
    local tipo=$3
    
    echo -e "${BLUE}Enviando transação para ${endpoint}...${NC}"
    echo -e "Placa: ${YELLOW}${placa}${NC}"
    
    # Buscar IDs disponíveis dinamicamente
    praca_id=$(curl -s http://localhost:9080/api/pracas | jq -r '.[0].id' 2>/dev/null)
    pista_id=$(curl -s "http://localhost:9080/api/pistas?pracaId=$praca_id" 2>/dev/null | jq -r '.[0].id' 2>/dev/null)
    
    # Se não conseguir buscar, usa IDs padrão
    if [ -z "$praca_id" ] || [ "$praca_id" = "null" ]; then
        praca_id=1
    fi
    if [ -z "$pista_id" ] || [ "$pista_id" = "null" ]; then
        pista_id=1
    fi
    
    response=$(curl -s -w "\nHTTP_CODE:%{http_code}" -X POST "${BASE_URL}${endpoint}" \
      -H "Content-Type: application/json" \
      -d "{
        \"pracaId\": $praca_id,
        \"pistaId\": $pista_id,
        \"dataHoraPassagem\": \"$(date -u +"%Y-%m-%dT%H:%M:%S")\",
        \"placa\": \"${placa}\",
        \"tagId\": \"TAG${RANDOM}\",
        \"tipoVeiculo\": \"${tipo}\",
        \"valorOriginal\": 8.50,
        \"statusTransacao\": \"OK\",
        \"hashIntegridade\": \"hash_$(date +%s)\"
      }")
    
    http_code=$(echo "$response" | grep "HTTP_CODE:" | cut -d: -f2)
    body=$(echo "$response" | sed '/HTTP_CODE:/d')
    
    echo -e "${GREEN}Resposta (HTTP ${http_code}):${NC}"
    echo "$body"
    echo ""
}

# Menu interativo
echo "Escolha uma opção:"
echo "1. Enviar transação assíncrona (recomendado)"
echo "2. Enviar transação síncrona"
echo "3. Enviar múltiplas transações (teste de carga)"
echo "4. Verificar tópicos Kafka"
echo "5. Monitorar consumer group"
echo "6. Consumir mensagens do Kafka (debug)"
echo "7. Listar transações processadas"
echo ""
read -p "Opção: " opcao

case $opcao in
    1)
        echo ""
        enviar_transacao "" "ABC1D23" "CARRO"
        ;;
    
    2)
        echo ""
        enviar_transacao "/sync" "XYZ9W88" "CAMINHAO"
        ;;
    
    3)
        read -p "Quantas transações deseja enviar? " quantidade
        echo ""
        for i in $(seq 1 $quantidade); do
            placa="TST$(printf "%04d" $i)"
            enviar_transacao "" "$placa" "CARRO"
            sleep 0.1
        done
        echo -e "${GREEN}${quantidade} transações enviadas!${NC}"
        ;;
    
    4)
        echo -e "${BLUE}Listando tópicos Kafka...${NC}"
        docker exec rodovia-kafka kafka-topics \
            --bootstrap-server localhost:9092 \
            --list
        
        echo ""
        echo -e "${BLUE}Detalhes do tópico transacao-pedagio:${NC}"
        docker exec rodovia-kafka kafka-topics \
            --bootstrap-server localhost:9092 \
            --describe \
            --topic transacao-pedagio
        ;;
    
    5)
        echo -e "${BLUE}Monitorando consumer group...${NC}"
        docker exec rodovia-kafka kafka-consumer-groups \
            --bootstrap-server localhost:9092 \
            --describe \
            --group rodovia-transacao-consumer-group
        ;;
    
    6)
        echo -e "${BLUE}Consumindo mensagens (Ctrl+C para parar)...${NC}"
        docker exec -it rodovia-kafka kafka-console-consumer \
            --bootstrap-server localhost:9092 \
            --topic transacao-pedagio \
            --from-beginning
        ;;
    
    7)
        echo -e "${BLUE}Listando últimas 10 transações...${NC}"
        curl -s "${BASE_URL}?limite=10" | jq '.'
        ;;
    
    *)
        echo "Opção inválida!"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}Operação concluída!${NC}"
