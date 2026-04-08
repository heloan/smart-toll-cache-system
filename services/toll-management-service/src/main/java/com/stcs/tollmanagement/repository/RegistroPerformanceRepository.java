package com.stcs.tollmanagement.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import com.stcs.tollmanagement.entity.RegistroPerformance;

@Repository
public interface RegistroPerformanceRepository extends JpaRepository<RegistroPerformance, Long> {
}
