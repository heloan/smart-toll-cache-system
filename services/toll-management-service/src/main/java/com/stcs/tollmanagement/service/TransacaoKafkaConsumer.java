package com.stcs.tollmanagement.service;

import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.kafka.support.KafkaHeaders;
import org.springframework.messaging.handler.annotation.Header;
import org.springframework.messaging.handler.annotation.Payload;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import com.stcs.tollmanagement.dto.TransacaoPedagioKafkaDTO;
import com.stcs.tollmanagement.entity.OcorrenciaTransacao;
import com.stcs.tollmanagement.entity.PistaPedagio;
import com.stcs.tollmanagement.entity.PracaPedagio;
import com.stcs.tollmanagement.entity.TarifaPedagio;
import com.stcs.tollmanagement.entity.TransacaoPedagio;
import com.stcs.tollmanagement.enums.StatusTransacaoEnum;
import com.stcs.tollmanagement.enums.TipoOcorrenciaEnum;
import com.stcs.tollmanagement.repository.OcorrenciaTransacaoRepository;
import com.stcs.tollmanagement.repository.PistaPedagioRepository;
import com.stcs.tollmanagement.repository.PracaPedagioRepository;
import com.stcs.tollmanagement.repository.TarifaPedagioRepository;
import com.stcs.tollmanagement.repository.TransacaoPedagioRepository;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

/**
 * Serviço para consumir mensagens de transações do Kafka e persisti-las no banco
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class TransacaoKafkaConsumer {

    private final TransacaoPedagioRepository transacaoPedagioRepository;
    private final OcorrenciaTransacaoRepository ocorrenciaTransacaoRepository;
    private final PracaPedagioRepository pracaPedagioRepository;
    private final PistaPedagioRepository pistaPedagioRepository;
    private final TarifaPedagioRepository tarifaPedagioRepository;

    /**
     * Consome mensagens do tópico de transações e salva no banco de dados
     */
    @KafkaListener(
        topics = "${kafka.topic.transacao-pedagio}",
        groupId = "${spring.kafka.consumer.group-id}",
        containerFactory = "kafkaListenerContainerFactory"
    )
    @Transactional
    public void consumirTransacao(
            @Payload TransacaoPedagioKafkaDTO transacaoDTO,
            @Header(KafkaHeaders.RECEIVED_PARTITION) int partition,
            @Header(KafkaHeaders.OFFSET) long offset) {
        
        log.info("Recebida transação do Kafka - Placa: {}, Partition: {}, Offset: {}", 
                transacaoDTO.getPlaca(), partition, offset);
        
        try {
            // Buscar entidades relacionadas
            PracaPedagio praca = pracaPedagioRepository.findById(transacaoDTO.getPracaId())
                    .orElseThrow(() -> new IllegalArgumentException(
                            "Praça não encontrada: " + transacaoDTO.getPracaId()));
            
            PistaPedagio pista = pistaPedagioRepository.findById(transacaoDTO.getPistaId())
                    .orElseThrow(() -> new IllegalArgumentException(
                            "Pista não encontrada: " + transacaoDTO.getPistaId()));
            
            // Buscar tarifa vigente por tipo de veículo e data da passagem
            TarifaPedagio tarifa = tarifaPedagioRepository.findTarifaVigente(
                    transacaoDTO.getTipoVeiculo(), 
                    transacaoDTO.getDataHoraPassagem().toLocalDate())
                    .orElseThrow(() -> new IllegalArgumentException(
                            "Tarifa vigente não encontrada para tipo de veículo: " + 
                            transacaoDTO.getTipoVeiculo() + " na data: " + 
                            transacaoDTO.getDataHoraPassagem().toLocalDate()));
            
            // Criar entidade TransacaoPedagio
            TransacaoPedagio transacao = TransacaoPedagio.builder()
                    .praca(praca)
                    .pista(pista)
                    .tarifa(tarifa)
                    .dataHoraPassagem(transacaoDTO.getDataHoraPassagem())
                    .placa(transacaoDTO.getPlaca())
                    .tagId(transacaoDTO.getTagId())
                    .tipoVeiculo(transacaoDTO.getTipoVeiculo())
                    .valorOriginal(transacaoDTO.getValorOriginal())
                    .statusTransacao(transacaoDTO.getStatusTransacao())
                    .hashIntegridade(transacaoDTO.getHashIntegridade())
                    .build();
            
            // Salvar no banco de dados
            TransacaoPedagio transacaoSalva = transacaoPedagioRepository.save(transacao);
            
            // Se a transação tem status OCORRENCIA, criar registro de ocorrência
            if (transacaoSalva.getStatusTransacao() == StatusTransacaoEnum.OCORRENCIA) {
                TipoOcorrenciaEnum tipoOcorrencia = detectarTipoOcorrencia(transacaoSalva, tarifa);
                OcorrenciaTransacao ocorrencia = OcorrenciaTransacao.builder()
                        .transacao(transacaoSalva)
                        .tipoOcorrencia(tipoOcorrencia)
                        .observacao("Ocorrência detectada automaticamente pelo consumidor Kafka")
                        .detectadaAutomaticamente(true)
                        .build();
                ocorrenciaTransacaoRepository.save(ocorrencia);
                log.info("Ocorrência criada - Tipo: {}, Transação ID: {}", 
                        tipoOcorrencia, transacaoSalva.getId());
            }
            
            log.info("Transação processada e salva com sucesso - ID: {}, Placa: {}, Praça: {}", 
                    transacaoSalva.getId(), transacaoSalva.getPlaca(), praca.getNome());
            
        } catch (Exception e) {
            log.error("Erro ao processar transação do Kafka - Placa: {}, Partition: {}, Offset: {}, Erro: {}", 
                    transacaoDTO.getPlaca(), partition, offset, e.getMessage(), e);
            
            // Em produção, você pode implementar uma estratégia de retry ou DLQ (Dead Letter Queue)
            throw e; // Relança a exceção para que o Kafka possa fazer retry
        }
    }

    /**
     * Detecta o tipo de ocorrência com base nos dados da transação
     */
    private TipoOcorrenciaEnum detectarTipoOcorrencia(TransacaoPedagio transacao, TarifaPedagio tarifa) {
        // Placa com formato inválido (ex: INV845)
        String placa = transacao.getPlaca();
        if (placa != null && (placa.length() < 7 || placa.startsWith("INV"))) {
            return TipoOcorrenciaEnum.FALHA_LEITURA;
        }

        // Valor divergente da tarifa vigente
        if (tarifa != null && transacao.getValorOriginal() != null 
                && transacao.getValorOriginal().compareTo(tarifa.getValor()) != 0) {
            return TipoOcorrenciaEnum.SEM_SALDO;
        }

        // Tag duplicada conhecida
        if ("TAG999999".equals(transacao.getTagId())) {
            return TipoOcorrenciaEnum.TAG_BLOQUEADA;
        }

        // Horário inconsistente (futuro)
        if (transacao.getDataHoraPassagem() != null 
                && transacao.getDataHoraPassagem().isAfter(java.time.LocalDateTime.now().plusMinutes(5))) {
            return TipoOcorrenciaEnum.EVASAO;
        }

        return TipoOcorrenciaEnum.FALHA_LEITURA;
    }
}
