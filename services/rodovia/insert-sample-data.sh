#!/bin/bash

# Script para inserir dados de simulação via API REST

BASE_URL="http://localhost:9080/api"

echo "======================================"
echo "  Inserindo Dados de Simulação"
echo "======================================"
echo ""

# Cores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Função para fazer POST
post_data() {
    local endpoint=$1
    local data=$2
    local description=$3
    
    echo -e "${BLUE}${description}...${NC}"
    response=$(curl -s -w "\nHTTP_CODE:%{http_code}" -X POST "${BASE_URL}${endpoint}" \
      -H "Content-Type: application/json" \
      -d "${data}")
    
    http_code=$(echo "$response" | grep "HTTP_CODE:" | cut -d: -f2)
    body=$(echo "$response" | sed '/HTTP_CODE:/d')
    
    if [ "$http_code" -ge 200 ] && [ "$http_code" -lt 300 ]; then
        echo -e "${GREEN}✓ Sucesso (HTTP ${http_code})${NC}"
        echo "$body"
    else
        echo -e "${RED}✗ Erro (HTTP ${http_code})${NC}"
        echo "$body"
    fi
    echo ""
    sleep 0.5
}

echo -e "${YELLOW}=== 1. Criando Concessionárias ===${NC}"
echo ""

post_data "/concessionarias" '{
  "nomeFantasia": "Via Sul",
  "razaoSocial": "Via Sul Concessionária S.A.",
  "cnpj": "12345678000190",
  "contratoConcessao": "CONTRATO-001/2020",
  "dataInicioContrato": "2020-01-01",
  "dataFimContrato": "2050-12-31"
}' "Criando Concessionária Via Sul"

post_data "/concessionarias" '{
  "nomeFantasia": "Rodoeste",
  "razaoSocial": "Rodoeste Rodovias S.A.",
  "cnpj": "98765432000110",
  "contratoConcessao": "CONTRATO-002/2019",
  "dataInicioContrato": "2019-06-01",
  "dataFimContrato": "2049-05-31"
}' "Criando Concessionária Rodoeste"

post_data "/concessionarias" '{
  "nomeFantasia": "AutoBan",
  "razaoSocial": "AutoBan Concessionária de Rodovias S.A.",
  "cnpj": "11222333000144",
  "contratoConcessao": "CONTRATO-003/2021",
  "dataInicioContrato": "2021-03-15",
  "dataFimContrato": "2051-03-14"
}' "Criando Concessionária AutoBan"

echo -e "${YELLOW}=== 2. Criando Rodovias ===${NC}"
echo ""

post_data "/rodovias" '{
  "concessionariaId": 1,
  "codigo": "SP-348",
  "nome": "Rodovia dos Bandeirantes",
  "uf": "SP",
  "extensaoKm": 172.0
}' "Criando Rodovia dos Bandeirantes (SP-348)"

post_data "/rodovias" '{
  "concessionariaId": 2,
  "codigo": "BR-116",
  "nome": "Rodovia Presidente Dutra",
  "uf": "SP",
  "extensaoKm": 402.0
}' "Criando Rodovia Presidente Dutra (BR-116)"

post_data "/rodovias" '{
  "concessionariaId": 3,
  "codigo": "SP-330",
  "nome": "Rodovia Anhanguera",
  "uf": "SP",
  "extensaoKm": 320.0
}' "Criando Rodovia Anhanguera (SP-330)"

echo -e "${YELLOW}=== 3. Criando Praças de Pedágio ===${NC}"
echo ""

post_data "/pracas" '{
  "rodoviaId": 1,
  "nome": "Praça de Pedágio Jundiaí",
  "km": 45.5,
  "sentido": "NORTE"
}' "Criando Praça Jundiaí (SP-348)"

post_data "/pracas" '{
  "rodoviaId": 1,
  "nome": "Praça de Pedágio Campinas",
  "km": 92.3,
  "sentido": "NORTE"
}' "Criando Praça Campinas (SP-348)"

post_data "/pracas" '{
  "rodoviaId": 2,
  "nome": "Praça de Pedágio Guararema",
  "km": 67.8,
  "sentido": "SUL"
}' "Criando Praça Guararema (BR-116)"

