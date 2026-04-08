package com.stcs.tollmanagement.repository;

import java.util.Optional;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import com.stcs.tollmanagement.entity.Concessionaria;

@Repository
public interface ConcessionariaRepository extends JpaRepository<Concessionaria, Long> {
    
    Optional<Concessionaria> findByCnpj(String cnpj);
    
    boolean existsByCnpj(String cnpj);
}
