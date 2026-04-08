package com.stcs.tollmanagement.dto;

import java.time.LocalDateTime;

import com.stcs.tollmanagement.entity.OcorrenciaTransacao;
import com.stcs.tollmanagement.enums.TipoOcorrenciaEnum;

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
