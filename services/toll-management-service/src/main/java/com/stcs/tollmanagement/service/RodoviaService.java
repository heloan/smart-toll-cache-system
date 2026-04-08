package com.stcs.tollmanagement.service;

import java.util.List;
import java.util.stream.Collectors;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import com.stcs.tollmanagement.dto.RodoviaRequestDTO;
import com.stcs.tollmanagement.dto.RodoviaResponseDTO;
import com.stcs.tollmanagement.entity.Concessionaria;
import com.stcs.tollmanagement.entity.Rodovia;
import com.stcs.tollmanagement.repository.ConcessionariaRepository;
import com.stcs.tollmanagement.repository.RodoviaRepository;

import lombok.RequiredArgsConstructor;

@Service
@RequiredArgsConstructor
public class RodoviaService {

    private final RodoviaRepository rodoviaRepository;
    private final ConcessionariaRepository concessionariaRepository;

    @Transactional
    public RodoviaResponseDTO criarRodovia(RodoviaRequestDTO request) {
        
        if (rodoviaRepository.existsByCodigo(request.getCodigo())) {
            throw new IllegalArgumentException("Código de rodovia já está cadastrado");
        }

        Concessionaria concessionaria = concessionariaRepository.findById(request.getConcessionariaId())
                .orElseThrow(() -> new IllegalArgumentException("Concessionária não encontrada"));

        Rodovia rodovia = Rodovia.builder()
                .concessionaria(concessionaria)
                .codigo(request.getCodigo())
                .nome(request.getNome())
                .uf(request.getUf())
                .extensaoKm(request.getExtensaoKm())
                .ativa(request.getAtiva() != null ? request.getAtiva() : true)
                .build();

        rodovia = rodoviaRepository.save(rodovia);
        
        return RodoviaResponseDTO.fromEntity(rodovia);
    }

    @Transactional(readOnly = true)
    public RodoviaResponseDTO buscarPorId(Long id) {
        Rodovia rodovia = rodoviaRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("Rodovia não encontrada"));
        return RodoviaResponseDTO.fromEntity(rodovia);
    }

    @Transactional(readOnly = true)
    public List<RodoviaResponseDTO> listarTodas() {
        return rodoviaRepository.findAll().stream()
                .map(RodoviaResponseDTO::fromEntity)
                .collect(Collectors.toList());
    }

    @Transactional(readOnly = true)
    public List<RodoviaResponseDTO> listarPorConcessionaria(Long concessionariaId) {
        return rodoviaRepository.findByConcessionariaId(concessionariaId).stream()
                .map(RodoviaResponseDTO::fromEntity)
                .collect(Collectors.toList());
    }

    @Transactional(readOnly = true)
    public RodoviaResponseDTO buscarPorCodigo(String codigo) {
        Rodovia rodovia = rodoviaRepository.findByCodigo(codigo)
                .orElseThrow(() -> new IllegalArgumentException("Rodovia não encontrada"));
        return RodoviaResponseDTO.fromEntity(rodovia);
    }
}
