package com.tcc.rodovia.entity;

import java.time.LocalDateTime;

import com.tcc.rodovia.enums.OrigemDadosEnum;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.PrePersist;
import jakarta.persistence.Table;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Entity
@Table(name = "registro_performance")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class RegistroPerformance {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "endpoint", nullable = false, length = 255)
    private String endpoint;

    @Column(name = "metodo_http", nullable = false, length = 10)
    private String metodoHttp;

    @Column(name = "tempo_processamento_ms", nullable = false)
    private Long tempoProcessamentoMs;

    @Column(name = "memoria_usada_mb", nullable = false)
    private Double memoriaUsadaMb;

    @Column(name = "memoria_livre_mb", nullable = false)
    private Double memoriaLivreMb;

    @Column(name = "memoria_total_mb", nullable = false)
    private Double memoriaTotalMb;

    @Column(name = "uso_cpu_processo", nullable = false)
    private Double usoCpuProcesso;

    @Column(name = "threads_ativas", nullable = false)
    private Integer threadsAtivas;

    @Column(name = "status_http", nullable = false)
    private Integer statusHttp;

    @Column(name = "ip_cliente", length = 45)
    private String ipCliente;

    @Column(name = "user_agent", length = 255)
    private String userAgent;

    @Column(name = "parametros", columnDefinition = "TEXT")
    private String parametros;

    @Column(name = "erro", columnDefinition = "TEXT")
    private String erro;

    @Enumerated(EnumType.STRING)
    @Column(name = "origem_dados", length = 20)
    private OrigemDadosEnum origemDados;

    @Column(name = "criado_em", nullable = false, updatable = false)
    private LocalDateTime criadoEm;

    @PrePersist
    protected void onCreate() {
        criadoEm = LocalDateTime.now();
    }
}
