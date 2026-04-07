-- Smart Toll Cache System — Database Initialization Script
-- PostgreSQL 15 — Matches rodovia JPA entity model

-- ============================================
-- Table: concessionaria
-- ============================================
CREATE TABLE IF NOT EXISTS concessionaria (
    id                   BIGSERIAL PRIMARY KEY,
    nome_fantasia        VARCHAR(120) NOT NULL,
    razao_social         VARCHAR(160) NOT NULL,
    cnpj                 VARCHAR(14) NOT NULL UNIQUE,
    contrato_concessao   VARCHAR(60),
    data_inicio_contrato DATE NOT NULL,
    data_fim_contrato    DATE,
    ativo                BOOLEAN NOT NULL DEFAULT TRUE,
    criado_em            TIMESTAMP NOT NULL DEFAULT NOW()
);

-- ============================================
-- Table: rodovia
-- ============================================
CREATE TABLE IF NOT EXISTS rodovia (
    id                BIGSERIAL PRIMARY KEY,
    concessionaria_id BIGINT NOT NULL REFERENCES concessionaria(id),
    codigo            VARCHAR(20) NOT NULL,
    nome              VARCHAR(120),
    uf                VARCHAR(2) NOT NULL,
    extensao_km       DECIMAL(8, 2),
    ativa             BOOLEAN NOT NULL DEFAULT TRUE,
    criado_em         TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_rodovia_concessionaria ON rodovia(concessionaria_id);
CREATE INDEX IF NOT EXISTS idx_rodovia_uf ON rodovia(uf);

-- ============================================
-- Table: praca_pedagio (Toll Plaza)
-- ============================================
CREATE TABLE IF NOT EXISTS praca_pedagio (
    id          BIGSERIAL PRIMARY KEY,
    rodovia_id  BIGINT NOT NULL REFERENCES rodovia(id),
    nome        VARCHAR(120),
    km          DECIMAL(8, 3) NOT NULL,
    sentido     VARCHAR(20),
    ativa       BOOLEAN NOT NULL DEFAULT TRUE,
    criado_em   TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_praca_rodovia ON praca_pedagio(rodovia_id);

-- ============================================
-- Table: pista_pedagio (Toll Lane)
-- ============================================
CREATE TABLE IF NOT EXISTS pista_pedagio (
    id            BIGSERIAL PRIMARY KEY,
    praca_id      BIGINT NOT NULL REFERENCES praca_pedagio(id),
    numero_pista  INTEGER NOT NULL,
    tipo_pista    VARCHAR(20) NOT NULL,   -- MANUAL, TAG, MISTA
    sentido       VARCHAR(20),
    ativa         BOOLEAN NOT NULL DEFAULT TRUE,
    criado_em     TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT uk_praca_pista UNIQUE (praca_id, numero_pista)
);

CREATE INDEX IF NOT EXISTS idx_pista_praca ON pista_pedagio(praca_id);

-- ============================================
-- Table: tarifa_pedagio (Toll Rate)
-- ============================================
CREATE TABLE IF NOT EXISTS tarifa_pedagio (
    id               BIGSERIAL PRIMARY KEY,
    tipo_veiculo     VARCHAR(20) NOT NULL,   -- MOTO, CARRO, CAMINHAO
    valor            DECIMAL(10, 2) NOT NULL,
    vigencia_inicio  DATE NOT NULL,
    vigencia_fim     DATE,
    criado_em        TIMESTAMP NOT NULL DEFAULT NOW()
);

-- ============================================
-- Table: operador (Operator)
-- ============================================
CREATE TABLE IF NOT EXISTS operador (
    id              BIGSERIAL PRIMARY KEY,
    username        VARCHAR(50) NOT NULL UNIQUE,
    password        VARCHAR(255) NOT NULL,
    nome_completo   VARCHAR(100) NOT NULL,
    email           VARCHAR(100) NOT NULL UNIQUE,
    telefone        VARCHAR(20),
    ativo           BOOLEAN NOT NULL DEFAULT TRUE,
    criado_em       TIMESTAMP NOT NULL DEFAULT NOW(),
    atualizado_em   TIMESTAMP
);

-- ============================================
-- Table: transacao_pedagio (Toll Transaction)
-- ============================================
CREATE TABLE IF NOT EXISTS transacao_pedagio (
    id                  BIGSERIAL PRIMARY KEY,
    praca_id            BIGINT NOT NULL REFERENCES praca_pedagio(id),
    pista_id            BIGINT NOT NULL REFERENCES pista_pedagio(id),
    tarifa_id           BIGINT NOT NULL REFERENCES tarifa_pedagio(id),
    data_hora_passagem  TIMESTAMP NOT NULL,
    placa               VARCHAR(10) NOT NULL,
    tag_id              VARCHAR(40),
    tipo_veiculo        VARCHAR(20) NOT NULL,   -- MOTO, CARRO, CAMINHAO
    valor_original      DECIMAL(10, 2) NOT NULL,
    status_transacao    VARCHAR(20) NOT NULL,    -- OK, OCORRENCIA, CORRIGIDA
    hash_integridade    VARCHAR(128) NOT NULL,
    criado_em           TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_transacao_praca ON transacao_pedagio(praca_id);
CREATE INDEX IF NOT EXISTS idx_transacao_pista ON transacao_pedagio(pista_id);
CREATE INDEX IF NOT EXISTS idx_transacao_tarifa ON transacao_pedagio(tarifa_id);
CREATE INDEX IF NOT EXISTS idx_transacao_status ON transacao_pedagio(status_transacao);
CREATE INDEX IF NOT EXISTS idx_transacao_placa ON transacao_pedagio(placa);
CREATE INDEX IF NOT EXISTS idx_transacao_data ON transacao_pedagio(data_hora_passagem);

-- ============================================
-- Table: ocorrencia_transacao (Transaction Occurrence / Issue)
-- ============================================
CREATE TABLE IF NOT EXISTS ocorrencia_transacao (
    id                        BIGSERIAL PRIMARY KEY,
    transacao_id              BIGINT NOT NULL REFERENCES transacao_pedagio(id),
    tipo_ocorrencia           VARCHAR(30) NOT NULL,   -- EVASAO, TAG_BLOQUEADA, SEM_SALDO, FALHA_LEITURA
    observacao                TEXT,
    detectada_automaticamente BOOLEAN NOT NULL DEFAULT TRUE,
    criado_em                 TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_ocorrencia_transacao ON ocorrencia_transacao(transacao_id);

-- ============================================
-- Table: correcao_transacao (Transaction Correction)
-- ============================================
CREATE TABLE IF NOT EXISTS correcao_transacao (
    id               BIGSERIAL PRIMARY KEY,
    transacao_id     BIGINT NOT NULL REFERENCES transacao_pedagio(id),
    operador_id      BIGINT NOT NULL REFERENCES operador(id),
    motivo           TEXT NOT NULL,
    valor_anterior   DECIMAL(10, 2) NOT NULL,
    valor_corrigido  DECIMAL(10, 2) NOT NULL,
    tipo_correcao    VARCHAR(20) NOT NULL,   -- MANUAL, AUTOMATICA
    criado_em        TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_correcao_transacao ON correcao_transacao(transacao_id);
CREATE INDEX IF NOT EXISTS idx_correcao_operador ON correcao_transacao(operador_id);

-- ============================================
-- Table: registro_performance (Performance Metrics)
-- ============================================
CREATE TABLE IF NOT EXISTS registro_performance (
    id                      BIGSERIAL PRIMARY KEY,
    endpoint                VARCHAR(255) NOT NULL,
    metodo_http             VARCHAR(10) NOT NULL,
    tempo_processamento_ms  BIGINT NOT NULL,
    memoria_usada_mb        DOUBLE PRECISION NOT NULL,
    memoria_livre_mb        DOUBLE PRECISION NOT NULL,
    memoria_total_mb        DOUBLE PRECISION NOT NULL,
    uso_cpu_processo        DOUBLE PRECISION NOT NULL,
    threads_ativas          INTEGER NOT NULL,
    status_http             INTEGER NOT NULL,
    ip_cliente              VARCHAR(45),
    user_agent              VARCHAR(255),
    parametros              TEXT,
    erro                    TEXT,
    origem_dados            VARCHAR(20),   -- BANCO_DADOS, CACHE_LOCAL, CACHE_REDIS, NAO_APLICAVEL
    criado_em               TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_performance_endpoint ON registro_performance(endpoint);
CREATE INDEX IF NOT EXISTS idx_performance_criado ON registro_performance(criado_em);

-- ============================================
-- Seed Data (sample data for development)
-- ============================================

-- Concessionaria
INSERT INTO concessionaria (nome_fantasia, razao_social, cnpj, contrato_concessao, data_inicio_contrato) VALUES
    ('AutoPista SP', 'AutoPista Concessionária S.A.', '12345678000190', 'CONC-2020-001', '2020-01-01');

-- Rodovia
INSERT INTO rodovia (concessionaria_id, codigo, nome, uf, extensao_km) VALUES
    (1, 'BR-101', 'Rodovia Rio-Santos', 'SP', 210.50);

-- Pracas de pedagio
INSERT INTO praca_pedagio (rodovia_id, nome, km, sentido) VALUES
    (1, 'Praça Norte', 45.500, 'NORTE'),
    (1, 'Praça Sul', 120.000, 'SUL'),
    (1, 'Praça Centro', 85.200, 'AMBOS');

-- Pistas de pedagio
INSERT INTO pista_pedagio (praca_id, numero_pista, tipo_pista, sentido) VALUES
    (1, 1, 'TAG',    'NORTE'),
    (1, 2, 'MISTA',  'NORTE'),
    (1, 3, 'MANUAL', 'NORTE'),
    (2, 1, 'TAG',    'SUL'),
    (2, 2, 'MISTA',  'SUL'),
    (3, 1, 'TAG',    'AMBOS');

-- Tarifas de pedagio
INSERT INTO tarifa_pedagio (tipo_veiculo, valor, vigencia_inicio) VALUES
    ('MOTO',     5.00,  '2024-01-01'),
    ('CARRO',   10.00,  '2024-01-01'),
    ('CAMINHAO', 20.00, '2024-01-01');

-- Operador
INSERT INTO operador (username, password, nome_completo, email, ativo) VALUES
    ('admin', '$2a$10$placeholder', 'Administrador', 'admin@smarttoll.com', TRUE);
