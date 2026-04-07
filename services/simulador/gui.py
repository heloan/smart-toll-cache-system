#!/usr/bin/env python3
"""
Interface Gráfica para o Simulador de Transações de Pedágio
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import queue
import logging
from datetime import datetime
from simulator import PedagioSimulator
from config import Config


class TextHandler(logging.Handler):
    """Handler customizado para redirecionar logs para o widget de texto"""
    
    def __init__(self, text_widget, queue):
        logging.Handler.__init__(self)
        self.text_widget = text_widget
        self.queue = queue
    
    def emit(self, record):
        msg = self.format(record)
        self.queue.put(msg)


class SimuladorGUI:
    """Interface gráfica do simulador"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador de Transações de Pedágio")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # Variáveis de controle
        self.simulador = None
        self.thread_simulacao = None
        self.simulacao_ativa = False
        self.log_queue = queue.Queue()
        
        # Configurações
        self.config = Config()
        
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
            text="🚗 Simulador de Transações de Pedágio",
            font=("Arial", 16, "bold")
        )
        titulo.grid(row=0, column=0, pady=(0, 20), sticky=tk.W)
        
        # Frame de configurações
        config_frame = ttk.LabelFrame(main_frame, text="Configurações", padding="10")
        config_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        config_frame.columnconfigure(1, weight=1)
        
        # Kafka Server
        ttk.Label(config_frame, text="Servidor Kafka:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.kafka_server_var = tk.StringVar(value=self.config.KAFKA_BOOTSTRAP_SERVERS)
        kafka_entry = ttk.Entry(config_frame, textvariable=self.kafka_server_var, width=40)
        kafka_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        
        # Tópico Kafka
        ttk.Label(config_frame, text="Tópico Kafka:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.kafka_topic_var = tk.StringVar(value=self.config.KAFKA_TOPIC)
        topic_entry = ttk.Entry(config_frame, textvariable=self.kafka_topic_var, width=40)
        topic_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        
        # Taxa de transações
        ttk.Label(config_frame, text="Transações/segundo:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.rate_var = tk.IntVar(value=self.config.SIMULATION_RATE)
        rate_spinbox = ttk.Spinbox(config_frame, from_=1, to=1000, textvariable=self.rate_var, width=10)
        rate_spinbox.grid(row=2, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Taxa de erro
        ttk.Label(config_frame, text="Taxa de erro (%):").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.error_rate_var = tk.DoubleVar(value=self.config.ERROR_RATE * 100)
        error_rate_spinbox = ttk.Spinbox(
            config_frame,
            from_=0,
            to=100,
            textvariable=self.error_rate_var,
            width=10,
            increment=1
        )
        error_rate_spinbox.grid(row=3, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Frame de controle de execução
        exec_frame = ttk.LabelFrame(main_frame, text="Controle de Execução", padding="10")
        exec_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        exec_frame.columnconfigure(1, weight=1)
        
        # Duração
        ttk.Label(exec_frame, text="Duração (segundos):").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.duracao_var = tk.IntVar(value=0)
        duracao_frame = ttk.Frame(exec_frame)
        duracao_frame.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        self.duracao_check_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            duracao_frame,
            text="Limitar",
            variable=self.duracao_check_var,
            command=self.toggle_duracao
        ).pack(side=tk.LEFT)
        self.duracao_spinbox = ttk.Spinbox(
            duracao_frame,
            from_=1,
            to=3600,
            textvariable=self.duracao_var,
            width=10,
            state='disabled'
        )
        self.duracao_spinbox.pack(side=tk.LEFT, padx=(10, 0))
        
        # Total de transações
        ttk.Label(exec_frame, text="Total de transações:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.count_var = tk.IntVar(value=1000)
        count_frame = ttk.Frame(exec_frame)
        count_frame.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        self.count_check_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            count_frame,
            text="Limitar",
            variable=self.count_check_var,
            command=self.toggle_count
        ).pack(side=tk.LEFT)
        self.count_spinbox = ttk.Spinbox(
            count_frame,
            from_=1,
            to=1000000,
            textvariable=self.count_var,
            width=10,
            state='disabled'
        )
        self.count_spinbox.pack(side=tk.LEFT, padx=(10, 0))
        
        # Botões de controle
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=3, column=0, pady=(0, 10))
        
        self.btn_iniciar = ttk.Button(
            buttons_frame,
            text="▶ Iniciar Simulação",
            command=self.iniciar_simulacao,
            style='Accent.TButton'
        )
        self.btn_iniciar.pack(side=tk.LEFT, padx=5)
        
        self.btn_parar = ttk.Button(
            buttons_frame,
            text="⏹ Parar Simulação",
            command=self.parar_simulacao,
            state='disabled'
        )
        self.btn_parar.pack(side=tk.LEFT, padx=5)
        
        self.btn_limpar = ttk.Button(
            buttons_frame,
            text="🗑 Limpar Log",
            command=self.limpar_log
        )
        self.btn_limpar.pack(side=tk.LEFT, padx=5)
        
        # Modo Stress Test
        self.stress_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            buttons_frame,
            text="Modo Stress Test (1000 TPS)",
            variable=self.stress_var
        ).pack(side=tk.LEFT, padx=20)
        
        # Frame de estatísticas
        stats_frame = ttk.LabelFrame(main_frame, text="Estatísticas", padding="10")
        stats_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        stats_inner = ttk.Frame(stats_frame)
        stats_inner.pack(fill=tk.X)
        
        # Labels de estatísticas
        self.label_status = ttk.Label(
            stats_inner,
            text="Status: Pronto",
            font=("Arial", 10, "bold")
        )
        self.label_status.pack(anchor=tk.W, pady=2)
        
        self.label_total = ttk.Label(stats_inner, text="Total enviadas: 0")
        self.label_total.pack(anchor=tk.W, pady=2)
        
        self.label_ok = ttk.Label(stats_inner, text="Transações OK: 0")
        self.label_ok.pack(anchor=tk.W, pady=2)
        
        self.label_erro = ttk.Label(stats_inner, text="Transações com erro: 0")
        self.label_erro.pack(anchor=tk.W, pady=2)
        
        self.label_taxa = ttk.Label(stats_inner, text="Taxa de erro: 0.00%")
        self.label_taxa.pack(anchor=tk.W, pady=2)
        
        # Frame de log
        log_frame = ttk.LabelFrame(main_frame, text="Log de Execução", padding="10")
        log_frame.grid(row=5, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 0))
        main_frame.rowconfigure(5, weight=1)
        
        # ScrolledText para logs
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=15,
            wrap=tk.WORD,
            font=("Courier", 9)
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Configurar tags de cor para diferentes níveis de log
        self.log_text.tag_config("INFO", foreground="blue")
        self.log_text.tag_config("WARNING", foreground="orange")
        self.log_text.tag_config("ERROR", foreground="red")
        self.log_text.tag_config("SUCCESS", foreground="green")
    
    def toggle_duracao(self):
        """Habilita/desabilita o spinbox de duração"""
        if self.duracao_check_var.get():
            self.duracao_spinbox.config(state='normal')
        else:
            self.duracao_spinbox.config(state='disabled')
    
    def toggle_count(self):
        """Habilita/desabilita o spinbox de contagem"""
        if self.count_check_var.get():
            self.count_spinbox.config(state='normal')
        else:
            self.count_spinbox.config(state='disabled')
    
    def configurar_logging(self):
        """Configura o sistema de logging"""
        # Criar handler customizado
        text_handler = TextHandler(self.log_text, self.log_queue)
        text_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
        
        # Configurar root logger
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
        
        # Limitar tamanho do log
        num_lines = int(self.log_text.index('end-1c').split('.')[0])
        if num_lines > 1000:
            self.log_text.delete('1.0', '500.0')
    
    def limpar_log(self):
        """Limpa o log"""
        self.log_text.delete('1.0', tk.END)
    
    def atualizar_estatisticas(self):
        """Atualiza as estatísticas na interface"""
        if self.simulador and hasattr(self.simulador, 'estatisticas'):
            stats = self.simulador.estatisticas
            total = stats.get('total_enviadas', 0)
            ok = stats.get('total_ok', 0)
            erro = stats.get('total_com_erro', 0)
            
            self.label_total.config(text=f"Total enviadas: {total}")
            self.label_ok.config(text=f"Transações OK: {ok}")
            self.label_erro.config(text=f"Transações com erro: {erro}")
            
            if total > 0:
                taxa = (erro / total) * 100
                self.label_taxa.config(text=f"Taxa de erro: {taxa:.2f}%")
        
        if self.simulacao_ativa:
            self.root.after(500, self.atualizar_estatisticas)
    
    def iniciar_simulacao(self):
        """Inicia a simulação em uma thread separada"""
        if self.simulacao_ativa:
            messagebox.showwarning("Aviso", "Simulação já está em execução!")
            return
        
        # Validar configurações
        try:
            # Atualizar configurações
            self.config.KAFKA_BOOTSTRAP_SERVERS = self.kafka_server_var.get()
            self.config.KAFKA_TOPIC = self.kafka_topic_var.get()
            
            if self.stress_var.get():
                self.config.SIMULATION_RATE = 1000
            else:
                self.config.SIMULATION_RATE = self.rate_var.get()
            
            self.config.ERROR_RATE = self.error_rate_var.get() / 100.0
            
            # Obter parâmetros de execução
            duracao = self.duracao_var.get() if self.duracao_check_var.get() else None
            total = self.count_var.get() if self.count_check_var.get() else None
            
            if duracao is None and total is None:
                resposta = messagebox.askyesno(
                    "Confirmação",
                    "Nenhum limite definido. A simulação rodará indefinidamente.\nDeseja continuar?"
                )
                if not resposta:
                    return
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao validar configurações: {e}")
            return
        
        # Atualizar interface
        self.simulacao_ativa = True
        self.btn_iniciar.config(state='disabled')
        self.btn_parar.config(state='normal')
        self.label_status.config(text="Status: Executando...", foreground="green")
        
        # Limpar estatísticas anteriores
        self.limpar_log()
        
        # Criar simulador
        self.simulador = PedagioSimulator()
        
        # Iniciar thread de simulação
        self.thread_simulacao = threading.Thread(
            target=self.executar_simulacao,
            args=(duracao, total),
            daemon=True
        )
        self.thread_simulacao.start()
        
        # Iniciar atualização de estatísticas
        self.atualizar_estatisticas()
        
        self.adicionar_log("=== SIMULAÇÃO INICIADA ===")
    
    def executar_simulacao(self, duracao, total):
        """Executa a simulação (roda em thread separada)"""
        try:
            self.simulador.executar(
                duracao_segundos=duracao,
                total_transacoes=total
            )
        except Exception as e:
            logging.error(f"Erro durante simulação: {e}")
        finally:
            # Atualizar interface no thread principal
            self.root.after(0, self.simulacao_finalizada)
    
    def simulacao_finalizada(self):
        """Callback quando a simulação termina"""
        self.simulacao_ativa = False
        self.btn_iniciar.config(state='normal')
        self.btn_parar.config(state='disabled')
        self.label_status.config(text="Status: Finalizado", foreground="blue")
        self.adicionar_log("=== SIMULAÇÃO FINALIZADA ===")
    
    def parar_simulacao(self):
        """Para a simulação em execução"""
        if not self.simulacao_ativa:
            return
        
        resposta = messagebox.askyesno(
            "Confirmação",
            "Deseja realmente parar a simulação?"
        )
        
        if resposta:
            self.simulacao_ativa = False
            if self.simulador:
                self.simulador.parar()
            self.btn_iniciar.config(state='normal')
            self.btn_parar.config(state='disabled')
            self.label_status.config(text="Status: Parado", foreground="red")
            self.adicionar_log("=== SIMULAÇÃO INTERROMPIDA PELO USUÁRIO ===")
    
    def ao_fechar(self):
        """Callback ao fechar a janela"""
        if self.simulacao_ativa:
            resposta = messagebox.askyesno(
                "Confirmação",
                "Simulação em execução. Deseja realmente sair?"
            )
            if not resposta:
                return
            
            if self.simulador:
                self.simulador.parar()
        
        self.root.destroy()


def main():
    """Função principal"""
    root = tk.Tk()
    app = SimuladorGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
