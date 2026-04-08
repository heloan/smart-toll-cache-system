package com.stcs.tollmanagement.entity;

import com.stcs.tollmanagement.enums.TipoPistaEnum;
import jakarta.persistence.*;
import lombok.*;
import java.time.LocalDateTime;
import java.util.List;

@Entity
@Table(name = "pista_pedagio",
       uniqueConstraints = @UniqueConstraint(name = "uk_praca_pista", columnNames = {"praca_id", "numero_pista"}))
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class PistaPedagio {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "praca_id", nullable = false)
    private PracaPedagio praca;

    @Column(name = "numero_pista", nullable = false)
    private Integer numeroPista;

    @Enumerated(EnumType.STRING)
    @Column(name = "tipo_pista", nullable = false)
    private TipoPistaEnum tipoPista;

    @Column(length = 20)
    private String sentido;

    @Column(nullable = false)
    private Boolean ativa = true;

    @Column(name = "criado_em", nullable = false, updatable = false)
    private LocalDateTime criadoEm;

    @OneToMany(mappedBy = "pista", cascade = CascadeType.ALL, fetch = FetchType.LAZY)
    private List<TransacaoPedagio> transacoes;

    @PrePersist
    protected void onCreate() {
        criadoEm = LocalDateTime.now();
    }
}
