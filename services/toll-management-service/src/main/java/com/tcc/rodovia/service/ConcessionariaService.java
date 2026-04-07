package com.tcc.rodovia.service;

import java.util.List;
import java.util.stream.Collectors;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import com.tcc.rodovia.dto.ConcessionariaRequestDTO;
import com.tcc.rodovia.dto.ConcessionariaResponseDTO;
import com.tcc.rodovia.entity.Concessionaria;
import com.tcc.rodovia.repository.ConcessionariaRepository;
import com.tcc.rodovia.util.OrigemDadosMarker;

import lombok.RequiredArgsConstructor;

@Service
@RequiredArgsConstructor
public class ConcessionariaService {

    private final ConcessionariaRepository concessionariaRepository;
    private final OrigemDadosMarker origemDadosMarker;

    @Transactional
    public ConcessionariaResponseDTO criarConcessionaria(ConcessionariaRequestDTO request) {
        
        if (concessionariaRepository.existsByCnpj(request.getCnpj())) {
            throw new IllegalArgumentException("CNPJ já está cadastrado");
        }

        Concessionaria concessionaria = Concessionaria.builder()
                .nomeFantasia(request.getNomeFantasia())
                .razaoSocial(request.getRazaoSocial())
                .cnpj(request.getCnpj())
                .contratoConcessao(request.getContratoConcessao())
                .dataInicioContrato(request.getDataInicioContrato())
                .dataFimContrato(request.getDataFimContrato())
                .ativo(request.getAtivo() != null ? request.getAtivo() : true)
                .build();

        concessionaria = concessionariaRepository.save(concessionaria);
        
        return ConcessionariaResponseDTO.fromEntity(concessionaria);
    }

    @Transactional(readOnly = true)
    public ConcessionariaResponseDTO buscarPorId(Long id) {
        origemDadosMarker.marcarBancoDados(); // Marcar que veio do banco
        Concessionaria concessionaria = concessionariaRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("Concessionária não encontrada"));
        return ConcessionariaResponseDTO.fromEntity(concessionaria);
    }

    @Transactional(readOnly = true)
    public List<ConcessionariaResponseDTO> listarTodas() {
        origemDadosMarker.marcarBancoDados(); // Marcar que veio do banco
        return concessionariaRepository.findAll().stream()
                .map(ConcessionariaResponseDTO::fromEntity)
                .collect(Collectors.toList());
    }

    @Transactional(readOnly = true)
    public ConcessionariaResponseDTO buscarPorCnpj(String cnpj) {
        origemDadosMarker.marcarBancoDados(); // Marcar que veio do banco
        Concessionaria concessionaria = concessionariaRepository.findByCnpj(cnpj)
                .orElseThrow(() -> new IllegalArgumentException("Concessionária não encontrada"));
        return ConcessionariaResponseDTO.fromEntity(concessionaria);
    }
}
