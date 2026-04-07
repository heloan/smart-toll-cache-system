package com.tcc.rodovia.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import com.tcc.rodovia.entity.RegistroPerformance;

@Repository
public interface RegistroPerformanceRepository extends JpaRepository<RegistroPerformance, Long> {
}
