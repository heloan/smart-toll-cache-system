package com.stcs.tollmanagement.dto;

import java.time.LocalDate;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ConcessionariaRequestDTO {

    @NotBlank(message = "Nome fantasia é obrigatório")
    @Size(max = 120, message = "Nome fantasia deve ter no máximo 120 caracteres")
    private String nomeFantasia;

    @NotBlank(message = "Razão social é obrigatória")
    @Size(max = 160, message = "Razão social deve ter no máximo 160 caracteres")
    private String razaoSocial;

    @NotBlank(message = "CNPJ é obrigatório")
    @Pattern(regexp = "\\d{14}", message = "CNPJ deve conter 14 dígitos")
    private String cnpj;

    @Size(max = 60, message = "Contrato de concessão deve ter no máximo 60 caracteres")
    private String contratoConcessao;

    @NotNull(message = "Data de início do contrato é obrigatória")
    private LocalDate dataInicioContrato;

    private LocalDate dataFimContrato;

    private Boolean ativo;
}
