package com.tcc.rodovia.entity;

import jakarta.persistence.*;
import lombok.*;
import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;

@Entity
@Table(name = "praca_pedagio")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class PracaPedagio {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "rodovia_id", nullable = false)
    private Rodovia rodovia;

    @Column(length = 120)
    private String nome;

    @Column(nullable = false, precision = 8, scale = 3)
    private BigDecimal km;

    @Column(length = 20)
    private String sentido;

    @Column(nullable = false)
    private Boolean ativa = true;

    @Column(name = "criado_em", nullable = false, updatable = false)
    private LocalDateTime criadoEm;

    @OneToMany(mappedBy = "praca", cascade = CascadeType.ALL, fetch = FetchType.LAZY)
    private List<PistaPedagio> pistas;

    @OneToMany(mappedBy = "praca", cascade = CascadeType.ALL, fetch = FetchType.LAZY)
    private List<TransacaoPedagio> transacoes;

    @PrePersist
    protected void onCreate() {
        criadoEm = LocalDateTime.now();
    }
}
