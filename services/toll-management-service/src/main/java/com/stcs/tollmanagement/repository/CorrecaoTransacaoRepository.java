package com.stcs.tollmanagement.repository;

import java.time.LocalDateTime;
import java.util.List;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import com.stcs.tollmanagement.entity.CorrecaoTransacao;
import com.stcs.tollmanagement.enums.TipoCorrecaoEnum;

@Repository
public interface CorrecaoTransacaoRepository extends JpaRepository<CorrecaoTransacao, Long> {
    
    @Query("SELECT c FROM CorrecaoTransacao c " +
           "JOIN FETCH c.transacao " +
           "JOIN FETCH c.operador " +
           "ORDER BY c.criadoEm DESC")
    List<CorrecaoTransacao> findAllWithRelations();
    
    List<CorrecaoTransacao> findByTipoCorrecao(TipoCorrecaoEnum tipoCorrecao);
    
    List<CorrecaoTransacao> findByCriadoEmBetween(LocalDateTime inicio, LocalDateTime fim);
    
    @Query("SELECT c FROM CorrecaoTransacao c WHERE c.operador.id = :operadorId ORDER BY c.criadoEm DESC")
    List<CorrecaoTransacao> findByOperadorId(Long operadorId);
}
