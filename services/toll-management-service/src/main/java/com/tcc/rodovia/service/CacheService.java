package com.tcc.rodovia.service;

import java.time.Duration;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.TimeUnit;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Service;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

@Service
@RequiredArgsConstructor
@Slf4j
public class CacheService {

    private final RedisTemplate<String, Object> redisTemplate;

    // Cache local usando ConcurrentHashMap para thread-safety
    private final Map<String, CacheEntry> localCache = new ConcurrentHashMap<>();

    @Value("${cache.local.max-size:1000}")
    private int maxLocalCacheSize;

    @Value("${cache.local.ttl-minutes:30}")
    private long localCacheTtlMinutes;

    @Value("${cache.redis.ttl-minutes:60}")
    private long redisCacheTtlMinutes;

    /**
     * Estrutura para armazenar entrada no cache local com tempo de expiração
     */
    private static class CacheEntry {
        private final Object data;
        private final long expirationTime;

        public CacheEntry(Object data, long ttlMillis) {
            this.data = data;
            this.expirationTime = System.currentTimeMillis() + ttlMillis;
        }

        public boolean isExpired() {
            return System.currentTimeMillis() > expirationTime;
        }

        public Object getData() {
            return data;
        }
    }

    /**
     * Busca no cache local
     */
    @SuppressWarnings("unchecked")
    public <T> List<Map<String, Object>> getFromLocalCache(String key) {
        CacheEntry entry = localCache.get(key);
        
        if (entry != null && !entry.isExpired()) {
            log.debug("Cache LOCAL HIT para chave: {}", key);
            return (List<Map<String, Object>>) entry.getData();
        }
        
        // Remover entrada expirada
        if (entry != null && entry.isExpired()) {
            localCache.remove(key);
            log.debug("Cache LOCAL EXPIRED para chave: {}", key);
        }
        
        log.debug("Cache LOCAL MISS para chave: {}", key);
        return null;
    }

    /**
     * Salva no cache local
     */
    public void putInLocalCache(String key, List<Map<String, Object>> data) {
        // Limpar cache se atingir tamanho máximo
        if (localCache.size() >= maxLocalCacheSize) {
            clearExpiredLocalCache();
            
            // Se ainda estiver cheio, remover entradas mais antigas
            if (localCache.size() >= maxLocalCacheSize) {
                localCache.keySet().stream()
                    .findFirst()
                    .ifPresent(localCache::remove);
            }
        }
        
        long ttlMillis = TimeUnit.MINUTES.toMillis(localCacheTtlMinutes);
        localCache.put(key, new CacheEntry(data, ttlMillis));
        log.debug("Cache LOCAL SAVE para chave: {} com TTL de {} minutos", key, localCacheTtlMinutes);
    }

    /**
     * Busca no cache Redis
     */
    @SuppressWarnings("unchecked")
    public List<Map<String, Object>> getFromRedisCache(String key) {
        try {
            Object data = redisTemplate.opsForValue().get(key);
            if (data != null) {
                log.debug("Cache REDIS HIT para chave: {}", key);
                return (List<Map<String, Object>>) data;
            }
            log.debug("Cache REDIS MISS para chave: {}", key);
            return null;
        } catch (Exception e) {
            log.error("Erro ao buscar no cache Redis: {}", e.getMessage());
            return null;
        }
    }

    /**
     * Salva no cache Redis
     */
    public void putInRedisCache(String key, List<Map<String, Object>> data) {
        try {
            redisTemplate.opsForValue().set(
                key, 
                data, 
                Duration.ofMinutes(redisCacheTtlMinutes)
            );
            log.debug("Cache REDIS SAVE para chave: {} com TTL de {} minutos", key, redisCacheTtlMinutes);
        } catch (Exception e) {
            log.error("Erro ao salvar no cache Redis: {}", e.getMessage());
        }
    }

    /**
     * Converte lista de entidades para List<Map<String, Object>>
     */
    public <T> List<Map<String, Object>> convertToMapList(List<T> entities) {
        List<Map<String, Object>> result = new ArrayList<>();
        
        for (T entity : entities) {
            Map<String, Object> map = new HashMap<>();
            
            // Usar reflexão para converter entidade em Map
            try {
                java.lang.reflect.Field[] fields = entity.getClass().getDeclaredFields();
                for (java.lang.reflect.Field field : fields) {
                    field.setAccessible(true);
                    Object value = field.get(entity);
                    
                    // Evitar serializar campos complexos (OneToMany, ManyToOne, etc)
                    if (value != null && isSimpleType(value.getClass())) {
                        map.put(field.getName(), value);
                    }
                }
            } catch (Exception e) {
                log.error("Erro ao converter entidade para Map: {}", e.getMessage());
            }
            
            result.add(map);
        }
        
        return result;
    }

    /**
     * Verifica se é um tipo simples que pode ser serializado
     */
    private boolean isSimpleType(Class<?> type) {
        return type.isPrimitive() ||
               type.equals(String.class) ||
               type.equals(Boolean.class) ||
               type.equals(Integer.class) ||
               type.equals(Long.class) ||
               type.equals(Double.class) ||
               type.equals(Float.class) ||
               type.equals(java.math.BigDecimal.class) ||
               type.equals(java.time.LocalDate.class) ||
               type.equals(java.time.LocalDateTime.class) ||
               type.isEnum();
    }

    /**
     * Limpa entradas expiradas do cache local
     */
    public void clearExpiredLocalCache() {
        localCache.entrySet().removeIf(entry -> entry.getValue().isExpired());
        log.debug("Cache LOCAL limpo - entradas expiradas removidas");
    }

    /**
     * Limpa todo o cache local
     */
    public void clearLocalCache() {
        localCache.clear();
        log.info("Cache LOCAL completamente limpo");
    }

    /**
     * Invalida uma chave específica em todos os caches
     */
    public void invalidate(String key) {
        localCache.remove(key);
        try {
            redisTemplate.delete(key);
            log.info("Cache invalidado para chave: {}", key);
        } catch (Exception e) {
            log.error("Erro ao invalidar cache Redis: {}", e.getMessage());
        }
    }

    /**
     * Gera chave de cache baseada em parâmetros
     */
    public String generateKey(String prefix, Object... params) {
        StringBuilder key = new StringBuilder(prefix);
        for (Object param : params) {
            key.append(":").append(param != null ? param.toString() : "null");
        }
        return key.toString();
    }
}
