package com.tcc.rodovia.service;

import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Propagation;
import org.springframework.transaction.annotation.Transactional;

import com.tcc.rodovia.entity.RegistroPerformance;
import com.tcc.rodovia.repository.RegistroPerformanceRepository;

import lombok.RequiredArgsConstructor;

@Service
@RequiredArgsConstructor
public class RegistroPerformanceService {

    private final RegistroPerformanceRepository repository;

    @Async
    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void registrarAsync(RegistroPerformance registro) {
        try {
            repository.save(registro);
        } catch (Exception e) {
            // Log silencioso para não afetar a requisição principal
            System.err.println("Erro ao registrar performance: " + e.getMessage());
        }
    }
}
