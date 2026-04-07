package com.tcc.rodovia.service;

import java.util.concurrent.CompletableFuture;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.kafka.support.SendResult;
import org.springframework.stereotype.Service;

import com.tcc.rodovia.dto.TransacaoPedagioKafkaDTO;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

/**
 * Serviço para produzir mensagens de transações no Kafka
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class TransacaoKafkaProducer {

    private final KafkaTemplate<String, TransacaoPedagioKafkaDTO> kafkaTemplate;

    @Value("${kafka.topic.transacao-pedagio}")
    private String topicName;

    /**
     * Envia uma transação para o tópico Kafka
     * @param transacao DTO da transação a ser enviada
     * @return CompletableFuture com o resultado do envio
     */
    public CompletableFuture<SendResult<String, TransacaoPedagioKafkaDTO>> enviarTransacao(
            TransacaoPedagioKafkaDTO transacao) {
        
        String key = transacao.getPlaca(); // Usando placa como chave para garantir ordem por veículo
        
        log.info("Enviando transação para Kafka - Placa: {}, Praça: {}, Pista: {}", 
                transacao.getPlaca(), transacao.getPracaId(), transacao.getPistaId());
        
        return kafkaTemplate.send(topicName, key, transacao)
                .whenComplete((result, ex) -> {
                    if (ex == null) {
                        log.info("Transação enviada com sucesso - Placa: {}, Offset: {}, Partition: {}", 
                                transacao.getPlaca(),
                                result.getRecordMetadata().offset(),
                                result.getRecordMetadata().partition());
                    } else {
                        log.error("Erro ao enviar transação para Kafka - Placa: {}, Erro: {}", 
                                transacao.getPlaca(), ex.getMessage(), ex);
                    }
                });
    }

    /**
     * Envia uma transação de forma síncrona
     * @param transacao DTO da transação a ser enviada
     */
    public void enviarTransacaoSync(TransacaoPedagioKafkaDTO transacao) {
        try {
            String key = transacao.getPlaca();
            SendResult<String, TransacaoPedagioKafkaDTO> result = 
                    kafkaTemplate.send(topicName, key, transacao).get();
            
            log.info("Transação enviada sincronamente - Placa: {}, Offset: {}", 
                    transacao.getPlaca(), result.getRecordMetadata().offset());
        } catch (Exception e) {
            log.error("Erro ao enviar transação sincronamente - Placa: {}, Erro: {}", 
                    transacao.getPlaca(), e.getMessage(), e);
            throw new RuntimeException("Erro ao enviar transação para Kafka", e);
        }
    }
}
