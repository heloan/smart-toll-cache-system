package com.tcc.rodovia.dto;

import java.math.BigDecimal;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Positive;
import jakarta.validation.constraints.Size;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class PracaPedagioRequestDTO {

    @NotNull(message = "ID da rodovia é obrigatório")
    private Long rodoviaId;

    @NotBlank(message = "Nome é obrigatório")
    @Size(max = 120, message = "Nome deve ter no máximo 120 caracteres")
    private String nome;

    @NotNull(message = "KM é obrigatório")
    @Positive(message = "KM deve ser positivo")
    private BigDecimal km;

    @Size(max = 20, message = "Sentido deve ter no máximo 20 caracteres")
    private String sentido;

    private Boolean ativa;
}
