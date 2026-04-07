package com.tcc.rodovia.dto;

import java.math.BigDecimal;
import java.time.LocalDateTime;

import com.tcc.rodovia.entity.TransacaoPedagio;
import com.tcc.rodovia.enums.StatusTransacaoEnum;
import com.tcc.rodovia.enums.TipoVeiculoEnum;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * DTO para enviar/receber transações de pedágio via Kafka
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class TransacaoPedagioKafkaDTO {

    private Long pracaId;
    private Long pistaId;
    private Long tarifaId;
    private LocalDateTime dataHoraPassagem;
    private String placa;
    private String tagId;
    private TipoVeiculoEnum tipoVeiculo;
    private BigDecimal valorOriginal;
    private StatusTransacaoEnum statusTransacao;
    private String hashIntegridade;

    /**
     * Converte a entidade TransacaoPedagio para DTO Kafka
     */
    public static TransacaoPedagioKafkaDTO fromEntity(TransacaoPedagio entity) {
        return TransacaoPedagioKafkaDTO.builder()
                .pracaId(entity.getPraca().getId())
                .pistaId(entity.getPista().getId())
                .tarifaId(entity.getTarifa().getId())
                .dataHoraPassagem(entity.getDataHoraPassagem())
                .placa(entity.getPlaca())
                .tagId(entity.getTagId())
                .tipoVeiculo(entity.getTipoVeiculo())
                .valorOriginal(entity.getValorOriginal())
                .statusTransacao(entity.getStatusTransacao())
                .hashIntegridade(entity.getHashIntegridade())
                .build();
    }
}
