package com.stcs.tollmanagement.service;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.Random;

import org.springframework.boot.CommandLineRunner;
import org.springframework.context.annotation.Profile;
import org.springframework.stereotype.Component;

import com.stcs.tollmanagement.dto.TransacaoPedagioKafkaDTO;
import com.stcs.tollmanagement.enums.StatusTransacaoEnum;
import com.stcs.tollmanagement.enums.TipoVeiculoEnum;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

/**
 * Gerador de transações de teste para o Kafka
 * Ative com o profile: --spring.profiles.active=kafka-test
 */
@Component
@Profile("kafka-test")
@RequiredArgsConstructor
@Slf4j
public class KafkaTransacaoTestGenerator implements CommandLineRunner {

    private final TransacaoKafkaProducer transacaoKafkaProducer;
    private final Random random = new Random();

    @Override
    public void run(String... args) throws Exception {
        log.info("=== Iniciando geração de transações de teste para Kafka ===");
        
        int quantidade = 10; // Altere conforme necessário
        
        if (args.length > 0) {
            try {
                quantidade = Integer.parseInt(args[0]);
            } catch (NumberFormatException e) {
                log.warn("Argumento inválido, usando quantidade padrão: 10");
            }
        }
        
        log.info("Gerando {} transações de teste...", quantidade);
        
        List<TransacaoPedagioKafkaDTO> transacoes = gerarTransacoesTeste(quantidade);
        
        for (int i = 0; i < transacoes.size(); i++) {
            TransacaoPedagioKafkaDTO transacao = transacoes.get(i);
            
            log.info("Enviando transação {}/{} - Placa: {}", 
                    i + 1, transacoes.size(), transacao.getPlaca());
            
            transacaoKafkaProducer.enviarTransacao(transacao);
            
            // Pequeno delay para não sobrecarregar
            Thread.sleep(100);
        }
        
        log.info("=== {} transações enviadas para o Kafka com sucesso ===", quantidade);
        log.info("Aguarde alguns segundos para o processamento pelo consumer...");
    }

    /**
     * Gera uma lista de transações de teste
     */
    private List<TransacaoPedagioKafkaDTO> gerarTransacoesTeste(int quantidade) {
        List<TransacaoPedagioKafkaDTO> transacoes = new ArrayList<>();
        
        for (int i = 0; i < quantidade; i++) {
            transacoes.add(gerarTransacaoAleatoria(i));
        }
        
        return transacoes;
    }

    /**
     * Gera uma transação aleatória
     */
    private TransacaoPedagioKafkaDTO gerarTransacaoAleatoria(int index) {
        String[] letras = {"A", "B", "C", "D", "E", "F", "G", "H", "J", "K", "L", "M", "N", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"};
        
        // Gerar placa no formato Mercosul: ABC1D23
        String placa = String.format("%s%s%s%d%s%02d",
                letras[random.nextInt(letras.length)],
                letras[random.nextInt(letras.length)],
                letras[random.nextInt(letras.length)],
                random.nextInt(10),
                letras[random.nextInt(letras.length)],
                random.nextInt(100));
        
        TipoVeiculoEnum[] tipos = TipoVeiculoEnum.values();
        TipoVeiculoEnum tipoVeiculo = tipos[random.nextInt(tipos.length)];
        
        BigDecimal valorOriginal;
        switch (tipoVeiculo) {
            case CARRO:
                valorOriginal = new BigDecimal("8.50");
                break;
            case CAMINHAO:
                valorOriginal = new BigDecimal("25.00");
                break;
            case MOTO:
                valorOriginal = new BigDecimal("4.25");
                break;
            default:
                valorOriginal = new BigDecimal("10.00");
        }
        
        return TransacaoPedagioKafkaDTO.builder()
                .pracaId(1L)
                .pistaId(1L)
                .tarifaId(1L)
                .dataHoraPassagem(LocalDateTime.now().minusSeconds(random.nextInt(3600)))
                .placa(placa)
                .tagId("TAG" + String.format("%08d", random.nextInt(100000000)))
                .tipoVeiculo(tipoVeiculo)
                .valorOriginal(valorOriginal)
                .statusTransacao(StatusTransacaoEnum.OK)
                .hashIntegridade("hash_test_" + System.currentTimeMillis() + "_" + index)
                .build();
    }
}
