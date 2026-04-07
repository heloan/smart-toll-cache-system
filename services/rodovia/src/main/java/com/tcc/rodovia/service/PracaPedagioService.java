package com.tcc.rodovia.service;

import java.util.List;
import java.util.stream.Collectors;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import com.tcc.rodovia.dto.PracaPedagioRequestDTO;
import com.tcc.rodovia.dto.PracaPedagioResponseDTO;
import com.tcc.rodovia.entity.PracaPedagio;
import com.tcc.rodovia.entity.Rodovia;
import com.tcc.rodovia.repository.PracaPedagioRepository;
import com.tcc.rodovia.repository.RodoviaRepository;

import lombok.RequiredArgsConstructor;

@Service
@RequiredArgsConstructor
public class PracaPedagioService {

    private final PracaPedagioRepository pracaPedagioRepository;
    private final RodoviaRepository rodoviaRepository;

    @Transactional
    public PracaPedagioResponseDTO criarPraca(PracaPedagioRequestDTO request) {
        
        Rodovia rodovia = rodoviaRepository.findById(request.getRodoviaId())
                .orElseThrow(() -> new IllegalArgumentException("Rodovia não encontrada"));

        PracaPedagio praca = PracaPedagio.builder()
                .rodovia(rodovia)
                .nome(request.getNome())
                .km(request.getKm())
                .sentido(request.getSentido())
                .ativa(request.getAtiva() != null ? request.getAtiva() : true)
                .build();

        praca = pracaPedagioRepository.save(praca);
        
        return PracaPedagioResponseDTO.fromEntity(praca);
    }

    @Transactional(readOnly = true)
    public PracaPedagioResponseDTO buscarPorId(Long id) {
        PracaPedagio praca = pracaPedagioRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("Praça de pedágio não encontrada"));
        return PracaPedagioResponseDTO.fromEntity(praca);
    }

    @Transactional(readOnly = true)
    public List<PracaPedagioResponseDTO> listarTodas() {
        return pracaPedagioRepository.findAll().stream()
                .map(PracaPedagioResponseDTO::fromEntity)
                .collect(Collectors.toList());
    }

    @Transactional(readOnly = true)
    public List<PracaPedagioResponseDTO> listarPorRodovia(Long rodoviaId) {
        return pracaPedagioRepository.findByRodoviaId(rodoviaId).stream()
                .map(PracaPedagioResponseDTO::fromEntity)
                .collect(Collectors.toList());
    }
}
