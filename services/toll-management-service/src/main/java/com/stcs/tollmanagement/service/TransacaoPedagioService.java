package com.stcs.tollmanagement.service;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import com.stcs.tollmanagement.dto.TransacaoPedagioResponseDTO;
import com.stcs.tollmanagement.entity.TransacaoPedagio;
import com.stcs.tollmanagement.enums.OrigemDadosEnum;
import com.stcs.tollmanagement.enums.StatusTransacaoEnum;
import com.stcs.tollmanagement.repository.TransacaoPedagioRepository;
import com.stcs.tollmanagement.util.OrigemDadosMarker;

import lombok.RequiredArgsConstructor;

@Service
@RequiredArgsConstructor
public class TransacaoPedagioService {

    private final TransacaoPedagioRepository transacaoPedagioRepository;
    private final OrigemDadosMarker origemDadosMarker;
    private final CacheService cacheService;

    @Transactional(readOnly = true)
    public List<TransacaoPedagioResponseDTO> listarTodas(Integer limite) {
        origemDadosMarker.marcarBancoDados();
        
        Pageable pageable = limite != null && limite > 0 
            ? PageRequest.of(0, limite) 
            : PageRequest.of(0, 1000);
        
        return transacaoPedagioRepository.findAllWithRelations(pageable).stream()
                .map(TransacaoPedagioResponseDTO::fromEntity)
                .collect(Collectors.toList());
    }

    @Transactional(readOnly = true)
    public TransacaoPedagioResponseDTO buscarPorId(Long id) {
        origemDadosMarker.marcarBancoDados();
        
        TransacaoPedagio transacao = transacaoPedagioRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("Transação não encontrada"));
        
