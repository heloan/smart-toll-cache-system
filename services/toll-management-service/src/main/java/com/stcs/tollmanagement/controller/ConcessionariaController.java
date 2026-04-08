package com.stcs.tollmanagement.controller;

import java.util.List;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.stcs.tollmanagement.dto.ConcessionariaRequestDTO;
import com.stcs.tollmanagement.dto.ConcessionariaResponseDTO;
import com.stcs.tollmanagement.service.ConcessionariaService;

import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;

@RestController
@RequestMapping("/api/concessionarias")
@RequiredArgsConstructor
@Validated
public class ConcessionariaController {

    private final ConcessionariaService concessionariaService;

    @PostMapping
    public ResponseEntity<ConcessionariaResponseDTO> criarConcessionaria(
            @Valid @RequestBody ConcessionariaRequestDTO request) {
        try {
            ConcessionariaResponseDTO response = concessionariaService.criarConcessionaria(request);
            return ResponseEntity.status(HttpStatus.CREATED).body(response);
        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest().build();
        }
    }

    @GetMapping
    public ResponseEntity<List<ConcessionariaResponseDTO>> listarTodas() {
        List<ConcessionariaResponseDTO> concessionarias = concessionariaService.listarTodas();
        return ResponseEntity.ok(concessionarias);
    }

    @GetMapping("/{id}")
    public ResponseEntity<ConcessionariaResponseDTO> buscarPorId(@PathVariable Long id) {
        try {
            ConcessionariaResponseDTO response = concessionariaService.buscarPorId(id);
            return ResponseEntity.ok(response);
        } catch (IllegalArgumentException e) {
            return ResponseEntity.notFound().build();
        }
    }

    @GetMapping("/cnpj/{cnpj}")
    public ResponseEntity<ConcessionariaResponseDTO> buscarPorCnpj(@PathVariable String cnpj) {
        try {
            ConcessionariaResponseDTO response = concessionariaService.buscarPorCnpj(cnpj);
            return ResponseEntity.ok(response);
        } catch (IllegalArgumentException e) {
            return ResponseEntity.notFound().build();
        }
    }
}
