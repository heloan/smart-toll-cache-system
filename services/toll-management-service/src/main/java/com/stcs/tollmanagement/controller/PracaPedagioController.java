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

import com.stcs.tollmanagement.dto.PracaPedagioRequestDTO;
import com.stcs.tollmanagement.dto.PracaPedagioResponseDTO;
import com.stcs.tollmanagement.service.PracaPedagioService;

import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;

@RestController
@RequestMapping("/api/pracas")
@RequiredArgsConstructor
@Validated
public class PracaPedagioController {

    private final PracaPedagioService pracaPedagioService;

    @PostMapping
    public ResponseEntity<PracaPedagioResponseDTO> criarPraca(@Valid @RequestBody PracaPedagioRequestDTO request) {
        try {
            PracaPedagioResponseDTO response = pracaPedagioService.criarPraca(request);
            return ResponseEntity.status(HttpStatus.CREATED).body(response);
        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest().build();
        }
    }

    @GetMapping
    public ResponseEntity<List<PracaPedagioResponseDTO>> listarTodas() {
        List<PracaPedagioResponseDTO> pracas = pracaPedagioService.listarTodas();
        return ResponseEntity.ok(pracas);
    }

    @GetMapping("/{id}")
    public ResponseEntity<PracaPedagioResponseDTO> buscarPorId(@PathVariable Long id) {
        try {
            PracaPedagioResponseDTO response = pracaPedagioService.buscarPorId(id);
            return ResponseEntity.ok(response);
        } catch (IllegalArgumentException e) {
            return ResponseEntity.notFound().build();
        }
    }

    @GetMapping("/rodovia/{rodoviaId}")
    public ResponseEntity<List<PracaPedagioResponseDTO>> listarPorRodovia(@PathVariable Long rodoviaId) {
        List<PracaPedagioResponseDTO> pracas = pracaPedagioService.listarPorRodovia(rodoviaId);
        return ResponseEntity.ok(pracas);
    }
}
