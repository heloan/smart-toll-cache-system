package com.tcc.rodovia.dto;

import java.time.LocalDate;
import java.time.LocalDateTime;

import com.tcc.rodovia.entity.Concessionaria;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ConcessionariaResponseDTO {

    private Long id;
    private String nomeFantasia;
    private String razaoSocial;
    private String cnpj;
    private String contratoConcessao;
    private LocalDate dataInicioContrato;
    private LocalDate dataFimContrato;
    private Boolean ativo;
    private LocalDateTime criadoEm;

    public static ConcessionariaResponseDTO fromEntity(Concessionaria concessionaria) {
        return ConcessionariaResponseDTO.builder()
                .id(concessionaria.getId())
                .nomeFantasia(concessionaria.getNomeFantasia())
                .razaoSocial(concessionaria.getRazaoSocial())
                .cnpj(concessionaria.getCnpj())
                .contratoConcessao(concessionaria.getContratoConcessao())
                .dataInicioContrato(concessionaria.getDataInicioContrato())
                .dataFimContrato(concessionaria.getDataFimContrato())
                .ativo(concessionaria.getAtivo())
                .criadoEm(concessionaria.getCriadoEm())
                .build();
    }
}
