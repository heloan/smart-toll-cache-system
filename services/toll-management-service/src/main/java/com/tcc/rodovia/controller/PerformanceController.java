package com.tcc.rodovia.controller;

import java.util.List;

import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Sort;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import com.tcc.rodovia.entity.RegistroPerformance;
import com.tcc.rodovia.repository.RegistroPerformanceRepository;

import lombok.RequiredArgsConstructor;

@RestController
@RequestMapping("/api/performance")
@RequiredArgsConstructor
public class PerformanceController {

    private final RegistroPerformanceRepository registroPerformanceRepository;

    @GetMapping
    public ResponseEntity<List<RegistroPerformance>> listarRegistros(
            @RequestParam(defaultValue = "100") int limit) {
        
        PageRequest pageRequest = PageRequest.of(0, limit, Sort.by(Sort.Direction.DESC, "criadoEm"));
        List<RegistroPerformance> registros = registroPerformanceRepository.findAll(pageRequest).getContent();
        
        return ResponseEntity.ok(registros);
    }
}
