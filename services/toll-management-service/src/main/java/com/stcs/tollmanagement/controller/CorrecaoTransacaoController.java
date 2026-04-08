package com.stcs.tollmanagement.controller;

import java.util.List;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.stcs.tollmanagement.dto.CorrecaoTransacaoResponseDTO;
import com.stcs.tollmanagement.service.CorrecaoTransacaoService;

import lombok.RequiredArgsConstructor;

@RestController
@RequestMapping("/api/correcoes")
@RequiredArgsConstructor
public class CorrecaoTransacaoController {

    private final CorrecaoTransacaoService correcaoTransacaoService;

    /**
     * Lista todas as correções de transação
     */
    @GetMapping
    public ResponseEntity<List<CorrecaoTransacaoResponseDTO>> listarTodas() {
        List<CorrecaoTransacaoResponseDTO> correcoes = correcaoTransacaoService.listarTodas();
        return ResponseEntity.ok(correcoes);
    }

    /**
     * Busca uma correção específica por ID
     */
    @GetMapping("/{id}")
    public ResponseEntity<CorrecaoTransacaoResponseDTO> buscarPorId(@PathVariable Long id) {
        try {
            CorrecaoTransacaoResponseDTO correcao = correcaoTransacaoService.buscarPorId(id);
            return ResponseEntity.ok(correcao);
        } catch (IllegalArgumentException e) {
            return ResponseEntity.notFound().build();
        }
    }

    /**
     * Lista correções realizadas por um operador específico
     */
    @GetMapping("/operador/{operadorId}")
    public ResponseEntity<List<CorrecaoTransacaoResponseDTO>> listarPorOperador(
            @PathVariable Long operadorId) {
        List<CorrecaoTransacaoResponseDTO> correcoes = 
            correcaoTransacaoService.listarPorOperador(operadorId);
        return ResponseEntity.ok(correcoes);
    }
}
