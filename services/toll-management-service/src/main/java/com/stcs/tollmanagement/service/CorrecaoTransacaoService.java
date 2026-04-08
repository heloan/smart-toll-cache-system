package com.stcs.tollmanagement.service;

import java.util.List;
import java.util.stream.Collectors;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import com.stcs.tollmanagement.dto.CorrecaoTransacaoResponseDTO;
import com.stcs.tollmanagement.repository.CorrecaoTransacaoRepository;
import com.stcs.tollmanagement.util.OrigemDadosMarker;

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
