package com.tcc.rodovia.dto;

import java.math.BigDecimal;
import java.time.LocalDateTime;

import com.tcc.rodovia.enums.StatusTransacaoEnum;
import com.tcc.rodovia.enums.TipoVeiculoEnum;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Positive;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * DTO para receber requisição de criação de transação
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class TransacaoPedagioRequestDTO {

    @NotNull(message = "ID da praça é obrigatório")
    @Positive(message = "ID da praça deve ser positivo")
    private Long pracaId;

    @NotNull(message = "ID da pista é obrigatório")
    @Positive(message = "ID da pista deve ser positivo")
    private Long pistaId;

    // TarifaId é opcional - se não fornecido, será buscada automaticamente
    // pela data de passagem e tipo de veículo
    private Long tarifaId;

    @NotNull(message = "Data e hora da passagem é obrigatória")
    private LocalDateTime dataHoraPassagem;

    @NotBlank(message = "Placa é obrigatória")
    @Pattern(regexp = "^[A-Z]{3}[0-9][A-Z0-9][0-9]{2}$", 
             message = "Placa inválida (formato: ABC1D23)")
    private String placa;

    private String tagId;

    @NotNull(message = "Tipo de veículo é obrigatório")
    private TipoVeiculoEnum tipoVeiculo;

    @NotNull(message = "Valor original é obrigatório")
    @Positive(message = "Valor original deve ser positivo")
    private BigDecimal valorOriginal;

    private StatusTransacaoEnum statusTransacao;

    private String hashIntegridade;

    /**
     * Converte para DTO Kafka
     */
    public TransacaoPedagioKafkaDTO toKafkaDTO() {
        return TransacaoPedagioKafkaDTO.builder()
                .pracaId(this.pracaId)
                .pistaId(this.pistaId)
                .tarifaId(this.tarifaId)
                .dataHoraPassagem(this.dataHoraPassagem)
                .placa(this.placa)
                .tagId(this.tagId)
                .tipoVeiculo(this.tipoVeiculo)
                .valorOriginal(this.valorOriginal)
                .statusTransacao(this.statusTransacao != null ? this.statusTransacao : StatusTransacaoEnum.OK)
                .hashIntegridade(this.hashIntegridade)
                .build();
    }
}
