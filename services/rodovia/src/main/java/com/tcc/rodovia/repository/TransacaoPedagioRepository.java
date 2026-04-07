package com.tcc.rodovia.repository;

import java.time.LocalDateTime;
import java.util.List;

import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import com.tcc.rodovia.entity.TransacaoPedagio;
import com.tcc.rodovia.enums.StatusTransacaoEnum;

@Repository
public interface TransacaoPedagioRepository extends JpaRepository<TransacaoPedagio, Long> {
    
    // Buscar transações com ocorrências criadas após determinada data
    @Query("SELECT DISTINCT t FROM TransacaoPedagio t " +
           "LEFT JOIN FETCH t.ocorrencias o " +
           "LEFT JOIN FETCH t.praca " +
           "LEFT JOIN FETCH t.pista " +
           "LEFT JOIN FETCH t.tarifa " +
           "WHERE o.criadoEm >= :dataInicio " +
           "ORDER BY t.criadoEm DESC")
    List<TransacaoPedagio> findTransacoesComOcorrenciasRecentes(
            @Param("dataInicio") LocalDateTime dataInicio, 
            Pageable pageable);
    
    // Buscar transações com ocorrências sem correção
    @Query("SELECT DISTINCT t FROM TransacaoPedagio t " +
           "JOIN FETCH t.ocorrencias o " +
           "LEFT JOIN FETCH t.praca " +
           "LEFT JOIN FETCH t.pista " +
           "LEFT JOIN FETCH t.tarifa " +
           "WHERE t.statusTransacao = :status " +
           "AND NOT EXISTS (SELECT 1 FROM CorrecaoTransacao c WHERE c.transacao = t) " +
           "ORDER BY o.criadoEm DESC")
    List<TransacaoPedagio> findTransacoesComOcorrenciasSemCorrecao(
            @Param("status") StatusTransacaoEnum status, 
            Pageable pageable);
    
    // Buscar todas as transações com paginação
    @Query("SELECT t FROM TransacaoPedagio t " +
           "LEFT JOIN FETCH t.praca " +
           "LEFT JOIN FETCH t.pista " +
           "LEFT JOIN FETCH t.tarifa " +
           "ORDER BY t.criadoEm DESC")
    List<TransacaoPedagio> findAllWithRelations(Pageable pageable);
    
    // Buscar transações por status
    List<TransacaoPedagio> findByStatusTransacao(StatusTransacaoEnum status);
    
    // Buscar transações por período
    List<TransacaoPedagio> findByDataHoraPassagemBetween(LocalDateTime inicio, LocalDateTime fim);
}
