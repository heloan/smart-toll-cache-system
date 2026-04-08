package com.stcs.tollmanagement.enums;

public enum OrigemDadosEnum {
    BANCO_DADOS,      // Consulta direta no banco de dados
    CACHE_LOCAL,      // Cache em memória da aplicação
    CACHE_REDIS,      // Cache Redis externo
    NAO_APLICAVEL     // Para requisições que não retornam dados (POST, PUT, DELETE)
}
