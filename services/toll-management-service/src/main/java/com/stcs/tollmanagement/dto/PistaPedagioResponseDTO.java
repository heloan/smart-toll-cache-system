package com.stcs.tollmanagement.dto;

import java.time.LocalDateTime;

import com.stcs.tollmanagement.entity.PistaPedagio;
import com.stcs.tollmanagement.enums.TipoPistaEnum;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class PistaPedagioResponseDTO {

    private Long id;
    private Long pracaId;
    private String pracaNome;
    private Integer numeroPista;
    private TipoPistaEnum tipoPista;
    private String sentido;
    private Boolean ativa;
    private LocalDateTime criadoEm;

    public static PistaPedagioResponseDTO fromEntity(PistaPedagio pista) {
        return PistaPedagioResponseDTO.builder()
                .id(pista.getId())
                .pracaId(pista.getPraca().getId())
                .pracaNome(pista.getPraca().getNome())
                .numeroPista(pista.getNumeroPista())
                .tipoPista(pista.getTipoPista())
                .sentido(pista.getSentido())
                .ativa(pista.getAtiva())
                .criadoEm(pista.getCriadoEm())
                .build();
    }
}
