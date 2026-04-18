#!/usr/bin/env python3
"""
Interface Gráfica para o Simulador de Correções de Transações de Pedágio
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import queue
import logging
from correcao_simulator import (
    API_BASE_URL,
    OPERADOR_ID,
    INTERVALO_SEGUNDOS,
    buscar_ocorrencias_pendentes,
    determinar_motivo,
    calcular_valor_corrigido,
    aplicar_correcao,
)
import time


class TextHandler(logging.Handler):
    """Handler customizado para redirecionar logs para o widget de texto"""

    def __init__(self, text_widget, log_queue):
        logging.Handler.__init__(self)
        self.text_widget = text_widget
        self.queue = log_queue

    def emit(self, record):
        msg = self.format(record)
        self.queue.put(msg)


class CorrecaoSimuladorGUI:
    """Interface gráfica do simulador de correções"""

    def __init__(self, root):
        self.root = root
        self.root.title("Simulador de Correções de Pedágio")
        self.root.geometry("900x700")
        self.root.resizable(True, True)

        # Variáveis de controle
        self.thread_simulacao = None
        self.simulacao_ativa = False
        self.stop_event = threading.Event()
        self.log_queue = queue.Queue()

        # Estatísticas
        self.stats = {'total': 0, 'sucesso': 0, 'erro': 0, 'ciclos': 0}

        # Criar interface
        self.criar_widgets()

        # Configurar logging
        self.configurar_logging()

        # Iniciar checagem da fila de logs
        self.processar_log_queue()

        # Configurar fechamento
        self.root.protocol("WM_DELETE_WINDOW", self.ao_fechar)

    def criar_widgets(self):
        """Cria todos os widgets da interface"""

        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configurar grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)

        # Título
        titulo = ttk.Label(
            main_frame,
            text="🔧 Simulador de Correções de Pedágio",
            font=("Arial", 16, "bold"),
        )
        titulo.grid(row=0, column=0, pady=(0, 20), sticky=tk.W)

        # Frame de configurações
        config_frame = ttk.LabelFrame(main_frame, text="Configurações", padding="10")
        config_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        config_frame.columnconfigure(1, weight=1)

        # URL da API
        ttk.Label(config_frame, text="URL da API:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.api_url_var = tk.StringVar(value=API_BASE_URL)
        api_entry = ttk.Entry(config_frame, textvariable=self.api_url_var, width=40)
        api_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)

        # Operador ID
        ttk.Label(config_frame, text="ID do Operador:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.operador_var = tk.IntVar(value=OPERADOR_ID)
        operador_spinbox = ttk.Spinbox(config_frame, from_=1, to=9999, textvariable=self.operador_var, width=10)
        operador_spinbox.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=5)

        # Intervalo entre correções
        ttk.Label(config_frame, text="Intervalo (segundos):").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.intervalo_var = tk.DoubleVar(value=INTERVALO_SEGUNDOS)
        intervalo_spinbox = ttk.Spinbox(
            config_frame, from_=0.1, to=60.0, textvariable=self.intervalo_var, width=10, increment=0.5
        )
        intervalo_spinbox.grid(row=2, column=1, sticky=tk.W, padx=(10, 0), pady=5)

        # Frame de controle de execução
        exec_frame = ttk.LabelFrame(main_frame, text="Controle de Execução", padding="10")
        exec_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        exec_frame.columnconfigure(1, weight=1)

        # Ciclos máximos
        ttk.Label(exec_frame, text="Ciclos máximos:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.ciclos_var = tk.IntVar(value=10)
        ciclos_frame = ttk.Frame(exec_frame)
        ciclos_frame.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        self.ciclos_check_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            ciclos_frame,
            text="Limitar",
            variable=self.ciclos_check_var,
            command=self.toggle_ciclos,
        ).pack(side=tk.LEFT)
        self.ciclos_spinbox = ttk.Spinbox(
            ciclos_frame, from_=1, to=10000, textvariable=self.ciclos_var, width=10, state='disabled'
        )
        self.ciclos_spinbox.pack(side=tk.LEFT, padx=(10, 0))

        # Limite de busca
        ttk.Label(exec_frame, text="Limite por busca:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.limite_var = tk.IntVar(value=50)
        limite_spinbox = ttk.Spinbox(exec_frame, from_=1, to=500, textvariable=self.limite_var, width=10)
        limite_spinbox.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=5)

        # Botões de controle
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=3, column=0, pady=(0, 10))

        self.btn_iniciar = ttk.Button(
            buttons_frame,
            text="▶ Iniciar Correções",
            command=self.iniciar_simulacao,
        )
        self.btn_iniciar.pack(side=tk.LEFT, padx=5)

        self.btn_parar = ttk.Button(
            buttons_frame,
            text="⏹ Parar Correções",
            command=self.parar_simulacao,
            state='disabled',
        )
        self.btn_parar.pack(side=tk.LEFT, padx=5)

        self.btn_limpar = ttk.Button(
            buttons_frame,
            text="🗑 Limpar Log",
            command=self.limpar_log,
        )
        self.btn_limpar.pack(side=tk.LEFT, padx=5)

        # Frame de estatísticas
        stats_frame = ttk.LabelFrame(main_frame, text="Estatísticas", padding="10")
        stats_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        stats_inner = ttk.Frame(stats_frame)
        stats_inner.pack(fill=tk.X)

        self.label_status = ttk.Label(
            stats_inner, text="Status: Pronto", font=("Arial", 10, "bold")
        )
        self.label_status.pack(anchor=tk.W, pady=2)

        self.label_total = ttk.Label(stats_inner, text="Total de correções tentadas: 0")
        self.label_total.pack(anchor=tk.W, pady=2)

        self.label_sucesso = ttk.Label(stats_inner, text="Correções com sucesso: 0")
        self.label_sucesso.pack(anchor=tk.W, pady=2)

        self.label_erro = ttk.Label(stats_inner, text="Correções com erro: 0")
        self.label_erro.pack(anchor=tk.W, pady=2)

        self.label_ciclos = ttk.Label(stats_inner, text="Ciclos executados: 0")
        self.label_ciclos.pack(anchor=tk.W, pady=2)

        self.label_taxa = ttk.Label(stats_inner, text="Taxa de sucesso: 0.00%")
        self.label_taxa.pack(anchor=tk.W, pady=2)

        # Frame de log
        log_frame = ttk.LabelFrame(main_frame, text="Log de Execução", padding="10")
        log_frame.grid(row=5, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 0))
        main_frame.rowconfigure(5, weight=1)

        self.log_text = scrolledtext.ScrolledText(
            log_frame, height=15, wrap=tk.WORD, font=("Courier", 9)
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)

        self.log_text.tag_config("INFO", foreground="blue")
        self.log_text.tag_config("WARNING", foreground="orange")
        self.log_text.tag_config("ERROR", foreground="red")
        self.log_text.tag_config("SUCCESS", foreground="green")

    def toggle_ciclos(self):
        """Habilita/desabilita o spinbox de ciclos"""
        if self.ciclos_check_var.get():
            self.ciclos_spinbox.config(state='normal')
        else:
            self.ciclos_spinbox.config(state='disabled')

    def configurar_logging(self):
        """Configura o sistema de logging"""
        text_handler = TextHandler(self.log_text, self.log_queue)
        text_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
        logging.getLogger().addHandler(text_handler)
        logging.getLogger().setLevel(logging.INFO)

    def processar_log_queue(self):
        """Processa mensagens da fila de log"""
        try:
            while True:
                msg = self.log_queue.get_nowait()
                self.adicionar_log(msg)
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self.processar_log_queue)

    def adicionar_log(self, mensagem):
        """Adiciona mensagem ao log"""
        self.log_text.insert(tk.END, mensagem + "\n")
        self.log_text.see(tk.END)

        num_lines = int(self.log_text.index('end-1c').split('.')[0])
        if num_lines > 1000:
            self.log_text.delete('1.0', '500.0')

    def limpar_log(self):
        """Limpa o log"""
        self.log_text.delete('1.0', tk.END)

    def atualizar_estatisticas(self):
        """Atualiza as estatísticas na interface"""
        total = self.stats['total']
        sucesso = self.stats['sucesso']
        erro = self.stats['erro']
        ciclos = self.stats['ciclos']

        self.label_total.config(text=f"Total de correções tentadas: {total}")
        self.label_sucesso.config(text=f"Correções com sucesso: {sucesso}")
        self.label_erro.config(text=f"Correções com erro: {erro}")
        self.label_ciclos.config(text=f"Ciclos executados: {ciclos}")

        if total > 0:
            taxa = (sucesso / total) * 100
            self.label_taxa.config(text=f"Taxa de sucesso: {taxa:.2f}%")

        if self.simulacao_ativa:
            self.root.after(500, self.atualizar_estatisticas)

    def iniciar_simulacao(self):
        """Inicia a simulação de correções em uma thread separada"""
        if self.simulacao_ativa:
            messagebox.showwarning("Aviso", "Correções já estão em execução!")
            return

        try:
            base_url = self.api_url_var.get().strip()
            operador_id = self.operador_var.get()
            intervalo = self.intervalo_var.get()
            ciclos = self.ciclos_var.get() if self.ciclos_check_var.get() else None
            limite = self.limite_var.get()

            if not base_url:
                messagebox.showerror("Erro", "URL da API não pode ser vazia.")
                return

            if ciclos is None:
                resposta = messagebox.askyesno(
                    "Confirmação",
                    "Nenhum limite de ciclos definido. As correções rodarão indefinidamente.\nDeseja continuar?",
                )
                if not resposta:
                    return

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao validar configurações: {e}")
            return

        # Atualizar interface
        self.simulacao_ativa = True
        self.stop_event.clear()
        self.stats = {'total': 0, 'sucesso': 0, 'erro': 0, 'ciclos': 0}
        self.btn_iniciar.config(state='disabled')
        self.btn_parar.config(state='normal')
        self.label_status.config(text="Status: Executando...", foreground="green")

        self.limpar_log()

        self.thread_simulacao = threading.Thread(
            target=self.executar_correcoes,
            args=(base_url, operador_id, intervalo, ciclos, limite),
            daemon=True,
        )
        self.thread_simulacao.start()

        self.atualizar_estatisticas()
        self.adicionar_log("=== CORREÇÕES INICIADAS ===")

    def executar_correcoes(self, base_url, operador_id, intervalo, ciclos, limite):
        """Executa o loop de correções (roda em thread separada)"""
        logger = logging.getLogger(__name__)
        logger.info('=' * 70)
        logger.info('SIMULADOR DE CORREÇÕES DE PEDÁGIO')
        logger.info(f'API: {base_url}')
        logger.info(f'Operador ID: {operador_id}')
        logger.info(f'Intervalo entre correções: {intervalo}s')
        if ciclos:
            logger.info(f'Ciclos máximos: {ciclos}')
        logger.info('=' * 70)

        try:
            while not self.stop_event.is_set():
                if ciclos and self.stats['ciclos'] >= ciclos:
                    break

                pendentes = buscar_ocorrencias_pendentes(base_url, limite)
                if not pendentes:
                    logger.info('Nenhuma ocorrência pendente encontrada. Aguardando...')
                    # Aguardar com checagem do stop_event
                    if self.stop_event.wait(timeout=intervalo * 5):
                        break
                    self.stats['ciclos'] += 1
                    continue

                logger.info(f'{len(pendentes)} ocorrência(s) pendente(s) encontrada(s)')

                for transacao in pendentes:
                    if self.stop_event.is_set():
                        break

                    tid = transacao.get('id')
                    placa = transacao.get('placa', '?')
                    valor_original = transacao.get('valorOriginal', 0)
                    tipo_veiculo = transacao.get('tipoVeiculo', '?')

                    motivo = determinar_motivo(transacao)
                    valor_corrigido = calcular_valor_corrigido(transacao)

                    logger.info(
                        f'Corrigindo transação #{tid} | placa={placa} | '
                        f'tipo={tipo_veiculo} | valor={valor_original} -> {valor_corrigido}'
                    )

                    resultado = aplicar_correcao(base_url, tid, operador_id, motivo, valor_corrigido)
                    self.stats['total'] += 1

                    if resultado:
                        self.stats['sucesso'] += 1
                        logger.info(f'  -> Correção #{resultado.get("id")} criada com sucesso')
                    else:
                        self.stats['erro'] += 1

                    if self.stop_event.wait(timeout=intervalo):
                        break

                self.stats['ciclos'] += 1

                if self.stats['total'] > 0 and self.stats['total'] % 10 == 0:
                    logger.info(
                        f'[Estatísticas] total={self.stats["total"]} '
                        f'sucesso={self.stats["sucesso"]} erro={self.stats["erro"]}'
                    )

        except Exception as e:
            logger.error(f"Erro durante correções: {e}")
        finally:
            logger.info('=' * 70)
            logger.info('RESULTADO FINAL')
            logger.info(f'Total de correções tentadas: {self.stats["total"]}')
            logger.info(f'Sucesso: {self.stats["sucesso"]}')
            logger.info(f'Erro: {self.stats["erro"]}')
            logger.info(f'Ciclos executados: {self.stats["ciclos"]}')
            logger.info('=' * 70)
            self.root.after(0, self.simulacao_finalizada)

    def simulacao_finalizada(self):
        """Callback quando as correções terminam"""
        self.simulacao_ativa = False
        self.btn_iniciar.config(state='normal')
        self.btn_parar.config(state='disabled')
        self.label_status.config(text="Status: Finalizado", foreground="blue")
        self.adicionar_log("=== CORREÇÕES FINALIZADAS ===")

    def parar_simulacao(self):
        """Para as correções em execução"""
        if not self.simulacao_ativa:
            return

        resposta = messagebox.askyesno(
            "Confirmação", "Deseja realmente parar as correções?"
        )

        if resposta:
            self.stop_event.set()
            self.simulacao_ativa = False
            self.btn_iniciar.config(state='normal')
            self.btn_parar.config(state='disabled')
            self.label_status.config(text="Status: Parado", foreground="red")
            self.adicionar_log("=== CORREÇÕES INTERROMPIDAS PELO USUÁRIO ===")

    def ao_fechar(self):
        """Callback ao fechar a janela"""
        if self.simulacao_ativa:
            resposta = messagebox.askyesno(
                "Confirmação", "Correções em execução. Deseja realmente sair?"
            )
            if not resposta:
                return
            self.stop_event.set()

        self.root.destroy()


def main():
    """Função principal"""
    root = tk.Tk()
    app = CorrecaoSimuladorGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
