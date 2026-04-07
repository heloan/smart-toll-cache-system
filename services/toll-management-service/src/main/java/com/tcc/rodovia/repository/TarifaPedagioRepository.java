package com.tcc.rodovia.repository;

import java.time.LocalDate;
import java.util.List;
import java.util.Optional;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import com.tcc.rodovia.entity.TarifaPedagio;
import com.tcc.rodovia.enums.TipoVeiculoEnum;

@Repository
public interface TarifaPedagioRepository extends JpaRepository<TarifaPedagio, Long> {
    
    @Query("SELECT t FROM TarifaPedagio t WHERE t.tipoVeiculo = :tipoVeiculo " +
           "AND t.vigenciaInicio <= :data " +
           "AND (t.vigenciaFim IS NULL OR t.vigenciaFim >= :data)")
    Optional<TarifaPedagio> findTarifaVigente(@Param("tipoVeiculo") TipoVeiculoEnum tipoVeiculo, 
                                               @Param("data") LocalDate data);
    
    List<TarifaPedagio> findByTipoVeiculo(TipoVeiculoEnum tipoVeiculo);
    
    @Query("SELECT t FROM TarifaPedagio t WHERE t.vigenciaInicio <= :data " +
           "AND (t.vigenciaFim IS NULL OR t.vigenciaFim >= :data)")
    List<TarifaPedagio> findTarifasVigentes(@Param("data") LocalDate data);
}
