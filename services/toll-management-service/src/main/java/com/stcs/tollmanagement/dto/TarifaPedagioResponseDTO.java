package com.stcs.tollmanagement.dto;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;

import com.stcs.tollmanagement.entity.TarifaPedagio;
import com.stcs.tollmanagement.enums.TipoVeiculoEnum;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class TarifaPedagioResponseDTO {

    private Long id;
    private TipoVeiculoEnum tipoVeiculo;
    private BigDecimal valor;
    private LocalDate vigenciaInicio;
    private LocalDate vigenciaFim;
    private LocalDateTime criadoEm;
    private Boolean vigente;

    public static TarifaPedagioResponseDTO fromEntity(TarifaPedagio tarifa) {
        LocalDate hoje = LocalDate.now();
        boolean vigente = !tarifa.getVigenciaInicio().isAfter(hoje) && 
                         (tarifa.getVigenciaFim() == null || !tarifa.getVigenciaFim().isBefore(hoje));
        
        return TarifaPedagioResponseDTO.builder()
                .id(tarifa.getId())
                .tipoVeiculo(tarifa.getTipoVeiculo())
                .valor(tarifa.getValor())
                .vigenciaInicio(tarifa.getVigenciaInicio())
                .vigenciaFim(tarifa.getVigenciaFim())
                .criadoEm(tarifa.getCriadoEm())
                .vigente(vigente)
                .build();
    }
}
