package com.stcs.tollmanagement.service;

import java.time.LocalDate;
import java.util.List;
import java.util.stream.Collectors;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import com.stcs.tollmanagement.dto.TarifaPedagioRequestDTO;
import com.stcs.tollmanagement.dto.TarifaPedagioResponseDTO;
import com.stcs.tollmanagement.entity.TarifaPedagio;
import com.stcs.tollmanagement.repository.TarifaPedagioRepository;
import com.stcs.tollmanagement.util.OrigemDadosMarker;

import lombok.RequiredArgsConstructor;

@Service
@RequiredArgsConstructor
public class TarifaPedagioService {

    private final TarifaPedagioRepository tarifaPedagioRepository;
    private final OrigemDadosMarker origemDadosMarker;

    @Transactional
    public TarifaPedagioResponseDTO criarTarifa(TarifaPedagioRequestDTO request) {
        
        // Validar se vigência fim é posterior ao início
        if (request.getVigenciaFim() != null && 
            request.getVigenciaFim().isBefore(request.getVigenciaInicio())) {
            throw new IllegalArgumentException("Data de fim da vigência deve ser posterior à data de início");
        }

        TarifaPedagio tarifa = TarifaPedagio.builder()
                .tipoVeiculo(request.getTipoVeiculo())
                .valor(request.getValor())
                .vigenciaInicio(request.getVigenciaInicio())
                .vigenciaFim(request.getVigenciaFim())
                .build();

        tarifa = tarifaPedagioRepository.save(tarifa);
        
        return TarifaPedagioResponseDTO.fromEntity(tarifa);
    }

    @Transactional
    public TarifaPedagioResponseDTO atualizarTarifa(Long id, TarifaPedagioRequestDTO request) {
        
        TarifaPedagio tarifa = tarifaPedagioRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("Tarifa não encontrada"));

        // Validar se vigência fim é posterior ao início
        if (request.getVigenciaFim() != null && 
            request.getVigenciaFim().isBefore(request.getVigenciaInicio())) {
            throw new IllegalArgumentException("Data de fim da vigência deve ser posterior à data de início");
        }

        tarifa.setTipoVeiculo(request.getTipoVeiculo());
        tarifa.setValor(request.getValor());
        tarifa.setVigenciaInicio(request.getVigenciaInicio());
        tarifa.setVigenciaFim(request.getVigenciaFim());

        tarifa = tarifaPedagioRepository.save(tarifa);
        
        return TarifaPedagioResponseDTO.fromEntity(tarifa);
    }

    @Transactional
    public void excluirTarifa(Long id) {
        if (!tarifaPedagioRepository.existsById(id)) {
            throw new IllegalArgumentException("Tarifa não encontrada");
        }
        tarifaPedagioRepository.deleteById(id);
    }

    @Transactional(readOnly = true)
    public TarifaPedagioResponseDTO buscarPorId(Long id) {
        origemDadosMarker.marcarBancoDados();
        TarifaPedagio tarifa = tarifaPedagioRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("Tarifa não encontrada"));
        return TarifaPedagioResponseDTO.fromEntity(tarifa);
    }

    @Transactional(readOnly = true)
    public List<TarifaPedagioResponseDTO> listarTodas() {
        origemDadosMarker.marcarBancoDados();
        return tarifaPedagioRepository.findAll().stream()
                .map(TarifaPedagioResponseDTO::fromEntity)
                .collect(Collectors.toList());
    }

    @Transactional(readOnly = true)
    public List<TarifaPedagioResponseDTO> listarTarifasVigentes() {
        origemDadosMarker.marcarBancoDados();
        return tarifaPedagioRepository.findTarifasVigentes(LocalDate.now()).stream()
                .map(TarifaPedagioResponseDTO::fromEntity)
                .collect(Collectors.toList());
    }
}
