package com.stcs.tollmanagement.dto;

import java.time.LocalDateTime;

import com.stcs.tollmanagement.entity.Operador;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class OperadorResponseDTO {

    private Long id;
    private String username;
    private String nomeCompleto;
    private String email;
    private String telefone;
    private Boolean ativo;
    private LocalDateTime criadoEm;
    private LocalDateTime atualizadoEm;

    public static OperadorResponseDTO fromEntity(Operador operador) {
        return OperadorResponseDTO.builder()
                .id(operador.getId())
                .username(operador.getUsername())
                .nomeCompleto(operador.getNomeCompleto())
                .email(operador.getEmail())
                .telefone(operador.getTelefone())
                .ativo(operador.getAtivo())
                .criadoEm(operador.getCriadoEm())
                .atualizadoEm(operador.getAtualizadoEm())
                .build();
    }
}
