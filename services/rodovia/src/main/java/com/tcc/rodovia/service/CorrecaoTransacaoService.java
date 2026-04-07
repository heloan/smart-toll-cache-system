package com.tcc.rodovia.service;

import java.util.List;
import java.util.stream.Collectors;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import com.tcc.rodovia.dto.CorrecaoTransacaoResponseDTO;
import com.tcc.rodovia.repository.CorrecaoTransacaoRepository;
import com.tcc.rodovia.util.OrigemDadosMarker;

import lombok.RequiredArgsConstructor;

@Service
@RequiredArgsConstructor
public class CorrecaoTransacaoService {

    private final CorrecaoTransacaoRepository correcaoTransacaoRepository;
    private final OrigemDadosMarker origemDadosMarker;

    @Transactional(readOnly = true)
    public List<CorrecaoTransacaoResponseDTO> listarTodas() {
        origemDadosMarker.marcarBancoDados();
        
        return correcaoTransacaoRepository.findAllWithRelations().stream()
                .map(CorrecaoTransacaoResponseDTO::fromEntity)
                .collect(Collectors.toList());
    }

    @Transactional(readOnly = true)
    public CorrecaoTransacaoResponseDTO buscarPorId(Long id) {
        origemDadosMarker.marcarBancoDados();
        
        return correcaoTransacaoRepository.findById(id)
                .map(CorrecaoTransacaoResponseDTO::fromEntity)
                .orElseThrow(() -> new IllegalArgumentException("Correção não encontrada"));
    }

    @Transactional(readOnly = true)
    public List<CorrecaoTransacaoResponseDTO> listarPorOperador(Long operadorId) {
        origemDadosMarker.marcarBancoDados();
        
        return correcaoTransacaoRepository.findByOperadorId(operadorId).stream()
                .map(CorrecaoTransacaoResponseDTO::fromEntity)
                .collect(Collectors.toList());
    }
}
