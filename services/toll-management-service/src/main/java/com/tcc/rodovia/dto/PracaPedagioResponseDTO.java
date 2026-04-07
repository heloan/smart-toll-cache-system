package com.tcc.rodovia.dto;

import java.math.BigDecimal;
import java.time.LocalDateTime;

import com.tcc.rodovia.entity.PracaPedagio;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class PracaPedagioResponseDTO {

    private Long id;
    private Long rodoviaId;
    private String rodoviaNome;
    private String nome;
    private BigDecimal km;
    private String sentido;
    private Boolean ativa;
    private LocalDateTime criadoEm;

    public static PracaPedagioResponseDTO fromEntity(PracaPedagio praca) {
        return PracaPedagioResponseDTO.builder()
                .id(praca.getId())
                .rodoviaId(praca.getRodovia().getId())
                .rodoviaNome(praca.getRodovia().getNome() != null ? praca.getRodovia().getNome() : praca.getRodovia().getCodigo())
                .nome(praca.getNome())
                .km(praca.getKm())
                .sentido(praca.getSentido())
                .ativa(praca.getAtiva())
                .criadoEm(praca.getCriadoEm())
                .build();
    }
}
