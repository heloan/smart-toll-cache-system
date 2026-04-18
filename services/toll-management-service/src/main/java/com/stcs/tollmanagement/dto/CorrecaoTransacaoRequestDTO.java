package com.stcs.tollmanagement.dto;

import java.math.BigDecimal;

import com.stcs.tollmanagement.enums.TipoCorrecaoEnum;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class CorrecaoTransacaoRequestDTO {

    private Long operadorId;
    private String motivo;
    private BigDecimal valorCorrigido;
    private TipoCorrecaoEnum tipoCorrecao;
}
