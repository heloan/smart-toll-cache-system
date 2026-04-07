package com.tcc.rodovia.repository;

import java.util.List;
import java.util.Optional;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import com.tcc.rodovia.entity.Rodovia;

@Repository
public interface RodoviaRepository extends JpaRepository<Rodovia, Long> {
    
    List<Rodovia> findByConcessionariaId(Long concessionariaId);
    
    Optional<Rodovia> findByCodigo(String codigo);
    
    boolean existsByCodigo(String codigo);
}
