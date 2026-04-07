package com.tcc.rodovia.entity;

import java.math.BigDecimal;
import java.time.LocalDateTime;

import com.tcc.rodovia.enums.TipoCorrecaoEnum;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.FetchType;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.PrePersist;
import jakarta.persistence.Table;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Entity
@Table(name = "correcao_transacao")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class CorrecaoTransacao {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "transacao_id", nullable = false)
    private TransacaoPedagio transacao;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "operador_id", nullable = false)
    private Operador operador;

    @Column(nullable = false, columnDefinition = "TEXT")
    private String motivo;

    @Column(name = "valor_anterior", nullable = false, precision = 10, scale = 2)
    private BigDecimal valorAnterior;

    @Column(name = "valor_corrigido", nullable = false, precision = 10, scale = 2)
    private BigDecimal valorCorrigido;

    @Enumerated(EnumType.STRING)
    @Column(name = "tipo_correcao", nullable = false)
    private TipoCorrecaoEnum tipoCorrecao;

    @Column(name = "criado_em", nullable = false, updatable = false)
    private LocalDateTime criadoEm;

    @PrePersist
    protected void onCreate() {
        criadoEm = LocalDateTime.now();
    }
}
