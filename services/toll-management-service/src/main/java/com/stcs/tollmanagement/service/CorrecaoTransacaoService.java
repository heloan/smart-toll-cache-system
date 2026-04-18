package com.stcs.tollmanagement.service;

import java.util.List;
import java.util.stream.Collectors;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import com.stcs.tollmanagement.dto.CorrecaoTransacaoRequestDTO;
import com.stcs.tollmanagement.dto.CorrecaoTransacaoResponseDTO;
import com.stcs.tollmanagement.entity.CorrecaoTransacao;
import com.stcs.tollmanagement.entity.Operador;
import com.stcs.tollmanagement.entity.TransacaoPedagio;
import com.stcs.tollmanagement.enums.StatusTransacaoEnum;
import com.stcs.tollmanagement.enums.TipoCorrecaoEnum;
import com.stcs.tollmanagement.repository.CorrecaoTransacaoRepository;
import com.stcs.tollmanagement.repository.OperadorRepository;
import com.stcs.tollmanagement.repository.TransacaoPedagioRepository;
import com.stcs.tollmanagement.util.OrigemDadosMarker;

import lombok.RequiredArgsConstructor;

@Service
@RequiredArgsConstructor
public class CorrecaoTransacaoService {

    private final CorrecaoTransacaoRepository correcaoTransacaoRepository;
    private final TransacaoPedagioRepository transacaoPedagioRepository;
    private final OperadorRepository operadorRepository;
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

    @Transactional
    public CorrecaoTransacaoResponseDTO criarCorrecao(Long transacaoId, CorrecaoTransacaoRequestDTO request) {
        TransacaoPedagio transacao = transacaoPedagioRepository.findById(transacaoId)
                .orElseThrow(() -> new IllegalArgumentException("Transação não encontrada: " + transacaoId));

        Operador operador = operadorRepository.findById(request.getOperadorId())
                .orElseThrow(() -> new IllegalArgumentException("Operador não encontrado: " + request.getOperadorId()));

        CorrecaoTransacao correcao = CorrecaoTransacao.builder()
                .transacao(transacao)
                .operador(operador)
                .motivo(request.getMotivo())
                .valorAnterior(transacao.getValorOriginal())
                .valorCorrigido(request.getValorCorrigido())
                .tipoCorrecao(request.getTipoCorrecao() != null ? request.getTipoCorrecao() : TipoCorrecaoEnum.AUTOMATICA)
                .build();

        correcaoTransacaoRepository.save(correcao);

        transacao.setStatusTransacao(StatusTransacaoEnum.CORRIGIDA);
        transacaoPedagioRepository.save(transacao);

        return CorrecaoTransacaoResponseDTO.fromEntity(correcao);
    }
}
