package com.tcc.rodovia.util;

import org.springframework.stereotype.Component;
import org.springframework.web.context.request.RequestContextHolder;
import org.springframework.web.context.request.ServletRequestAttributes;

import com.tcc.rodovia.enums.OrigemDadosEnum;
import com.tcc.rodovia.interceptor.PerformanceInterceptor;

import jakarta.servlet.http.HttpServletRequest;

/**
 * Utilitário para marcar a origem dos dados em requisições.
 * Deve ser usado nos serviços para indicar se os dados vieram do banco, cache local ou Redis.
 */
@Component
public class OrigemDadosMarker {

    /**
     * Marca a requisição atual como consultada no banco de dados
     */
    public void marcarBancoDados() {
        marcarOrigem(OrigemDadosEnum.BANCO_DADOS);
    }

    /**
     * Marca a requisição atual como consultada no cache local da aplicação
     */
    public void marcarCacheLocal() {
        marcarOrigem(OrigemDadosEnum.CACHE_LOCAL);
    }

    /**
     * Marca a requisição atual como consultada no cache Redis
     */
    public void marcarCacheRedis() {
        marcarOrigem(OrigemDadosEnum.CACHE_REDIS);
    }

    /**
     * Marca a requisição atual como não aplicável (POST, PUT, DELETE)
     */
    public void marcarNaoAplicavel() {
        marcarOrigem(OrigemDadosEnum.NAO_APLICAVEL);
    }

    private void marcarOrigem(OrigemDadosEnum origem) {
        ServletRequestAttributes attributes = (ServletRequestAttributes) RequestContextHolder.getRequestAttributes();
        if (attributes != null) {
            HttpServletRequest request = attributes.getRequest();
            request.setAttribute(PerformanceInterceptor.ORIGEM_DADOS_ATTRIBUTE, origem);
        }
    }
}
