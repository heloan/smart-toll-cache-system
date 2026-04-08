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

import com.stcs.tollmanagement.dto.PistaPedagioRequestDTO;
import com.stcs.tollmanagement.dto.PistaPedagioResponseDTO;
import com.stcs.tollmanagement.service.PistaPedagioService;

import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;

@RestController
@RequestMapping("/api/pistas")
@RequiredArgsConstructor
@Validated
public class PistaPedagioController {

    private final PistaPedagioService pistaPedagioService;

    @PostMapping
    public ResponseEntity<PistaPedagioResponseDTO> criarPista(@Valid @RequestBody PistaPedagioRequestDTO request) {
        try {
            PistaPedagioResponseDTO response = pistaPedagioService.criarPista(request);
            return ResponseEntity.status(HttpStatus.CREATED).body(response);
        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest().build();
        }
    }

    @GetMapping
    public ResponseEntity<List<PistaPedagioResponseDTO>> listarTodas() {
        List<PistaPedagioResponseDTO> pistas = pistaPedagioService.listarTodas();
        return ResponseEntity.ok(pistas);
    }

    @GetMapping("/{id}")
    public ResponseEntity<PistaPedagioResponseDTO> buscarPorId(@PathVariable Long id) {
        try {
            PistaPedagioResponseDTO response = pistaPedagioService.buscarPorId(id);
            return ResponseEntity.ok(response);
        } catch (IllegalArgumentException e) {
            return ResponseEntity.notFound().build();
        }
    }

    @GetMapping("/praca/{pracaId}")
    public ResponseEntity<List<PistaPedagioResponseDTO>> listarPorPraca(@PathVariable Long pracaId) {
        List<PistaPedagioResponseDTO> pistas = pistaPedagioService.listarPorPraca(pracaId);
        return ResponseEntity.ok(pistas);
    }
}
