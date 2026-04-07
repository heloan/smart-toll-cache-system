package com.tcc.rodovia.config;

import java.util.HashMap;
import java.util.Map;

import org.apache.kafka.clients.admin.AdminClientConfig;
import org.apache.kafka.clients.admin.NewTopic;
import org.apache.kafka.clients.consumer.ConsumerConfig;
import org.apache.kafka.clients.producer.ProducerConfig;
import org.apache.kafka.common.serialization.StringDeserializer;
import org.apache.kafka.common.serialization.StringSerializer;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.kafka.annotation.EnableKafka;
import org.springframework.kafka.config.ConcurrentKafkaListenerContainerFactory;
import org.springframework.kafka.core.ConsumerFactory;
import org.springframework.kafka.core.DefaultKafkaConsumerFactory;
import org.springframework.kafka.core.DefaultKafkaProducerFactory;
import org.springframework.kafka.core.KafkaAdmin;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.kafka.core.ProducerFactory;
import org.springframework.kafka.support.serializer.ErrorHandlingDeserializer;
import org.springframework.kafka.support.serializer.JsonDeserializer;
import org.springframework.kafka.support.serializer.JsonSerializer;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;
import com.tcc.rodovia.dto.TransacaoPedagioKafkaDTO;

/**
 * Configuração do Apache Kafka para mensageria de transações
 */
@Configuration
@EnableKafka
public class KafkaConfig {

    @Value("${spring.kafka.bootstrap-servers}")
    private String bootstrapServers;

    @Value("${spring.kafka.consumer.group-id}")
    private String groupId;

    @Value("${kafka.topic.transacao-pedagio}")
    private String transacaoTopic;

    @Value("${kafka.topic.transacao-pedagio.partitions:3}")
    private int partitions;

    @Value("${kafka.topic.transacao-pedagio.replication:1}")
    private short replication;

    /**
     * Configuração do Kafka Admin para gerenciar tópicos
     */
    @Bean
    public KafkaAdmin kafkaAdmin() {
        Map<String, Object> configs = new HashMap<>();
        configs.put(AdminClientConfig.BOOTSTRAP_SERVERS_CONFIG, bootstrapServers);
        return new KafkaAdmin(configs);
    }

    /**
     * Criação do tópico de transações de pedágio
     */
    @Bean
    public NewTopic transacaoPedagioTopic() {
        return new NewTopic(transacaoTopic, partitions, replication);
    }

    /**
     * ObjectMapper configurado para serialização JSON
     */
    @Bean
    public ObjectMapper objectMapper() {
        ObjectMapper mapper = new ObjectMapper();
        mapper.registerModule(new JavaTimeModule());
        return mapper;
    }

    /**
     * Configuração do Producer Factory
     */
    @Bean
    public ProducerFactory<String, TransacaoPedagioKafkaDTO> producerFactory(ObjectMapper objectMapper) {
        Map<String, Object> configProps = new HashMap<>();
        configProps.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, bootstrapServers);
        configProps.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class);
        configProps.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, JsonSerializer.class);
        configProps.put(ProducerConfig.ACKS_CONFIG, "all");
        configProps.put(ProducerConfig.RETRIES_CONFIG, 3);
        configProps.put(ProducerConfig.ENABLE_IDEMPOTENCE_CONFIG, true);
        configProps.put(JsonSerializer.ADD_TYPE_INFO_HEADERS, false);
        
        return new DefaultKafkaProducerFactory<>(configProps, 
            new StringSerializer(), 
            new JsonSerializer<>(objectMapper));
    }

    /**
     * KafkaTemplate para enviar mensagens
     */
    @Bean
    public KafkaTemplate<String, TransacaoPedagioKafkaDTO> kafkaTemplate(ObjectMapper objectMapper) {
        return new KafkaTemplate<>(producerFactory(objectMapper));
    }

    /**
     * Configuração do Consumer Factory
     */
    @Bean
    public ConsumerFactory<String, TransacaoPedagioKafkaDTO> consumerFactory(ObjectMapper objectMapper) {
        JsonDeserializer<TransacaoPedagioKafkaDTO> jsonDeserializer = 
            new JsonDeserializer<>(TransacaoPedagioKafkaDTO.class, objectMapper);
        jsonDeserializer.addTrustedPackages("*");
        jsonDeserializer.setUseTypeHeaders(false);
        
        Map<String, Object> props = new HashMap<>();
        props.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, bootstrapServers);
        props.put(ConsumerConfig.GROUP_ID_CONFIG, groupId);
        props.put(ConsumerConfig.AUTO_OFFSET_RESET_CONFIG, "earliest");
        
        return new DefaultKafkaConsumerFactory<>(props, 
            new StringDeserializer(), 
            new ErrorHandlingDeserializer<>(jsonDeserializer));
    }

    /**
     * Container Factory para listeners Kafka
     */
    @Bean
    public ConcurrentKafkaListenerContainerFactory<String, TransacaoPedagioKafkaDTO> kafkaListenerContainerFactory(
            ObjectMapper objectMapper) {
        ConcurrentKafkaListenerContainerFactory<String, TransacaoPedagioKafkaDTO> factory = 
            new ConcurrentKafkaListenerContainerFactory<>();
        factory.setConsumerFactory(consumerFactory(objectMapper));
        factory.setConcurrency(3); // Número de threads para processar mensagens
        return factory;
    }
}
