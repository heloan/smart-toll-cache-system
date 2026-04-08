package com.stcs.tollmanagement.interceptor;

import java.io.PrintWriter;
import java.io.StringWriter;
import java.lang.management.ManagementFactory;
import java.lang.management.MemoryMXBean;
import java.lang.management.MemoryUsage;
import java.lang.management.ThreadMXBean;

import org.springframework.stereotype.Component;
import org.springframework.web.servlet.HandlerInterceptor;
import org.springframework.web.servlet.ModelAndView;

import com.sun.management.OperatingSystemMXBean;
import com.stcs.tollmanagement.entity.RegistroPerformance;
import com.stcs.tollmanagement.enums.OrigemDadosEnum;
import com.stcs.tollmanagement.service.RegistroPerformanceService;

import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;

@Component
@RequiredArgsConstructor
public class PerformanceInterceptor implements HandlerInterceptor {

    private final RegistroPerformanceService performanceService;
    private static final String START_TIME_ATTRIBUTE = "startTime";
    private static final String MEMORY_START_ATTRIBUTE = "memoryStart";
    public static final String ORIGEM_DADOS_ATTRIBUTE = "origemDados";

    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) {
        request.setAttribute(START_TIME_ATTRIBUTE, System.currentTimeMillis());
        
        MemoryMXBean memoryBean = ManagementFactory.getMemoryMXBean();
        MemoryUsage heapUsage = memoryBean.getHeapMemoryUsage();
        request.setAttribute(MEMORY_START_ATTRIBUTE, heapUsage.getUsed());
        
        return true;
    }

    @Override
    public void postHandle(HttpServletRequest request, HttpServletResponse response, Object handler,
            ModelAndView modelAndView) {
        // Método vazio - lógica implementada em afterCompletion
    }

    @Override
    public void afterCompletion(HttpServletRequest request, HttpServletResponse response, Object handler,
            Exception ex) {
        
        Long startTime = (Long) request.getAttribute(START_TIME_ATTRIBUTE);
        if (startTime == null) {
            return;
        }

        long tempoProcessamento = System.currentTimeMillis() - startTime;

        // Métricas de memória
        MemoryMXBean memoryBean = ManagementFactory.getMemoryMXBean();
        MemoryUsage heapUsage = memoryBean.getHeapMemoryUsage();
        double memoriaUsadaMb = heapUsage.getUsed() / (1024.0 * 1024.0);
        double memoriaLivreMb = (heapUsage.getMax() - heapUsage.getUsed()) / (1024.0 * 1024.0);
        double memoriaTotalMb = heapUsage.getMax() / (1024.0 * 1024.0);

        // Métricas de CPU
        OperatingSystemMXBean osBean = (OperatingSystemMXBean) ManagementFactory.getOperatingSystemMXBean();
        double usoCpu = osBean.getProcessCpuLoad() * 100;

        // Threads ativas
        ThreadMXBean threadBean = ManagementFactory.getThreadMXBean();
        int threadsAtivas = threadBean.getThreadCount();

        // Informações da requisição
        String endpoint = request.getRequestURI();
        String metodoHttp = request.getMethod();
        String ipCliente = obterIpCliente(request);
        String userAgent = request.getHeader("User-Agent");
        String parametros = obterParametros(request);
        int statusHttp = response.getStatus();

        // Mensagem de erro se houver
        String erro = null;
        if (ex != null) {
            StringWriter sw = new StringWriter();
            ex.printStackTrace(new PrintWriter(sw));
            erro = sw.toString();
            if (erro.length() > 5000) {
                erro = erro.substring(0, 5000) + "...";
            }
        }
// Obter origem dos dados se foi definida
        OrigemDadosEnum origemDados = (OrigemDadosEnum) request.getAttribute(ORIGEM_DADOS_ATTRIBUTE);
        if (origemDados == null) {
            // Definir padrão baseado no método HTTP
            if ("GET".equals(metodoHttp)) {
                origemDados = OrigemDadosEnum.BANCO_DADOS; // Assume banco se não especificado
            } else {
                origemDados = OrigemDadosEnum.NAO_APLICAVEL;
            }
        }

        RegistroPerformance registro = RegistroPerformance.builder()
                .endpoint(endpoint)
                .metodoHttp(metodoHttp)
                .tempoProcessamentoMs(tempoProcessamento)
                .memoriaUsadaMb(memoriaUsadaMb)
                .memoriaLivreMb(memoriaLivreMb)
                .memoriaTotalMb(memoriaTotalMb)
                .usoCpuProcesso(usoCpu)
                .threadsAtivas(threadsAtivas)
                .statusHttp(statusHttp)
                .ipCliente(ipCliente)
                .userAgent(userAgent != null && userAgent.length() > 255 ? userAgent.substring(0, 255) : userAgent)
                .parametros(parametros)
                .erro(erro)
                .origemDados(origemDados)
                .build();

        performanceService.registrarAsync(registro);
    }

    private String obterIpCliente(HttpServletRequest request) {
        String ip = request.getHeader("X-Forwarded-For");
        if (ip == null || ip.isEmpty() || "unknown".equalsIgnoreCase(ip)) {
            ip = request.getHeader("Proxy-Client-IP");
        }
        if (ip == null || ip.isEmpty() || "unknown".equalsIgnoreCase(ip)) {
            ip = request.getHeader("WL-Proxy-Client-IP");
        }
        if (ip == null || ip.isEmpty() || "unknown".equalsIgnoreCase(ip)) {
            ip = request.getRemoteAddr();
        }
        if (ip != null && ip.length() > 45) {
            ip = ip.substring(0, 45);
        }
        return ip;
    }

    private String obterParametros(HttpServletRequest request) {
        StringBuilder params = new StringBuilder();
        request.getParameterMap().forEach((key, values) -> {
            params.append(key).append("=");
            if (values != null && values.length > 0) {
                params.append(String.join(",", values));
            }
            params.append("&");
        });
        
        if (params.length() > 0) {
            params.setLength(params.length() - 1); // Remove último &
        }
        
        String parametros = params.toString();
        if (parametros.length() > 5000) {
            parametros = parametros.substring(0, 5000) + "...";
        }
        
        return parametros.isEmpty() ? null : parametros;
    }
}
