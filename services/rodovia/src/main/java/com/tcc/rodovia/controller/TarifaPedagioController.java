package com.tcc.rodovia.controller;

import java.util.List;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.tcc.rodovia.dto.TarifaPedagioRequestDTO;
import com.tcc.rodovia.dto.TarifaPedagioResponseDTO;
import com.tcc.rodovia.service.TarifaPedagioService;

import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;

@RestController
@RequestMapping("/api/tarifas")
@RequiredArgsConstructor
@Validated
public class TarifaPedagioController {

    private final TarifaPedagioService tarifaPedagioService;

    @PostMapping
    public ResponseEntity<TarifaPedagioResponseDTO> criarTarifa(@Valid @RequestBody TarifaPedagioRequestDTO request) {
        try {
            TarifaPedagioResponseDTO response = tarifaPedagioService.criarTarifa(request);
            return ResponseEntity.status(HttpStatus.CREATED).body(response);
        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest().build();
        }
    }

    @PutMapping("/{id}")
    public ResponseEntity<TarifaPedagioResponseDTO> atualizarTarifa(
            @PathVariable Long id,
            @Valid @RequestBody TarifaPedagioRequestDTO request) {
        try {
            TarifaPedagioResponseDTO response = tarifaPedagioService.atualizarTarifa(id, request);
            return ResponseEntity.ok(response);
        } catch (IllegalArgumentException e) {
            return ResponseEntity.notFound().build();
        }
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> excluirTarifa(@PathVariable Long id) {
        try {
            tarifaPedagioService.excluirTarifa(id);
            return ResponseEntity.noContent().build();
        } catch (IllegalArgumentException e) {
            return ResponseEntity.notFound().build();
        }
    }

    @GetMapping
    public ResponseEntity<List<TarifaPedagioResponseDTO>> listarTodas() {
        List<TarifaPedagioResponseDTO> tarifas = tarifaPedagioService.listarTodas();
        return ResponseEntity.ok(tarifas);
    }

    @GetMapping("/vigentes")
    public ResponseEntity<List<TarifaPedagioResponseDTO>> listarVigentes() {
        List<TarifaPedagioResponseDTO> tarifas = tarifaPedagioService.listarTarifasVigentes();
        return ResponseEntity.ok(tarifas);
    }

    @GetMapping("/{id}")
    public ResponseEntity<TarifaPedagioResponseDTO> buscarPorId(@PathVariable Long id) {
        try {
            TarifaPedagioResponseDTO response = tarifaPedagioService.buscarPorId(id);
            return ResponseEntity.ok(response);
        } catch (IllegalArgumentException e) {
            return ResponseEntity.notFound().build();
        }
    }
}
