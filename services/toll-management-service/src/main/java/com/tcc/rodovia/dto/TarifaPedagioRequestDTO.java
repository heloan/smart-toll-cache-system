package com.tcc.rodovia.dto;

import java.math.BigDecimal;
import java.time.LocalDate;

import com.tcc.rodovia.enums.TipoVeiculoEnum;

import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Positive;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class TarifaPedagioRequestDTO {

    @NotNull(message = "Tipo de veículo é obrigatório")
    private TipoVeiculoEnum tipoVeiculo;

    @NotNull(message = "Valor é obrigatório")
    @Positive(message = "Valor deve ser positivo")
    private BigDecimal valor;

    @NotNull(message = "Data de início da vigência é obrigatória")
    private LocalDate vigenciaInicio;

    private LocalDate vigenciaFim;
}
