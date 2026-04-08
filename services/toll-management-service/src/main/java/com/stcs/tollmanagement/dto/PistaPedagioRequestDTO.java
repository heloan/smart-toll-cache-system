package com.stcs.tollmanagement.dto;

import com.stcs.tollmanagement.enums.TipoPistaEnum;

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
public class PistaPedagioRequestDTO {

    @NotNull(message = "ID da praça é obrigatório")
    private Long pracaId;

    @NotNull(message = "Número da pista é obrigatório")
    @Positive(message = "Número da pista deve ser positivo")
    private Integer numeroPista;

    @NotNull(message = "Tipo da pista é obrigatório")
    private TipoPistaEnum tipoPista;

    @Size(max = 20, message = "Sentido deve ter no máximo 20 caracteres")
    private String sentido;

    private Boolean ativa;
}
