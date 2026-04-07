package com.tcc.rodovia.entity;

import jakarta.persistence.*;
import lombok.*;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;

@Entity
@Table(name = "concessionaria")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Concessionaria {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "nome_fantasia", nullable = false, length = 120)
    private String nomeFantasia;

    @Column(name = "razao_social", nullable = false, length = 160)
    private String razaoSocial;

    @Column(nullable = false, unique = true, length = 14)
    private String cnpj;

    @Column(name = "contrato_concessao", length = 60)
    private String contratoConcessao;

    @Column(name = "data_inicio_contrato", nullable = false)
    private LocalDate dataInicioContrato;

    @Column(name = "data_fim_contrato")
    private LocalDate dataFimContrato;

    @Column(nullable = false)
    private Boolean ativo = true;

    @Column(name = "criado_em", nullable = false, updatable = false)
    private LocalDateTime criadoEm;

    @OneToMany(mappedBy = "concessionaria", cascade = CascadeType.ALL, fetch = FetchType.LAZY)
    private List<Rodovia> rodovias;

    @PrePersist
    protected void onCreate() {
        criadoEm = LocalDateTime.now();
    }
}
