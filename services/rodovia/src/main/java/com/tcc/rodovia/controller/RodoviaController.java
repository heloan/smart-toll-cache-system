package com.tcc.rodovia.controller;

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

import com.tcc.rodovia.dto.RodoviaRequestDTO;
import com.tcc.rodovia.dto.RodoviaResponseDTO;
import com.tcc.rodovia.service.RodoviaService;

import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;

@RestController
@RequestMapping("/api/rodovias")
@RequiredArgsConstructor
@Validated
public class RodoviaController {

    private final RodoviaService rodoviaService;

    @PostMapping
    public ResponseEntity<RodoviaResponseDTO> criarRodovia(@Valid @RequestBody RodoviaRequestDTO request) {
        try {
            RodoviaResponseDTO response = rodoviaService.criarRodovia(request);
            return ResponseEntity.status(HttpStatus.CREATED).body(response);
        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest().build();
        }
    }

    @GetMapping
    public ResponseEntity<List<RodoviaResponseDTO>> listarTodas() {
        List<RodoviaResponseDTO> rodovias = rodoviaService.listarTodas();
        return ResponseEntity.ok(rodovias);
    }

    @GetMapping("/{id}")
    public ResponseEntity<RodoviaResponseDTO> buscarPorId(@PathVariable Long id) {
        try {
            RodoviaResponseDTO response = rodoviaService.buscarPorId(id);
            return ResponseEntity.ok(response);
        } catch (IllegalArgumentException e) {
            return ResponseEntity.notFound().build();
        }
    }

    @GetMapping("/concessionaria/{concessionariaId}")
    public ResponseEntity<List<RodoviaResponseDTO>> listarPorConcessionaria(
            @PathVariable Long concessionariaId) {
        List<RodoviaResponseDTO> rodovias = rodoviaService.listarPorConcessionaria(concessionariaId);
        return ResponseEntity.ok(rodovias);
    }

    @GetMapping("/codigo/{codigo}")
    public ResponseEntity<RodoviaResponseDTO> buscarPorCodigo(@PathVariable String codigo) {
        try {
            RodoviaResponseDTO response = rodoviaService.buscarPorCodigo(codigo);
            return ResponseEntity.ok(response);
        } catch (IllegalArgumentException e) {
            return ResponseEntity.notFound().build();
        }
    }
}
