package com.stcs.tollmanagement.repository;

import java.util.Optional;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import com.stcs.tollmanagement.entity.Operador;

@Repository
public interface OperadorRepository extends JpaRepository<Operador, Long> {
    
    Optional<Operador> findByUsername(String username);
    
    Optional<Operador> findByEmail(String email);
    
    boolean existsByUsername(String username);
    
    boolean existsByEmail(String email);
}
