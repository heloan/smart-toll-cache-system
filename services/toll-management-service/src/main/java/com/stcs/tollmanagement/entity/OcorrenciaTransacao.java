package com.stcs.tollmanagement.entity;

import com.stcs.tollmanagement.enums.TipoOcorrenciaEnum;
import jakarta.persistence.*;
import lombok.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "ocorrencia_transacao")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class OcorrenciaTransacao {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "transacao_id", nullable = false)
    private TransacaoPedagio transacao;

    @Enumerated(EnumType.STRING)
    @Column(name = "tipo_ocorrencia", nullable = false)
    private TipoOcorrenciaEnum tipoOcorrencia;

    @Column(columnDefinition = "TEXT")
    private String observacao;

    @Column(name = "detectada_automaticamente", nullable = false)
    private Boolean detectadaAutomaticamente = true;

    @Column(name = "criado_em", nullable = false, updatable = false)
    private LocalDateTime criadoEm;

    @PrePersist
    protected void onCreate() {
        criadoEm = LocalDateTime.now();
    }
}
