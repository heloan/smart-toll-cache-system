package com.stcs.tollmanagement.service;

import java.util.List;
import java.util.stream.Collectors;

import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import com.stcs.tollmanagement.dto.OperadorRequestDTO;
import com.stcs.tollmanagement.dto.OperadorResponseDTO;
import com.stcs.tollmanagement.entity.Operador;
import com.stcs.tollmanagement.repository.OperadorRepository;

import lombok.RequiredArgsConstructor;

@Service
@RequiredArgsConstructor
public class OperadorService {

    private final OperadorRepository operadorRepository;
    private final PasswordEncoder passwordEncoder;

    @Transactional
    public OperadorResponseDTO criarOperador(OperadorRequestDTO request) {
        
        if (operadorRepository.existsByUsername(request.getUsername())) {
            throw new IllegalArgumentException("Username já está em uso");
        }
        
        if (operadorRepository.existsByEmail(request.getEmail())) {
            throw new IllegalArgumentException("Email já está em uso");
        }

        Operador operador = Operador.builder()
                .username(request.getUsername())
                .password(passwordEncoder.encode(request.getPassword()))
                .nomeCompleto(request.getNomeCompleto())
                .email(request.getEmail())
                .telefone(request.getTelefone())
                .ativo(request.getAtivo() != null ? request.getAtivo() : true)
                .build();

        operador = operadorRepository.save(operador);
        
        return OperadorResponseDTO.fromEntity(operador);
    }

    @Transactional(readOnly = true)
    public List<OperadorResponseDTO> listarTodos() {
        return operadorRepository.findAll().stream()
                .map(OperadorResponseDTO::fromEntity)
                .collect(Collectors.toList());
    }

    @Transactional(readOnly = true)
    public OperadorResponseDTO buscarPorId(Long id) {
        Operador operador = operadorRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("Operador não encontrado"));
        return OperadorResponseDTO.fromEntity(operador);
    }

    @Transactional(readOnly = true)
    public OperadorResponseDTO buscarPorUsername(String username) {
        Operador operador = operadorRepository.findByUsername(username)
                .orElseThrow(() -> new IllegalArgumentException("Operador não encontrado"));
        return OperadorResponseDTO.fromEntity(operador);
    }
}
