package com.tcc.rodovia.dto;

import java.math.BigDecimal;
import java.time.LocalDateTime;

import com.tcc.rodovia.entity.Rodovia;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class RodoviaResponseDTO {

    private Long id;
    private Long concessionariaId;
    private String concessionariaNome;
    private String codigo;
    private String nome;
    private String uf;
    private BigDecimal extensaoKm;
    private Boolean ativa;
    private LocalDateTime criadoEm;

    public static RodoviaResponseDTO fromEntity(Rodovia rodovia) {
        return RodoviaResponseDTO.builder()
                .id(rodovia.getId())
                .concessionariaId(rodovia.getConcessionaria().getId())
                .concessionariaNome(rodovia.getConcessionaria().getNomeFantasia())
                .codigo(rodovia.getCodigo())
                .nome(rodovia.getNome())
                .uf(rodovia.getUf())
                .extensaoKm(rodovia.getExtensaoKm())
                .ativa(rodovia.getAtiva())
                .criadoEm(rodovia.getCriadoEm())
                .build();
    }
}
