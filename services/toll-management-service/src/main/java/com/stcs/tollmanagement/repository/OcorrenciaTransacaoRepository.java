package com.stcs.tollmanagement.repository;

import java.time.LocalDateTime;
import java.util.List;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import com.stcs.tollmanagement.entity.OcorrenciaTransacao;
import com.stcs.tollmanagement.enums.TipoOcorrenciaEnum;

@Repository
public interface OcorrenciaTransacaoRepository extends JpaRepository<OcorrenciaTransacao, Long> {
    
    @Query("SELECT o FROM OcorrenciaTransacao o " +
           "JOIN FETCH o.transacao " +
           "ORDER BY o.criadoEm DESC")
    List<OcorrenciaTransacao> findAllWithTransacao();
    
    List<OcorrenciaTransacao> findByTipoOcorrencia(TipoOcorrenciaEnum tipoOcorrencia);
    
    List<OcorrenciaTransacao> findByCriadoEmBetween(LocalDateTime inicio, LocalDateTime fim);
    
    @Query("SELECT o FROM OcorrenciaTransacao o WHERE o.transacao.id = :transacaoId ORDER BY o.criadoEm DESC")
    List<OcorrenciaTransacao> findByTransacaoId(Long transacaoId);
}
