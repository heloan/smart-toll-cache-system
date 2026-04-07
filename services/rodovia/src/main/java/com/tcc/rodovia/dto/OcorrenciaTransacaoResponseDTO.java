package com.tcc.rodovia.dto;

import java.time.LocalDateTime;

import com.tcc.rodovia.entity.OcorrenciaTransacao;
import com.tcc.rodovia.enums.TipoOcorrenciaEnum;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class OcorrenciaTransacaoResponseDTO {

    private Long id;
    private Long transacaoId;
    private TipoOcorrenciaEnum tipoOcorrencia;
    private String observacao;
    private Boolean detectadaAutomaticamente;
    private LocalDateTime criadoEm;

    public static OcorrenciaTransacaoResponseDTO fromEntity(OcorrenciaTransacao ocorrencia) {
        return OcorrenciaTransacaoResponseDTO.builder()
                .id(ocorrencia.getId())
                .transacaoId(ocorrencia.getTransacao().getId())
                .tipoOcorrencia(ocorrencia.getTipoOcorrencia())
                .observacao(ocorrencia.getObservacao())
                .detectadaAutomaticamente(ocorrencia.getDetectadaAutomaticamente())
                .criadoEm(ocorrencia.getCriadoEm())
                .build();
    }
}
