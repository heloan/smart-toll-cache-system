package com.tcc.rodovia.entity;

import jakarta.persistence.*;
import lombok.*;
import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;

@Entity
@Table(name = "rodovia")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Rodovia {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "concessionaria_id", nullable = false)
    private Concessionaria concessionaria;

    @Column(nullable = false, length = 20)
    private String codigo;

    @Column(length = 120)
    private String nome;

    @Column(nullable = false, length = 2)
    private String uf;

    @Column(name = "extensao_km", precision = 8, scale = 2)
    private BigDecimal extensaoKm;

    @Column(nullable = false)
    private Boolean ativa = true;

    @Column(name = "criado_em", nullable = false, updatable = false)
    private LocalDateTime criadoEm;

    @OneToMany(mappedBy = "rodovia", cascade = CascadeType.ALL, fetch = FetchType.LAZY)
    private List<PracaPedagio> pracasPedagio;

    @PrePersist
    protected void onCreate() {
        criadoEm = LocalDateTime.now();
    }
}
