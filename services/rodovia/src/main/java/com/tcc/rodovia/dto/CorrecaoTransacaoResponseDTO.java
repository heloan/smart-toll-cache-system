package com.tcc.rodovia.dto;

import java.math.BigDecimal;
import java.time.LocalDateTime;

import com.tcc.rodovia.entity.CorrecaoTransacao;
import com.tcc.rodovia.enums.TipoCorrecaoEnum;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class CorrecaoTransacaoResponseDTO {

    private Long id;
    private Long transacaoId;
    private Long operadorId;
    private String operadorNome;
    private String motivo;
    private BigDecimal valorAnterior;
    private BigDecimal valorCorrigido;
    private TipoCorrecaoEnum tipoCorrecao;
    private LocalDateTime criadoEm;

    public static CorrecaoTransacaoResponseDTO fromEntity(CorrecaoTransacao correcao) {
        return CorrecaoTransacaoResponseDTO.builder()
                .id(correcao.getId())
                .transacaoId(correcao.getTransacao().getId())
                .operadorId(correcao.getOperador().getId())
                .operadorNome(correcao.getOperador().getNomeCompleto())
                .motivo(correcao.getMotivo())
                .valorAnterior(correcao.getValorAnterior())
                .valorCorrigido(correcao.getValorCorrigido())
                .tipoCorrecao(correcao.getTipoCorrecao())
                .criadoEm(correcao.getCriadoEm())
                .build();
    }
}