        return TransacaoPedagioResponseDTO.fromEntityWithOcorrencias(transacao);
    }

    @Transactional(readOnly = true)
    public List<TransacaoPedagioResponseDTO> listarTransacoesComOcorrenciasParaCorrigir(
            Integer limite, Integer horasMaximas, OrigemDadosEnum origemDados) {
        
        // Gerar chave de cache
        String cacheKey = cacheService.generateKey("transacoes:ocorrencias", limite, horasMaximas);
        
        // Calcular data de início baseado nas horas máximas
        LocalDateTime dataInicio = horasMaximas != null && horasMaximas > 0
            ? LocalDateTime.now().minusHours(horasMaximas)
            : LocalDateTime.now().minusDays(30);
        
        Pageable pageable = limite != null && limite > 0 
            ? PageRequest.of(0, limite) 
            : PageRequest.of(0, 100);
        
        List<TransacaoPedagio> transacoes = null;
        List<Map<String, Object>> cachedData = null;
        
        // Estratégia de busca baseada na origem de dados solicitada
        if (origemDados == null || origemDados == OrigemDadosEnum.BANCO_DADOS) {
            //  Buscar no banco de dados
            origemDadosMarker.marcarBancoDados();
            transacoes = buscarTransacoesNoBanco(pageable, dataInicio);
            
        } else if (origemDados == OrigemDadosEnum.CACHE_LOCAL) {
            // Forçar uso do cache local
            cachedData = cacheService.getFromLocalCache(cacheKey);
            if (cachedData != null) {
                origemDadosMarker.marcarCacheLocal();
                return convertMapListToDTO(cachedData);
            }
            
            // Se não encontrou, buscar no banco e atualizar cache local
            origemDadosMarker.marcarBancoDados();
            transacoes = buscarTransacoesNoBanco(pageable, dataInicio);
            List<Map<String, Object>> dataToCache = convertToMapList(transacoes);
            cacheService.putInLocalCache(cacheKey, dataToCache);
            
        } else if (origemDados == OrigemDadosEnum.CACHE_REDIS) {
            // Forçar uso do cache Redis
            cachedData = cacheService.getFromRedisCache(cacheKey);
            if (cachedData != null) {
                origemDadosMarker.marcarCacheRedis();
                return convertMapListToDTO(cachedData);
            }
            
            // Se não encontrou, buscar no banco e atualizar cache Redis
            origemDadosMarker.marcarBancoDados();
            transacoes = buscarTransacoesNoBanco(pageable, dataInicio);
            List<Map<String, Object>> dataToCache = convertToMapList(transacoes);
            cacheService.putInRedisCache(cacheKey, dataToCache);
        }
        
        return transacoes.stream()
                .map(TransacaoPedagioResponseDTO::fromEntityWithOcorrencias)
                .collect(Collectors.toList());
    }
    
    /**
     * Busca transações no banco de dados
     */
    private List<TransacaoPedagio> buscarTransacoesNoBanco(Pageable pageable, LocalDateTime dataInicio) {
        // Buscar transações com ocorrências que ainda não foram corrigidas (status OCORRENCIA)
        List<TransacaoPedagio> transacoes = transacaoPedagioRepository
                .findTransacoesComOcorrenciasSemCorrecao(StatusTransacaoEnum.OCORRENCIA, pageable);
        
        // Se não encontrou com ocorrências sem correção, buscar todas com ocorrências recentes
        if (transacoes.isEmpty()) {
            transacoes = transacaoPedagioRepository
                    .findTransacoesComOcorrenciasRecentes(dataInicio, pageable);
        }
        
        return transacoes;
    }
    
    /**
     * Converte transações para List<Map>
     */
    private List<Map<String, Object>> convertToMapList(List<TransacaoPedagio> transacoes) {
        return transacoes.stream()
                .map(this::transacaoToMap)
                .collect(Collectors.toList());
    }
    
    /**
     * Converte uma transação para Map
     */
    private Map<String, Object> transacaoToMap(TransacaoPedagio t) {
        Map<String, Object> map = new HashMap<>();
        map.put("id", t.getId());
        map.put("pracaId", t.getPraca().getId());
        map.put("pracaNome", t.getPraca().getNome());
        map.put("pistaId", t.getPista().getId());
        map.put("pistaNumeroPista", t.getPista().getNumeroPista());
        map.put("dataHoraPassagem", t.getDataHoraPassagem().toString());
        map.put("placa", t.getPlaca());
        map.put("tipoVeiculo", t.getTipoVeiculo().name());
        map.put("valorOriginal", t.getValorOriginal().toString());
        map.put("statusTransacao", t.getStatusTransacao().name());
        map.put("quantidadeOcorrencias", t.getOcorrencias() != null ? t.getOcorrencias().size() : 0);
        return map;
    }
    
    /**
     * Converte List<Map> de volta para DTOs
     */
    private List<TransacaoPedagioResponseDTO> convertMapListToDTO(List<Map<String, Object>> mapList) {
        // Para dados do cache, retornar os IDs para que o frontend possa fazer requisições individuais
        // se precisar de mais detalhes
        return mapList.stream()
                .map(map -> {
                    TransacaoPedagioResponseDTO dto = new TransacaoPedagioResponseDTO();
                    dto.setId(((Number) map.get("id")).longValue());
                    dto.setPracaId(((Number) map.get("pracaId")).longValue());
                    dto.setPracaNome((String) map.get("pracaNome"));
                    dto.setPistaId(((Number) map.get("pistaId")).longValue());
                    dto.setPistaNumeroPista(((Number) map.get("pistaNumeroPista")).intValue());
                    dto.setDataHoraPassagem(java.time.LocalDateTime.parse((String) map.get("dataHoraPassagem")));
                    dto.setPlaca((String) map.get("placa"));
                    dto.setTipoVeiculo(com.stcs.tollmanagement.enums.TipoVeiculoEnum.valueOf((String) map.get("tipoVeiculo")));
                    dto.setValorOriginal(new java.math.BigDecimal((String) map.get("valorOriginal")));
                    dto.setStatusTransacao(StatusTransacaoEnum.valueOf((String) map.get("statusTransacao")));
                    dto.setQuantidadeOcorrencias(((Number) map.get("quantidadeOcorrencias")).intValue());
                    return dto;
                })
                .collect(Collectors.toList());
    }

    @Transactional(readOnly = true)
    public List<TransacaoPedagioResponseDTO> listarPorStatus(StatusTransacaoEnum status) {
        origemDadosMarker.marcarBancoDados();
        
        return transacaoPedagioRepository.findByStatusTransacao(status).stream()
                .map(TransacaoPedagioResponseDTO::fromEntity)
                .collect(Collectors.toList());
    }
}
