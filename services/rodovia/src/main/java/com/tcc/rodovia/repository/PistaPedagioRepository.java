package com.tcc.rodovia.repository;

import java.util.List;
import java.util.Optional;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import com.tcc.rodovia.entity.PistaPedagio;

@Repository
public interface PistaPedagioRepository extends JpaRepository<PistaPedagio, Long> {
    
    List<PistaPedagio> findByPracaId(Long pracaId);
    
    Optional<PistaPedagio> findByPracaIdAndNumeroPista(Long pracaId, Integer numeroPista);
    
    boolean existsByPracaIdAndNumeroPista(Long pracaId, Integer numeroPista);
}
