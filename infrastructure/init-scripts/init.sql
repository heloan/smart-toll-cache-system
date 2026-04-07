-- Smart Toll Cache System — Database Initialization Script
-- PostgreSQL 14

-- ============================================
-- Table: praca (Toll Plaza)
-- ============================================
CREATE TABLE IF NOT EXISTS praca (
    id          BIGSERIAL PRIMARY KEY,
    nome        VARCHAR(255) NOT NULL,
    rodovia     VARCHAR(100) NOT NULL,
    km          DECIMAL(10, 2),
    uf          CHAR(2) NOT NULL,
    created_at  TIMESTAMP DEFAULT NOW(),
    updated_at  TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_praca_uf ON praca(uf);

-- ============================================
-- Table: pista (Toll Lane)
-- ============================================
CREATE TABLE IF NOT EXISTS pista (
    id          BIGSERIAL PRIMARY KEY,
    numero      INTEGER NOT NULL,
    tipo        VARCHAR(50) NOT NULL,
    status      VARCHAR(20) NOT NULL DEFAULT 'ATIVA',
    praca_id    BIGINT NOT NULL REFERENCES praca(id),
    created_at  TIMESTAMP DEFAULT NOW(),
    updated_at  TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_pista_praca_id ON pista(praca_id);
CREATE INDEX IF NOT EXISTS idx_pista_status ON pista(status);

-- ============================================
-- Table: transacao (Transaction)
-- ============================================
CREATE TABLE IF NOT EXISTS transacao (
    id          BIGSERIAL PRIMARY KEY,
    tipo        VARCHAR(50) NOT NULL,
    status      VARCHAR(20) NOT NULL DEFAULT 'PENDENTE',
    valor       DECIMAL(10, 2) NOT NULL,
    placa       VARCHAR(10),
    tag         VARCHAR(50),
    data_hora   TIMESTAMP NOT NULL,
    corrigida   BOOLEAN DEFAULT FALSE,
    pista_id    BIGINT NOT NULL REFERENCES pista(id),
    created_at  TIMESTAMP DEFAULT NOW(),
    updated_at  TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_transacao_pista_id ON transacao(pista_id);
CREATE INDEX IF NOT EXISTS idx_transacao_status ON transacao(status);
CREATE INDEX IF NOT EXISTS idx_transacao_data_hora ON transacao(data_hora);
CREATE INDEX IF NOT EXISTS idx_transacao_placa ON transacao(placa);
CREATE INDEX IF NOT EXISTS idx_transacao_tag ON transacao(tag);

-- ============================================
-- Seed Data (optional sample data for development)
-- ============================================

-- Sample toll plazas
-- INSERT INTO praca (nome, rodovia, km, uf) VALUES ('Praca Norte', 'BR-101', 45.5, 'SP');
-- INSERT INTO praca (nome, rodovia, km, uf) VALUES ('Praca Sul', 'BR-101', 120.0, 'RJ');

-- Sample lanes
-- INSERT INTO pista (numero, tipo, status, praca_id) VALUES (1, 'AUTOMATICA', 'ATIVA', 1);
-- INSERT INTO pista (numero, tipo, status, praca_id) VALUES (2, 'MANUAL', 'ATIVA', 1);

-- Sample transactions
-- INSERT INTO transacao (tipo, status, valor, placa, tag, data_hora, pista_id)
-- VALUES ('NORMAL', 'PENDENTE', 12.50, 'ABC1234', 'TAG001', NOW(), 1);
