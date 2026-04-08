package com.stcs.tollmanagement.dto;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;
import java.util.stream.Collectors;

import com.stcs.tollmanagement.entity.TransacaoPedagio;
import com.stcs.tollmanagement.enums.StatusTransacaoEnum;
import com.stcs.tollmanagement.enums.TipoVeiculoEnum;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class TransacaoPedagioResponseDTO {

    private Long id;
    private Long pracaId;
    private String pracaNome;
    private Long pistaId;
    private Integer pistaNumeroPista;
    private Long tarifaId;
    private LocalDateTime dataHoraPassagem;
    private String placa;
    private String tagId;
    private TipoVeiculoEnum tipoVeiculo;
    private BigDecimal valorOriginal;
    private StatusTransacaoEnum statusTransacao;
    private String hashIntegridade;
    private LocalDateTime criadoEm;
    private Integer quantidadeOcorrencias;
    private Integer quantidadeCorrecoes;
    private List<OcorrenciaTransacaoResponseDTO> ocorrencias;

    public static TransacaoPedagioResponseDTO fromEntity(TransacaoPedagio transacao) {
        return TransacaoPedagioResponseDTO.builder()
                .id(transacao.getId())
                .pracaId(transacao.getPraca().getId())
                .pracaNome(transacao.getPraca().getNome())
                .pistaId(transacao.getPista().getId())
                .pistaNumeroPista(transacao.getPista().getNumeroPista())
                .tarifaId(transacao.getTarifa().getId())
                .dataHoraPassagem(transacao.getDataHoraPassagem())
                .placa(transacao.getPlaca())
                .tagId(transacao.getTagId())
                .tipoVeiculo(transacao.getTipoVeiculo())
                .valorOriginal(transacao.getValorOriginal())
                .statusTransacao(transacao.getStatusTransacao())
                .hashIntegridade(transacao.getHashIntegridade())
                .criadoEm(transacao.getCriadoEm())
                .quantidadeOcorrencias(transacao.getOcorrencias() != null ? transacao.getOcorrencias().size() : 0)
                .quantidadeCorrecoes(transacao.getCorrecoes() != null ? transacao.getCorrecoes().size() : 0)
                .build();
    }

    public static TransacaoPedagioResponseDTO fromEntityWithOcorrencias(TransacaoPedagio transacao) {
        TransacaoPedagioResponseDTO dto = fromEntity(transacao);
        if (transacao.getOcorrencias() != null && !transacao.getOcorrencias().isEmpty()) {
            dto.setOcorrencias(
                transacao.getOcorrencias().stream()
                    .map(OcorrenciaTransacaoResponseDTO::fromEntity)
                    .collect(Collectors.toList())
            );
        }
        return dto;
    }
}
