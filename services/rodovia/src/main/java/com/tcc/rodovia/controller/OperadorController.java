package com.tcc.rodovia.controller;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.tcc.rodovia.dto.OperadorRequestDTO;
import com.tcc.rodovia.dto.OperadorResponseDTO;
import com.tcc.rodovia.service.OperadorService;

import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;

@RestController
@RequestMapping("/api/operadores")
@RequiredArgsConstructor
@Validated
public class OperadorController {

    private final OperadorService operadorService;

    @PostMapping
    public ResponseEntity<OperadorResponseDTO> criarOperador(@Valid @RequestBody OperadorRequestDTO request) {
        try {
            OperadorResponseDTO response = operadorService.criarOperador(request);
            return ResponseEntity.status(HttpStatus.CREATED).body(response);
        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest().build();
        }
    }

    @GetMapping("/{id}")
    public ResponseEntity<OperadorResponseDTO> buscarPorId(@PathVariable Long id) {
        try {
            OperadorResponseDTO response = operadorService.buscarPorId(id);
            return ResponseEntity.ok(response);
        } catch (IllegalArgumentException e) {
            return ResponseEntity.notFound().build();
        }
    }

    @GetMapping("/username/{username}")
    public ResponseEntity<OperadorResponseDTO> buscarPorUsername(@PathVariable String username) {
        try {
            OperadorResponseDTO response = operadorService.buscarPorUsername(username);
            return ResponseEntity.ok(response);
        } catch (IllegalArgumentException e) {
            return ResponseEntity.notFound().build();
        }
    }
}
