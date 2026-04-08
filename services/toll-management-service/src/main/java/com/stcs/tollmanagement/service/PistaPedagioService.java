package com.stcs.tollmanagement.service;

import java.util.List;
import java.util.stream.Collectors;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import com.stcs.tollmanagement.dto.PistaPedagioRequestDTO;
import com.stcs.tollmanagement.dto.PistaPedagioResponseDTO;
import com.stcs.tollmanagement.entity.PistaPedagio;
import com.stcs.tollmanagement.entity.PracaPedagio;
import com.stcs.tollmanagement.repository.PistaPedagioRepository;
import com.stcs.tollmanagement.repository.PracaPedagioRepository;

import lombok.RequiredArgsConstructor;

@Service
@RequiredArgsConstructor
public class PistaPedagioService {

    private final PistaPedagioRepository pistaPedagioRepository;
    private final PracaPedagioRepository pracaPedagioRepository;

    @Transactional
    public PistaPedagioResponseDTO criarPista(PistaPedagioRequestDTO request) {
        
        if (pistaPedagioRepository.existsByPracaIdAndNumeroPista(request.getPracaId(), request.getNumeroPista())) {
            throw new IllegalArgumentException("Já existe uma pista com esse número nesta praça");
        }

        PracaPedagio praca = pracaPedagioRepository.findById(request.getPracaId())
                .orElseThrow(() -> new IllegalArgumentException("Praça de pedágio não encontrada"));

        PistaPedagio pista = PistaPedagio.builder()
                .praca(praca)
                .numeroPista(request.getNumeroPista())
                .tipoPista(request.getTipoPista())
                .sentido(request.getSentido())
                .ativa(request.getAtiva() != null ? request.getAtiva() : true)
                .build();

        pista = pistaPedagioRepository.save(pista);
        
        return PistaPedagioResponseDTO.fromEntity(pista);
    }

    @Transactional(readOnly = true)
    public PistaPedagioResponseDTO buscarPorId(Long id) {
        PistaPedagio pista = pistaPedagioRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("Pista de pedágio não encontrada"));
        return PistaPedagioResponseDTO.fromEntity(pista);
    }

    @Transactional(readOnly = true)
    public List<PistaPedagioResponseDTO> listarTodas() {
        return pistaPedagioRepository.findAll().stream()
                .map(PistaPedagioResponseDTO::fromEntity)
                .collect(Collectors.toList());
    }

    @Transactional(readOnly = true)
    public List<PistaPedagioResponseDTO> listarPorPraca(Long pracaId) {
        return pistaPedagioRepository.findByPracaId(pracaId).stream()
                .map(PistaPedagioResponseDTO::fromEntity)
                .collect(Collectors.toList());
    }
}
