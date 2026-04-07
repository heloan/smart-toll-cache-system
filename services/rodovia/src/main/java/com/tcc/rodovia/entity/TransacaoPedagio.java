package com.tcc.rodovia.entity;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;

import com.tcc.rodovia.enums.StatusTransacaoEnum;
import com.tcc.rodovia.enums.TipoVeiculoEnum;

import jakarta.persistence.CascadeType;
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
import jakarta.persistence.OneToMany;
import jakarta.persistence.PrePersist;
import jakarta.persistence.Table;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Entity
@Table(name = "transacao_pedagio")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class TransacaoPedagio {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "praca_id", nullable = false)
    private PracaPedagio praca;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "pista_id", nullable = false)
    private PistaPedagio pista;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "tarifa_id", nullable = false)
    private TarifaPedagio tarifa;

    @Column(name = "data_hora_passagem", nullable = false)
    private LocalDateTime dataHoraPassagem;

    @Column(nullable = false, length = 10)
    private String placa;

    @Column(name = "tag_id", length = 40)
    private String tagId;

    @Enumerated(EnumType.STRING)
    @Column(name = "tipo_veiculo", nullable = false)
    private TipoVeiculoEnum tipoVeiculo;

    @Column(name = "valor_original", nullable = false, precision = 10, scale = 2)
    private BigDecimal valorOriginal;

    @Enumerated(EnumType.STRING)
    @Column(name = "status_transacao", nullable = false)
    private StatusTransacaoEnum statusTransacao;

    @Column(name = "hash_integridade", nullable = false, length = 128)
    private String hashIntegridade;

    @Column(name = "criado_em", nullable = false, updatable = false)
    private LocalDateTime criadoEm;

    @OneToMany(mappedBy = "transacao", cascade = CascadeType.ALL, fetch = FetchType.LAZY)
    private List<OcorrenciaTransacao> ocorrencias;

    @OneToMany(mappedBy = "transacao", cascade = CascadeType.ALL, fetch = FetchType.LAZY)
    private List<CorrecaoTransacao> correcoes;

    @PrePersist
    protected void onCreate() {
        criadoEm = LocalDateTime.now();
    }
}