post_data "/pracas" '{
  "rodoviaId": 3,
  "nome": "Praça de Pedágio Limeira",
  "km": 145.2,
  "sentido": "NORTE"
}' "Criando Praça Limeira (SP-330)"

echo -e "${YELLOW}=== 4. Criando Pistas de Pedágio ===${NC}"
echo ""

# Praça Jundiaí (ID 1) - 4 pistas
post_data "/pistas" '{
  "pracaId": 1,
  "numeroPista": 1,
  "tipoPista": "AUTOMATICA"
}' "Criando Pista 1 (Automática) - Jundiaí"

post_data "/pistas" '{
  "pracaId": 1,
  "numeroPista": 2,
  "tipoPista": "AUTOMATICA"
}' "Criando Pista 2 (Automática) - Jundiaí"

post_data "/pistas" '{
  "pracaId": 1,
  "numeroPista": 3,
  "tipoPista": "MANUAL"
}' "Criando Pista 3 (Manual) - Jundiaí"

post_data "/pistas" '{
  "pracaId": 1,
  "numeroPista": 4,
  "tipoPista": "MANUAL"
}' "Criando Pista 4 (Manual) - Jundiaí"

# Praça Campinas (ID 2) - 3 pistas
post_data "/pistas" '{
  "pracaId": 2,
  "numeroPista": 1,
  "tipoPista": "AUTOMATICA"
}' "Criando Pista 1 (Automática) - Campinas"

post_data "/pistas" '{
  "pracaId": 2,
  "numeroPista": 2,
  "tipoPista": "MANUAL"
}' "Criando Pista 2 (Manual) - Campinas"

post_data "/pistas" '{
  "pracaId": 2,
  "numeroPista": 3,
  "tipoPista": "MANUAL"
}' "Criando Pista 3 (Manual) - Campinas"

# Praça Guararema (ID 3) - 2 pistas
post_data "/pistas" '{
  "pracaId": 3,
  "numeroPista": 1,
  "tipoPista": "AUTOMATICA"
}' "Criando Pista 1 (Automática) - Guararema"

post_data "/pistas" '{
  "pracaId": 3,
  "numeroPista": 2,
  "tipoPista": "MANUAL"
}' "Criando Pista 2 (Manual) - Guararema"

# Praça Limeira (ID 4) - 3 pistas
post_data "/pistas" '{
  "pracaId": 4,
  "numeroPista": 1,
  "tipoPista": "AUTOMATICA"
}' "Criando Pista 1 (Automática) - Limeira"

post_data "/pistas" '{
  "pracaId": 4,
  "numeroPista": 2,
  "tipoPista": "AUTOMATICA"
}' "Criando Pista 2 (Automática) - Limeira"

post_data "/pistas" '{
  "pracaId": 4,
  "numeroPista": 3,
  "tipoPista": "MANUAL"
}' "Criando Pista 3 (Manual) - Limeira"

echo -e "${YELLOW}=== 5. Criando Tarifas ===${NC}"
echo ""

# Tarifas globais por tipo de veículo
post_data "/tarifas" '{
  "tipoVeiculo": "MOTO",
  "valor": 4.20,
  "vigenciaInicio": "2026-01-01",
  "vigenciaFim": "2026-12-31"
}' "Criando Tarifa MOTO"

post_data "/tarifas" '{
  "tipoVeiculo": "CARRO",
  "valor": 8.40,
  "vigenciaInicio": "2026-01-01",
  "vigenciaFim": "2026-12-31"
}' "Criando Tarifa CARRO"

post_data "/tarifas" '{
  "tipoVeiculo": "CAMINHAO",
  "valor": 25.20,
  "vigenciaInicio": "2026-01-01",
  "vigenciaFim": "2026-12-31"
}' "Criando Tarifa CAMINHAO"

echo ""
echo -e "${GREEN}======================================"
echo "  Dados de Simulação Inseridos!"
echo "======================================${NC}"
echo ""
echo "Resumo:"
echo "  - 3 Concessionárias"
echo "  - 3 Rodovias"
echo "  - 4 Praças de Pedágio"
echo "  - 12 Pistas"
echo "  - 3 Tarifas (por tipo de veículo)"
echo ""
echo "Agora você pode testar o Kafka com:"
echo "  ./test-kafka.sh"
