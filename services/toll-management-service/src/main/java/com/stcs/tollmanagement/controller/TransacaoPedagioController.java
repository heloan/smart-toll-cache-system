package com.stcs.tollmanagement.controller;

import java.util.List;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import com.stcs.tollmanagement.dto.TransacaoPedagioKafkaDTO;
import com.stcs.tollmanagement.dto.TransacaoPedagioRequestDTO;
import com.stcs.tollmanagement.dto.TransacaoPedagioResponseDTO;
import com.stcs.tollmanagement.enums.OrigemDadosEnum;
import com.stcs.tollmanagement.enums.StatusTransacaoEnum;
import com.stcs.tollmanagement.service.TransacaoKafkaProducer;
import com.stcs.tollmanagement.service.TransacaoPedagioService;

import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;

@RestController
@RequestMapping("/api/transacoes")
@RequiredArgsConstructor
public class TransacaoPedagioController {

    private final TransacaoPedagioService transacaoPedagioService;
    private final TransacaoKafkaProducer transacaoKafkaProducer;

    /**
     * Cria uma nova transação enviando para o Kafka (assíncrono)
     * O consumer do Kafka irá processar e salvar no banco de dados
     */
    @PostMapping
    public ResponseEntity<String> criarTransacao(@Valid @RequestBody TransacaoPedagioRequestDTO request) {
        try {
            TransacaoPedagioKafkaDTO kafkaDTO = request.toKafkaDTO();
            
            // Enviar para Kafka de forma assíncrona
            transacaoKafkaProducer.enviarTransacao(kafkaDTO);
            
            return ResponseEntity.status(HttpStatus.ACCEPTED)
                    .body("Transação enviada para processamento - Placa: " + request.getPlaca());
            
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body("Erro ao enviar transação: " + e.getMessage());
        }
    }

    /**
     * Cria uma nova transação de forma síncrona (aguarda confirmação do Kafka)
     */
    @PostMapping("/sync")
    public ResponseEntity<String> criarTransacaoSync(@Valid @RequestBody TransacaoPedagioRequestDTO request) {
        try {
            TransacaoPedagioKafkaDTO kafkaDTO = request.toKafkaDTO();
            
            // Enviar para Kafka de forma síncrona
            transacaoKafkaProducer.enviarTransacaoSync(kafkaDTO);
            
            return ResponseEntity.status(HttpStatus.CREATED)
                    .body("Transação enviada com sucesso para processamento - Placa: " + request.getPlaca());
            
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body("Erro ao enviar transação: " + e.getMessage());
        }
    }

    /**
     * Lista todas as transações de pedágio
     * @param limite Número máximo de registros a retornar (padrão: 1000)
     */
    @GetMapping
    public ResponseEntity<List<TransacaoPedagioResponseDTO>> listarTodas(
            @RequestParam(required = false, defaultValue = "1000") Integer limite) {
        List<TransacaoPedagioResponseDTO> transacoes = transacaoPedagioService.listarTodas(limite);
        return ResponseEntity.ok(transacoes);
    }

    /**
     * Busca uma transação específica por ID
     */
    @GetMapping("/{id}")
    public ResponseEntity<TransacaoPedagioResponseDTO> buscarPorId(@PathVariable Long id) {
        try {
            TransacaoPedagioResponseDTO transacao = transacaoPedagioService.buscarPorId(id);
            return ResponseEntity.ok(transacao);
        } catch (IllegalArgumentException e) {
            return ResponseEntity.notFound().build();
        }
    }

    /**
     * Lista transações com ocorrências que precisam ser corrigidas
     * @param limite Número máximo de transações a retornar (padrão: 100)
     * @param horas Considerar ocorrências das últimas X horas (padrão: 720 = 30 dias)
     * @param origemDados Origem dos dados: BANCO_DADOS, CACHE_LOCAL ou CACHE_REDIS (padrão: BANCO_DADOS)
     */
    @GetMapping("/ocorrencias/pendentes")
    public ResponseEntity<List<TransacaoPedagioResponseDTO>> listarComOcorrenciasParaCorrigir(
            @RequestParam(required = false, defaultValue = "100") Integer limite,
            @RequestParam(required = false, defaultValue = "720") Integer horas,
            @RequestParam(required = false) OrigemDadosEnum origemDados) {
        List<TransacaoPedagioResponseDTO> transacoes = 
            transacaoPedagioService.listarTransacoesComOcorrenciasParaCorrigir(limite, horas, origemDados);
        return ResponseEntity.ok(transacoes);
    }

    /**
     * Lista transações por status
     */
    @GetMapping("/status/{status}")
    public ResponseEntity<List<TransacaoPedagioResponseDTO>> listarPorStatus(
            @PathVariable StatusTransacaoEnum status) {
        List<TransacaoPedagioResponseDTO> transacoes = transacaoPedagioService.listarPorStatus(status);
        return ResponseEntity.ok(transacoes);
    }
}
