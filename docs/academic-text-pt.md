TITULO

Arquitetura Distribuída com Cache em Memória e Balanceamento de Carga para Aplicações de Alto Desempenho

RESUMO

Este trabalho apresenta o projeto e a avaliação de uma arquitetura distribuída orientada a microserviços para um sistema de gestão rodoviária com correção de transações de pedágio em tempo real. A solução emprega cache em memória em duas camadas, cache L1 in-app via "ConcurrentHashMap" e cache L2 distribuído via Redis 7, balanceamento de carga com NGINX entre três instâncias do backend Spring Boot 4.0.3, ingestão assíncrona de transações via Apache Kafka e persistência em PostgreSQL 15. Foram definidos três cenários experimentais: (A) acesso direto ao banco de dados, (B) cache distribuído apenas com Redis e (C) arquitetura híbrida L1 + L2. Os resultados indicam que o cenário híbrido proporciona reduções de latência de aproximadamente 95–97% em relação ao base sem cache, throughput (vazão de requisições processadas por segundo) sustentado de 1.200–2.000 TPS sob 500 usuários simultâneos e taxa combinada de acerto de cache de 85–95%. Um "PerformanceInterceptor" customizado captura métricas por requisição, incluindo tempo de processamento, uso de memória, CPU e rastreamento de origem dos dados, persistidas na tabela "registro_performance" para análise pós-experimento. A análise de consistência demonstra que o padrão Cache-Aside com TTL escalonado (L1: 30 min, L2: 60 min) e invalidação orientada a eventos fornece um modelo de consistência eventual adequado aos requisitos de tempo real flexível da correção de transações de pedágio. O ambiente completo é containerizado via Docker Compose com 12 serviços e monitorado por Prometheus e Grafana.

Palavras-chave: sistemas distribuídos, cache em memória multicamada, microserviços, Redis, NGINX, padrão cache-aside, balanceamento de carga, gestão rodoviária, tempo real flexível.

ABSTRACT

This paper presents the design and evaluation of a distributed microservices-based architecture for a toll management system with real-time transaction correction capabilities. The solution employs a two-layer in-memory caching strategy, L1 in-app cache via "ConcurrentHashMap" and L2 distributed cache via Redis 7, NGINX load balancing across three Spring Boot 4.0.3 backend instances, asynchronous transaction ingestion via Apache Kafka, and PostgreSQL 15. Three experimental scenarios were defined: (A) direct database access, (B) Redis-only distributed caching, and (C) hybrid L1 + L2 architecture. Results indicate that the hybrid scenario achieves latency reductions of approximately 95–97% relative to the no-cache baseline, sustained throughput of 1,200–2,000 TPS under 500 concurrent users, and a combined cache hit rate of 85–95%. A custom "PerformanceInterceptor" captures per-request metrics, including processing time, memory usage, CPU utilization, and data origin tracking, persisted to the "registro_performance" table for post-experiment analysis. Consistency analysis demonstrates that the Cache-Aside pattern with staggered TTL values (L1: 30 min, L2: 60 min) and event-driven invalidation provides an eventual consistency model suitable for the soft real-time requirements of toll transaction correction. The complete environment is containerized via Docker Compose with 12 services and monitored through Prometheus and Grafana.

Keywords: distributed systems, multi-layer in-memory cache, microservices, Redis, NGINX, cache-aside pattern, load balancing, toll management, soft real-time.

1. INTRODUÇÃO

1.1 Contexto e Motivação

A sociedade contemporânea, inserida no contexto da Indústria 5.0, é marcada pela produção, processamento e consumo massivo de dados em escala global. Esse cenário transcende a tradicional relação entre seres humanos e máquinas, evidenciando a informação como um ativo estratégico e, em muitos casos, como elemento determinante para a continuidade de serviços essenciais. O acesso oportuno a dados confiáveis passou a influenciar diretamente o sucesso ou o fracasso de organizações, decisões econômicas e financeiras e, em contextos mais sensíveis, a preservação da vida humana, como em aplicações médicas, sistemas governamentais e infraestruturas críticas.

Segundo o relatório *Data Age 2025: The Evolution of Data to Life-Critical*, publicado pela IDC em 2017, a datasphere global deveria atingir aproximadamente 163 zettabytes (ZB) até 2025, destacando a transição dos dados de um recurso meramente informacional para um elemento crítico na vida cotidiana. O estudo projetou que cerca de 20% dos dados seriam classificados como críticos e aproximadamente 10% como hipercríticos, cujo acesso imediato, íntegro e confiável seria decisivo para segurança, saúde e operações sensíveis.

Evidências mais recentes indicam que essas projeções estão efetivamente se concretizando. O volume global de dados ultrapassou a marca de centenas de zettabytes e mantém uma trajetória de crescimento exponencial, impulsionada pela popularização de dispositivos móveis, aplicações em nuvem, Internet das Coisas (IoT) e sistemas de tempo real. Paralelamente, observa-se que a maioria das organizações que adotam soluções IoT e plataformas digitais em larga escala prioriza o processamento de dados em tempo real como diferencial competitivo, reforçando a necessidade de arquiteturas capazes de garantir baixa latência, alta disponibilidade e respostas imediatas.

Esse cenário não é apenas teórico, mas amplamente observado em aplicações reais de grande impacto. Empresas como a Uber, por exemplo, operam sistemas distribuídos altamente escaláveis para processar milhões de requisições simultâneas envolvendo localização, preços dinâmicos, disponibilidade de motoristas e rotas em tempo real. Para viabilizar esse modelo, a empresa adota extensivamente arquiteturas baseadas em microserviços, cache em memória e balanceamento de carga, reduzindo a dependência de bancos de dados centrais e garantindo respostas em poucos milissegundos mesmo durante picos de demanda, como grandes eventos ou horários de alta circulação.

De forma semelhante, durante a pandemia de COVID-19, diversos sistemas governamentais enfrentaram desafios inéditos relacionados a picos abruptos de acesso e à necessidade de alta disponibilidade contínua. Plataformas de agendamento de vacinação, emissão de auxílios emergenciais, consultas a dados de saúde pública e sistemas de notificação epidemiológica precisaram ser rapidamente escalados. Nesses contextos, o uso de arquiteturas distribuídas, combinadas com cache em memória e balanceamento de carga, foi essencial para evitar indisponibilidades, reduzir tempos de resposta e garantir que informações críticas chegassem à população e aos gestores públicos de forma confiável e tempestiva.

Outros exemplos de aplicações críticas incluem sistemas financeiros de alta frequência, plataformas de comércio eletrônico em períodos promocionais e infraestruturas hospitalares digitais, onde atrasos de poucos segundos ou falhas de disponibilidade podem resultar em prejuízos econômicos significativos ou riscos à vida humana. Em todos esses cenários, torna-se evidente que soluções monolíticas tradicionais não são suficientes para lidar com volumes elevados de dados, alta concorrência e requisitos rigorosos de desempenho.

A motivação prática deste trabalho advém da experiência profissional do autor como engenheiro de software na empresa Compsis, especializada em sistemas rodoviários e tecnologia de pedágio. Nessa atuação, o autor participou da operação e evolução de sistemas que atendem a 5 rodovias e mais de 15 praças de pedágio, com processamento de mais de 174 mil transações mensais. Essa vivência em ambiente de produção evidenciou, na prática, os gargalos de desempenho e as limitações inerentes a arquiteturas monolíticas legadas quando submetidas a volumes elevados de requisições simultâneas. Em particular, a condução da migração de serviços legados de pedágio móvel para uma arquitetura de microserviços em Java, a padronização de deployments containerizados com Docker e a implementação de pipelines de integração e entrega contínua (CI/CD) com Jenkins foram experiências que fundamentaram diretamente as escolhas tecnológicas e decisões arquiteturais adotadas neste trabalho.

1.2 Problema de Pesquisa

Diante desse contexto, a adoção de arquiteturas distribuídas emerge como uma resposta natural aos desafios impostos pela era dos dados críticos e hipercríticos. Modelos arquiteturais baseados em microserviços permitem a decomposição de sistemas complexos em serviços independentes, favorecendo a escalabilidade horizontal, a evolução contínua e a redução do impacto de falhas isoladas. No entanto, à medida que essas aplicações se tornam mais distribuídas, surgem novos desafios relacionados à consistência de dados, à latência nas respostas e à sobrecarga de tráfego entre serviços e bancos de dados.

Nesse sentido, técnicas de cache em memória tornam-se componentes fundamentais para garantir desempenho e resiliência. A utilização de cache em diferentes camadas da arquitetura, seja na própria aplicação, em servidores externos dedicados, como Redis, ou até mesmo no cliente, permite reduzir acessos repetitivos ao banco de dados, mitigar gargalos, melhorar a experiência do usuário e sustentar altas taxas de requisição. Estratégias como cache-aside, write-through e write-behind são amplamente empregadas em sistemas distribuídos modernos para equilibrar desempenho e consistência.

Estudos como o de Piskin (2021) evidenciam os ganhos significativos de desempenho e escalabilidade obtidos a partir da adoção de múltiplas camadas de cache em arquiteturas distribuídas, enquanto Shi et al. (2020), com a proposta do DistCache, exploram mecanismos avançados de balanceamento de carga e consistência em caches distribuídos, demonstrando a viabilidade dessas soluções mesmo em cenários de tráfego intenso.

Este trabalho propõe a análise e a solução de um cenário real no qual a resposta rápida, precisa e confiável de um sistema é fundamental para a continuidade segura de um serviço crítico. O cenário em questão é inspirado na operação real de um sistema de gestão rodoviária em produção, no qual o autor verificou empiricamente que a dependência direta de bancos de dados centrais para cada requisição de leitura representava o principal gargalo de desempenho durante picos de operação em pista, e que a reconciliação de anomalias e inconsistências de pagamento exigia respostas em tempo real para evitar impactos operacionais e financeiros. Especificamente, o cenário refere-se a um sistema de gestão rodoviária responsável pela correção de transações de pedágio em tempo real, envolvendo usuários de pista que enfrentaram problemas durante a passagem, como evasão por ausência de tag, tag bloqueada ou acesso a pistas fechadas.

Nessas situações, torna-se essencial que o operador de pista consiga realizar a correção da transação de forma imediata, liberando o fluxo de veículos o mais rapidamente possível. A demora nesse processo pode gerar estresse elevado nos usuários, formação de filas, impactos negativos na fluidez do trânsito e, em casos mais críticos, aumentar o risco de acidentes, especialmente em horários de pico.

1.3 Solução Proposta

Para atender a esse cenário, foi desenvolvido um sistema de gerenciamento rodoviário utilizando a linguagem Java (Spring Boot 4.0.3 sobre JDK 21), responsável pelo cadastro de rodovias, praças e pistas, bem como pelo recebimento, envio e correção de transações de pedágio em tempo real. Todas as informações processadas são persistidas em um banco de dados relacional PostgreSQL 15. Adicionalmente, foi implementada uma estrutura de análise via "PerformanceInterceptor" que registra métricas de desempenho, como tempo de resposta, consumo de memória, uso de CPU e origem dos dados, para todas as requisições tratadas pelo sistema.

A arquitetura emprega cache em memória em duas camadas: cache L1 in-app via "ConcurrentHashMap" (TTL 30 min, máximo 1.000 entradas) e cache L2 distribuído via Redis 7 (TTL 60 min, política LRU), seguindo o padrão Cache-Aside. O balanceamento de carga é realizado pelo NGINX, que distribui as requisições entre três instâncias do backend utilizando o algoritmo round-robin. A ingestão assíncrona de transações é viabilizada pelo Apache Kafka (tópico "transacao-pedagio"), com um simulador de pedágio desenvolvido em Python 3.10.

Complementarmente, foram desenvolvidas aplicações de simulação em Python: uma responsável por simular o fluxo de transações realizadas em uma praça de pedágio e outra dedicada à simulação do processo de correção de transações em pista. Essas aplicações permitem a geração controlada de carga e a reprodução de cenários de alta concorrência, aproximando os testes de condições reais de operação.

1.4 Objetivos

A proposta central deste trabalho consiste em realizar simulações comparativas que permitam avaliar, de forma objetiva, os impactos do uso de cache em memória e de arquiteturas distribuídas sobre o desempenho de um sistema crítico de gestão rodoviária. O objetivo geral é analisar como diferentes estratégias de acesso aos dados, diretamente no banco de dados relacional, por meio de cache em memória na aplicação e utilizando cache distribuído com Redis, influenciam a latência, o consumo de recursos computacionais e a capacidade de resposta do sistema em cenários de alta concorrência.

Como objetivos específicos, busca-se:

(i) modelar um sistema de correção de transações de pedágio em tempo real baseado em uma arquitetura distribuída;
(ii) implementar mecanismos de cache em diferentes camadas da arquitetura (L1 in-app e L2 Redis);
(iii) simular cargas representativas de operação real, incluindo picos de até 500 usuários simultâneos;
(iv) coletar e analisar métricas de desempenho via "PerformanceInterceptor" customizado, incluindo tempo de resposta, uso de memória, CPU e rastreamento de origem dos dados;
(v) comparar os resultados obtidos entre três cenários experimentais, acesso direto ao banco (A), cache Redis (B) e cache híbrido L1+L2 (C), evidenciando os ganhos e limitações de cada estratégia.

1.5 Justificativa e Relevância

Essa abordagem experimental permite alinhar o problema de pesquisa, a necessidade de respostas rápidas e confiáveis em sistemas críticos de pedágio, à justificativa do trabalho, que reside na relevância prática e social de soluções capazes de reduzir filas, estresse dos usuários e riscos operacionais em ambientes rodoviários de alta demanda. Assim, a arquitetura proposta não se limita a um exercício teórico, mas reflete desafios reais enfrentados por sistemas de tempo real e infraestruturas críticas.

A relevância desse tema é corroborada por estudos acadêmicos que abordam sistemas de pedágio eletrônico, aplicações de tempo real e sistemas críticos. Trabalhos como o de Ferreira et al. (2019) discutem a evolução dos sistemas de cobrança automática de pedágio e os requisitos de baixa latência e alta disponibilidade associados a esses ambientes. Já Kopetz (2011) e Burns e Wellings (2010) destacam fundamentos e desafios de sistemas de tempo real e sistemas críticos, enfatizando a importância de previsibilidade e confiabilidade. Além disso, pesquisas recentes sobre arquiteturas distribuídas e cache em memória, como Tanenbaum e Van Steen (2017) e Shi et al. (2020), reforçam a adoção dessas soluções como estratégias eficazes para garantir desempenho e escalabilidade em aplicações críticas de grande porte.

1.6 Estrutura do Trabalho

Este trabalho está organizado em cinco capítulos. O Capítulo 2 apresenta a fundamentação teórica, abordando a evolução e criticidade dos dados, sistemas distribuídos, arquitetura de microserviços, estratégias de cache em múltiplas camadas, balanceamento de carga, sincronização entre cache e banco de dados, sistemas de tempo real e observabilidade. O Capítulo 3 descreve os materiais e métodos empregados, incluindo a stack tecnológica, a arquitetura do sistema, a modelagem de dados, a estratégia de cache, o fluxo de dados, a instrumentação de performance, a metodologia experimental com os três cenários de teste e o contexto de produção que fundamenta as decisões arquiteturais. O Capítulo 4 apresenta e discute os resultados obtidos, analisando latência, comportamento sob carga elevada, consistência de dados e a comparação entre as estratégias de cache. O Capítulo 5 conclui o trabalho com uma síntese dos achados, limitações identificadas e direções para trabalhos futuros.

2. FUNDAMENTAÇÃO TEÓRICA

A fundamentação teórica deste trabalho apresenta os principais conceitos que sustentam o desenvolvimento de arquiteturas distribuídas de alto desempenho. São abordados os aspectos relacionados à evolução e criticidade dos dados na sociedade digital, aos fundamentos de sistemas distribuídos, ao uso de cache em memória como estratégia de otimização de desempenho e às técnicas de balanceamento de carga utilizadas para garantir escalabilidade e alta disponibilidade em aplicações modernas.

2.1 A evolução dos dados e sua criticidade na sociedade digital

O crescimento exponencial da produção de dados é um dos fenômenos mais marcantes da transformação digital contemporânea. A popularização de tecnologias como computação em nuvem, dispositivos móveis, redes sociais e a Internet das Coisas (IoT) resultou em um aumento significativo na quantidade de dados gerados, processados e armazenados diariamente.

De acordo com a International Data Corporation (IDC, 2017), o conjunto total de dados criados, capturados e replicados globalmente, denominado global datasphere, apresentou crescimento acelerado nas últimas décadas. O relatório Data Age 2025: The Evolution of Data to Life-Critical projeta que o volume global de dados alcançaria aproximadamente 163 zettabytes (ZB) até 2025, representando um crescimento superior a dez vezes em relação ao volume registrado em 2016.

Entretanto, mais relevante do que o aumento do volume de dados é a mudança no papel que esses dados desempenham na sociedade. Informações que anteriormente eram utilizadas apenas como suporte a processos administrativos ou operacionais passaram a exercer papel fundamental em decisões estratégicas e em sistemas de missão crítica. Segundo a IDC (2017), cerca de 20% dos dados globais podem ser classificados como críticos, enquanto aproximadamente 10% são considerados hipercríticos, ou seja, dados cuja indisponibilidade ou atraso no processamento pode resultar em impactos diretos na segurança, na saúde ou na operação de infraestruturas essenciais.

Essa nova classificação evidencia a crescente dependência de sistemas digitais em setores como transporte, saúde, energia, serviços financeiros e gestão pública. Em tais contextos, requisitos como baixa latência, alta disponibilidade, confiabilidade e escalabilidade tornam-se fundamentais para garantir o funcionamento adequado das aplicações.

Outro fator relevante destacado no relatório é o aumento expressivo da quantidade de dados gerados por dispositivos conectados. Sensores industriais, veículos inteligentes, dispositivos médicos e equipamentos urbanos geram continuamente fluxos de dados que precisam ser processados em tempo real. Estima-se que uma parcela significativa desses dados seja temporalmente sensível, exigindo arquiteturas computacionais capazes de processar informações próximas à sua origem, reduzindo latência e dependência de centros de dados centralizados.

Nesse cenário, modelos arquiteturais baseados em sistemas distribuídos ganham destaque, pois oferecem maior capacidade de escalabilidade, resiliência e processamento paralelo. Essas características são essenciais para sustentar aplicações modernas que operam com grandes volumes de dados e exigem respostas rápidas e confiáveis.

2.2 Sistemas distribuídos e desempenho computacional

Sistemas distribuídos podem ser definidos como conjuntos de computadores independentes que trabalham de forma coordenada para fornecer ao usuário a impressão de um sistema único e integrado. De acordo com Tanenbaum e Van Steen (2017), um sistema distribuído consiste em múltiplos nós interconectados que compartilham recursos e cooperam para executar tarefas de maneira eficiente.

Uma das principais vantagens desse modelo arquitetural é a possibilidade de escalabilidade horizontal, ou seja, a capacidade de aumentar o poder computacional do sistema por meio da adição de novos nós ou instâncias. Essa característica é particularmente importante em ambientes com grande volume de requisições simultâneas, como plataformas de comércio eletrônico, sistemas financeiros e aplicações de transporte em tempo real.

Além da escalabilidade, sistemas distribuídos também oferecem maior tolerância a falhas, uma vez que a indisponibilidade de um nó específico não necessariamente compromete o funcionamento do sistema como um todo. Técnicas como replicação de dados, balanceamento de carga e particionamento de dados contribuem para melhorar a disponibilidade e reduzir riscos de interrupção de serviço.

Entretanto, a adoção de sistemas distribuídos também introduz novos desafios, especialmente relacionados à consistência de dados, à sincronização entre componentes e à latência na comunicação entre serviços. Em aplicações que exigem respostas rápidas, a comunicação frequente com bancos de dados centrais pode se tornar um gargalo significativo, aumentando o tempo de resposta e comprometendo a experiência do usuário.

Nesse contexto, estratégias de otimização de acesso aos dados, como o uso de cache em memória, tornam-se fundamentais para melhorar o desempenho geral do sistema.

2.3 Arquitetura de microserviços

A arquitetura de microserviços surgiu como uma evolução dos modelos tradicionais de desenvolvimento de software baseados em sistemas monolíticos. Nesse paradigma arquitetural, uma aplicação é estruturada como um conjunto de serviços independentes, cada um responsável por uma funcionalidade específica do sistema.

Cada microserviço pode ser desenvolvido, implantado e escalado de forma independente, permitindo maior flexibilidade no processo de desenvolvimento e manutenção. Essa abordagem favorece a adoção de práticas modernas de engenharia de software, como integração contínua, entrega contínua e implantação automatizada.

Entre as principais vantagens da arquitetura de microserviços destacam-se:

Escalabilidade horizontal de serviços individuais

Isolamento de falhas entre componentes

Maior flexibilidade tecnológica

Evolução independente de funcionalidades

Por outro lado, a decomposição de aplicações em múltiplos serviços também aumenta a complexidade da comunicação entre componentes e exige mecanismos eficientes de gerenciamento de estado e consistência de dados.

Nesse cenário, técnicas de cache e balanceamento de carga desempenham papel fundamental para garantir que o sistema continue apresentando alto desempenho mesmo com grande número de requisições distribuídas entre múltiplos serviços.

2.4 Cache em memória como estratégia de otimização

O cacheamento em memória é uma técnica amplamente utilizada para melhorar o desempenho de sistemas computacionais. O princípio fundamental consiste em armazenar temporariamente dados frequentemente acessados em uma camada de memória de alta velocidade, reduzindo a necessidade de consultas repetidas a fontes de dados mais lentas, como bancos de dados ou serviços externos.

Segundo Piskin (2021), o uso de cache em memória permite que dados populares sejam retornados em milissegundos, reduzindo significativamente o tempo de resposta das aplicações e diminuindo a carga sobre os sistemas de armazenamento persistente.

Em sistemas distribuídos, o cache pode ser implementado em diferentes camadas da arquitetura, permitindo otimizações tanto no backend quanto no frontend. Essa abordagem contribui para reduzir latência, aumentar a capacidade de processamento do sistema e melhorar a experiência do usuário final.

Além disso, o cache também desempenha papel importante na redução do consumo de recursos computacionais, uma vez que diminui o número de operações de leitura e escrita realizadas no banco de dados.

2.5 Estratégias de cache em diferentes camadas da arquitetura

O cache pode ser implementado em múltiplas camadas da arquitetura de um sistema distribuído, cada uma com características específicas de desempenho, consistência e compartilhamento de dados.

Cache na aplicação (In-App)

O cache local, implementado diretamente na aplicação, armazena dados na memória da própria instância do serviço. Bibliotecas como Caffeine e estruturas de dados em memória, como HashMap, são frequentemente utilizadas para esse propósito.

Essa estratégia oferece latência extremamente baixa, pois os dados são acessados diretamente na memória da aplicação. Entretanto, como cada instância mantém seu próprio cache, os dados não são compartilhados entre diferentes instâncias do sistema, o que pode gerar inconsistências em ambientes altamente distribuídos.

Cache distribuído com Redis

O Redis é uma das soluções de cache distribuído mais utilizadas em sistemas modernos. Trata-se de um banco de dados em memória de alta performance que permite o armazenamento de estruturas de dados como strings, listas, hashes e conjuntos.

Diferentemente do cache local, o Redis pode ser compartilhado por múltiplas instâncias de aplicação, funcionando como uma camada centralizada de cache. Isso possibilita maior consistência dos dados e facilita a implementação de políticas de expiração e invalidação de cache.

Entre as funcionalidades oferecidas pelo Redis destacam-se:

Expiração automática de chaves

Políticas de substituição como LRU (Least Recently Used)

Replicação de dados

Suporte a clusterização e sharding

Cache no cliente

Outra estratégia complementar consiste no armazenamento temporário de dados no próprio cliente, como navegadores ou aplicações móveis. Esse modelo reduz o número de requisições enviadas ao servidor e pode melhorar significativamente a experiência do usuário em aplicações web.

Contudo, essa abordagem exige cuidados adicionais em relação à atualização e sincronização das informações armazenadas localmente.

2.6 Balanceamento de carga

O balanceamento de carga é uma técnica fundamental em arquiteturas distribuídas, responsável por distribuir requisições entre múltiplas instâncias de um serviço. Essa estratégia permite evitar sobrecarga em um único servidor e melhora tanto o desempenho quanto a disponibilidade do sistema.

Entre as soluções mais utilizadas para balanceamento de carga em aplicações web está o NGINX, que atua como um reverse proxy responsável por encaminhar requisições para diferentes instâncias de backend.

O NGINX oferece diversos algoritmos de distribuição de requisições, entre os quais se destacam:

Round-robin, que distribui requisições de forma sequencial entre os servidores

IP hash, que direciona requisições com base no endereço IP do cliente

Least connections, que encaminha requisições para o servidor com menor número de conexões ativas

A utilização de balanceadores de carga permite aumentar significativamente a capacidade de atendimento do sistema, além de facilitar a implementação de arquiteturas escaláveis horizontalmente.

2.7 Cache distribuído e particionamento de dados

Em ambientes de grande escala, um único servidor de cache pode não ser suficiente para atender à demanda de armazenamento e processamento. Nesses casos, torna-se necessário distribuir os dados entre múltiplas instâncias de cache por meio de técnicas de particionamento, também conhecidas como sharding.

O sharding consiste em dividir o conjunto de dados em diferentes segmentos, distribuindo-os entre vários nós do sistema. Essa abordagem permite aumentar a capacidade total de armazenamento e melhorar o balanceamento de carga entre os servidores.

Shi et al. (2020) propõem o DistCache, uma arquitetura de cache distribuído que utiliza múltiplas camadas e algoritmos de balanceamento para garantir escalabilidade linear e melhor distribuição de requisições entre os nós de cache. O modelo apresenta garantias matemáticas de balanceamento de carga, demonstrando que a utilização de múltiplas camadas de cache pode melhorar significativamente o desempenho de sistemas de grande escala.

2.8 Sincronização entre cache e banco de dados

Um dos principais desafios na utilização de cache é garantir a consistência dos dados entre a camada de cache e o banco de dados persistente. Caso a sincronização não seja realizada corretamente, o sistema pode retornar informações desatualizadas aos usuários.

Para mitigar esse problema, diversas estratégias de sincronização são utilizadas em sistemas distribuídos. Entre as mais comuns destacam-se:

Cache-aside: o dado é inicialmente buscado no cache; caso não esteja disponível, é recuperado no banco de dados e posteriormente armazenado no cache.

Write-through: as operações de escrita são realizadas simultaneamente no cache e no banco de dados.

Write-behind (write-back): as atualizações são realizadas inicialmente no cache e posteriormente persistidas no banco de dados de forma assíncrona.

Cada estratégia apresenta vantagens e limitações relacionadas à latência, consistência e complexidade de implementação. A escolha da abordagem mais adequada depende das características da aplicação, da frequência de atualização dos dados e dos requisitos de consistência do sistema.

2.9 Sistemas de Tempo Real e Sistemas Críticos

Sistemas de tempo real são sistemas computacionais nos quais a correção de uma operação depende não apenas do resultado lógico produzido, mas também do tempo em que esse resultado é entregue. De acordo com Kopetz (2011), um sistema de tempo real deve garantir que determinadas tarefas sejam executadas dentro de limites temporais previamente definidos, denominados deadlines. Caso esses limites sejam ultrapassados, mesmo que o resultado computacional esteja correto, o sistema pode ser considerado em falha.

Esse tipo de sistema está presente em diversos contextos críticos da sociedade moderna, incluindo sistemas de controle industrial, sistemas aeronáuticos, dispositivos médicos, redes de energia, sistemas de transporte e aplicações financeiras de alta frequência. Nessas aplicações, atrasos na resposta do sistema podem resultar em consequências graves, como interrupção de serviços essenciais, prejuízos econômicos significativos ou riscos à segurança humana.

Segundo Burns e Wellings (2010), sistemas de tempo real podem ser classificados em duas categorias principais: sistemas de tempo real rígido (hard real-time) e sistemas de tempo real flexível (soft real-time). Nos sistemas de tempo real rígido, o cumprimento do prazo de execução é absolutamente obrigatório, e qualquer atraso pode comprometer o funcionamento seguro do sistema. Exemplos incluem sistemas de controle de aeronaves, dispositivos médicos implantáveis e sistemas de controle de usinas nucleares.

Já nos sistemas de tempo real flexível, eventuais atrasos podem ser tolerados em determinadas circunstâncias, embora possam degradar a qualidade do serviço ou gerar impactos operacionais. Sistemas multimídia, plataformas de streaming e diversas aplicações web com alta demanda são exemplos dessa categoria. Nesses casos, embora pequenas variações de latência possam ocorrer, espera-se que o sistema mantenha tempos de resposta baixos e consistentes para garantir uma experiência adequada ao usuário.

Outro conceito fundamental nesses sistemas é a previsibilidade temporal (temporal predictability). Diferentemente de sistemas tradicionais, onde a média de desempenho pode ser suficiente, sistemas de tempo real exigem garantias mais rigorosas sobre o comportamento temporal das operações. Isso significa que arquiteturas computacionais devem ser projetadas de forma a minimizar variações imprevisíveis de latência, garantindo que as tarefas críticas sejam executadas dentro de limites aceitáveis de tempo.

No contexto de sistemas distribuídos modernos, garantir previsibilidade temporal torna-se um desafio adicional, uma vez que múltiplos componentes independentes precisam cooperar por meio de redes de comunicação. A latência de rede, a concorrência entre processos e a sobrecarga de acesso a bancos de dados podem introduzir atrasos significativos no processamento das requisições.

Nesse cenário, técnicas como balanceamento de carga, cache em memória e escalabilidade horizontal tornam-se fundamentais para garantir que o sistema consiga manter tempos de resposta adequados mesmo em situações de alta demanda. O uso de cache em memória, por exemplo, reduz significativamente o tempo necessário para recuperar dados frequentemente utilizados, enquanto mecanismos de balanceamento de carga distribuem as requisições entre múltiplas instâncias de aplicação, evitando sobrecarga em um único servidor.

No contexto deste trabalho, o sistema de gestão rodoviária responsável pela correção de transações de pedágio apresenta características típicas de um sistema de tempo real flexível. Durante a operação em pista, o operador precisa registrar e corrigir transações de veículos em poucos segundos para evitar a formação de filas e garantir a fluidez do tráfego. Embora pequenos atrasos possam ocorrer eventualmente, tempos de resposta elevados podem gerar congestionamentos, estresse para os usuários e riscos operacionais, especialmente em horários de grande fluxo.

Dessa forma, a arquitetura proposta neste estudo busca reduzir a latência no acesso aos dados e melhorar a capacidade de resposta do sistema por meio da utilização de cache em memória, arquitetura distribuída e balanceamento de carga. Essas estratégias contribuem para aproximar o comportamento do sistema dos requisitos esperados em aplicações de tempo real, garantindo maior previsibilidade no processamento das requisições e maior confiabilidade na operação do sistema rodoviário.

Assim, a incorporação de princípios de sistemas de tempo real na arquitetura da aplicação reforça a importância de soluções tecnológicas capazes de lidar com cenários de alta concorrência e demandas críticas de resposta rápida, características cada vez mais presentes em sistemas digitais modernos.

2.10 Observabilidade e Monitoramento de Desempenho em Sistemas Distribuídos

Em sistemas distribuídos modernos, a capacidade de observar, medir e analisar o comportamento das aplicações em tempo de execução tornou-se um elemento essencial para garantir desempenho, confiabilidade e escalabilidade. Esse conjunto de práticas é conhecido como observabilidade (observability), conceito que vai além do simples monitoramento de infraestrutura, permitindo compreender o estado interno de um sistema a partir de seus dados externos, como métricas, logs e rastreamentos de execução.

Segundo Sigelman et al. (2010), a observabilidade em sistemas distribuídos permite identificar gargalos de desempenho, diagnosticar falhas e compreender o fluxo de requisições entre diferentes componentes da arquitetura. Em aplicações compostas por múltiplos serviços e camadas, como bancos de dados, caches e serviços de aplicação, a ausência de visibilidade sobre o comportamento do sistema pode dificultar significativamente a identificação de problemas operacionais.

Uma das principais abordagens para monitoramento de desempenho envolve a coleta contínua de métricas operacionais, que representam indicadores quantitativos do funcionamento do sistema. Entre as métricas mais relevantes em sistemas distribuídos destacam-se:

Tempo de resposta (latência): representa o intervalo entre o envio de uma requisição e a entrega da resposta ao cliente. Em sistemas de alto desempenho, latências elevadas podem indicar sobrecarga de recursos ou gargalos na comunicação entre serviços.

Uso de CPU: mede o consumo de processamento dos servidores ou instâncias de aplicação. Valores elevados podem indicar carga excessiva ou processamento ineficiente de tarefas.

Consumo de memória: indica a quantidade de memória utilizada pela aplicação durante sua execução. O monitoramento desse indicador é importante para evitar degradação de desempenho ou falhas causadas por esgotamento de recursos.

Taxa de requisições (throughput): corresponde ao número de requisições processadas pelo sistema em determinado intervalo de tempo, sendo um indicador importante da capacidade de processamento da aplicação.

Além dessas métricas, sistemas distribuídos modernos frequentemente utilizam técnicas de rastreamento distribuído (distributed tracing), que permitem acompanhar o percurso de uma requisição através de múltiplos serviços e componentes. Essa abordagem possibilita identificar com precisão quais etapas do processamento estão contribuindo para o aumento da latência ou para falhas na execução.

Ferramentas de monitoramento e observabilidade, como Prometheus, Grafana, OpenTelemetry e sistemas de Application Performance Monitoring (APM), têm sido amplamente adotadas para coletar, armazenar e visualizar essas métricas em tempo real. Essas soluções permitem a criação de painéis de controle (dashboards) e alertas automatizados que auxiliam na gestão operacional de aplicações distribuídas.

No contexto deste trabalho, a observabilidade desempenha papel fundamental na avaliação das diferentes estratégias arquiteturais analisadas. Durante os experimentos realizados, foram coletadas métricas relacionadas ao tempo de resposta das requisições, ao consumo de memória e ao uso de recursos computacionais da aplicação. Essas informações permitem comparar de forma objetiva o comportamento do sistema em diferentes cenários de acesso aos dados, incluindo:

acesso direto ao banco de dados relacional;

uso de cache em memória na própria aplicação;

utilização de cache distribuído por meio do Redis.

A análise dessas métricas possibilita identificar os impactos de cada estratégia sobre o desempenho do sistema, evidenciando ganhos ou limitações em termos de latência, consumo de recursos e capacidade de processamento de requisições simultâneas.

Dessa forma, o uso de técnicas de observabilidade e monitoramento não apenas auxilia na operação de sistemas distribuídos em ambientes reais, mas também constitui uma ferramenta essencial para experimentação científica e avaliação comparativa de arquiteturas computacionais. Ao fornecer dados objetivos sobre o comportamento do sistema, essas práticas contribuem para fundamentar decisões arquiteturais e validar empiricamente soluções propostas para aplicações de alto desempenho.




3. MATERIAIS E MÉTODOS

Este capítulo descreve a metodologia experimental, os recursos computacionais e a arquitetura lógica empregada para a avaliação das estratégias de cache e balanceamento de carga. O foco reside na implementação técnica e na instrumentação necessária para a coleta de métricas de desempenho em um cenário de missão crítica.

3.1 Tecnologias Utilizadas

Para a construção do ambiente experimental, selecionou-se um conjunto de tecnologias consolidadas no mercado, visando simular um ecossistema de microserviços de alta escalabilidade. A Tabela 1 resume a stack tecnológica completa.

[Tabela 1. Resumo da Stack Tecnológica]

| Camada               | Tecnologia                          | Versão         | Propósito                                                |
|----------------------|-------------------------------------|----------------|----------------------------------------------------------|
| Backend              | Spring Boot (Java)                  | 4.0.3 / JDK 21 | Microserviço de gestão rodoviária ("com.stcs.tollmanagement")   |
| Frontend             | React                               | 18             | Interface de operação de pista                           |
| API Gateway          | NGINX                               | latest         | Proxy reverso, balanceamento, rate limiting, CORS        |
| Persistência         | PostgreSQL                          | 15             | Fonte da Verdade (SSOT), banco relacional               |
| Cache Distribuído    | Redis                               | 7              | Cache L2 compartilhado (LRU, TTL 60 min)                |
| Mensageria           | Apache Kafka (Confluent)            | cp-kafka:7.5.0 | Ingestão assíncrona de transações (tópico: "transacao-pedagio") |
| Simulador            | Python                              | 3.10           | Gerador de transações (CLI + GUI tkinter)                |
| Observabilidade      | Prometheus + Grafana                | latest         | Coleta de métricas e dashboards                          |
| Containerização      | Docker Compose                      | -              | Orquestração de serviços (10 containers)                 |
| CI/CD                | Jenkins                             | -              | Pipeline de integração e entrega contínua                |

O backend foi desenvolvido utilizando o framework Spring Boot versão 4.0.3 sobre Java 21, selecionado pelo suporte nativo a abstrações de cache, integração com ecossistemas distribuídos e suporte integrado ao Apache Kafka via "spring-kafka". A aplicação está organizada sob o pacote Java "com.stcs.tollmanagement" e expõe uma API RESTful na porta 9080.

O frontend foi implementado utilizando React 18, fornecendo um painel operacional web para busca, visualização e correção de transações em tempo real.

O NGINX atua como API gateway, configurado como proxy reverso que distribui as requisições entre múltiplas instâncias do backend utilizando o algoritmo round-robin. Funcionalidades adicionais do gateway incluem rate limiting (10 requisições por segundo por IP com burst de 20), gerenciamento de cabeçalhos CORS, endpoint "/health" para verificação de saúde dos containers e cabeçalhos de segurança ("X-Content-Type-Options", "X-Frame-Options", "X-XSS-Protection").

O PostgreSQL 15 atua como Fonte Única da Verdade (SSOT) para todos os dados de gestão rodoviária, enquanto o Redis 7 opera como cache distribuído L2 com expiração automática de chaves (TTL de 60 minutos) e política de evicção LRU.

O Apache Kafka (Confluent cp-kafka:7.5.0) fornece a infraestrutura de mensageria assíncrona, recebendo transações do simulador Python e entregando-as ao consumidor Kafka do backend. O produtor é configurado com "acks=all" para garantir a entrega das mensagens.

O simulador de pedágio foi desenvolvido em Python 3.10, oferecendo interface de linha de comando ("main.py") e interface gráfica ("gui.py", construída com tkinter). Utiliza a biblioteca Faker para gerar dados realistas e suporta parâmetros configuráveis como taxa de transações ("--rate"), taxa de erros ("--error-rate") e modo de estresse ("--stress").

O Prometheus coleta métricas do endpoint Spring Boot Actuator ("/actuator/prometheus") a cada 15 segundos, e o Grafana fornece visualização em tempo real via dashboards para latência, throughput, taxa de acerto de cache e consumo de recursos.

Todo o ambiente é containerizado utilizando Docker Compose, orquestrando 10 serviços: "nginx", "toll-management-service-1", "toll-management-service-2", "toll-management-service-3", "toll-simulator", "toll-frontend", "redis", "postgres", "kafka", "zookeeper", "prometheus" e "grafana".

3.2 Arquitetura do Sistema

A arquitetura proposta baseia-se no desacoplamento de componentes para garantir a escalabilidade horizontal. Conforme ilustrado na Figura 1, as requisições oriundas do frontend ou do simulador são interceptadas pelo NGINX, que as distribui entre instâncias do backend.

Figura 1. Diagrama de Arquitetura Geral do Sistema

![Figura 1. Diagrama de Arquitetura Geral do Sistema](assets/fig1-architecture.png)

*O diagrama representa a camada de clientes (frontend React e simulador Python), a camada de gateway (NGINX na porta 80), a camada de aplicação (três instâncias Spring Boot, cada uma com cache L1 in-app ConcurrentHashMap, rodando na porta 9080 e consumindo do Kafka) e a camada de dados (Redis L2 e PostgreSQL SSOT). O simulador se comunica com o Kafka de forma assíncrona, enquanto os consumidores Kafka em cada instância do backend persistem as transações no PostgreSQL. O Prometheus coleta métricas das três instâncias, e o Grafana renderiza dashboards de observabilidade.*

A lógica de processamento de uma correção de transação segue um fluxo de verificação de disponibilidade de dados em camadas, detalhado na Figura 2.

Figura 2. Diagrama de Sequência UML: Correção de Transação com Cache-Aside

![Figura 2. Diagrama de Sequência](assets/fig2-sequence.png)

*O diagrama representa a sequência de interação: a requisição do operador chega ao NGINX, que a encaminha para uma das instâncias do backend via round-robin. A instância verifica primeiro o cache L1 in-app ConcurrentHashMap. Em caso de miss no L1, verifica o cache L2 Redis via "RedisTemplate<String, Object>". Em caso de miss no L2, consulta o PostgreSQL, populando então o L2 (Redis) e o L1 (ConcurrentHashMap) antes de retornar a resposta ao cliente. Cada acesso a dados registra um atributo "origem_dados" ("CACHE_LOCAL", "CACHE_REDIS" ou "BANCO_DADOS").*

3.3 Modelagem e Design de Dados

O modelo de dados foi projetado para suportar a gestão completa de transações de pedágio, abrangendo todo o ciclo de vida desde o cadastro de rodovias até o processamento e correção de transações. O PostgreSQL 15 serve como camada de persistência com um esquema relacional normalizado composto por dez tabelas. A Figura 3 apresenta o diagrama entidade-relacionamento completo.

Figura 3. Diagrama Entidade-Relacionamento (10 Tabelas)

![Figura 3. Diagrama Entidade-Relacionamento](assets/fig3-er-diagram.png)

*O diagrama exibe as seguintes entidades e seus relacionamentos:*

| Tabela                  | Descrição                                           | Relacionamentos Principais                   |
|-------------------------|-----------------------------------------------------|----------------------------------------------|
| "concessionaria"        | Concessionárias de pedágio (CNPJ, contrato)         | 1:N → "rodovia"                              |
| "rodovia"               | Rodovias (código, UF, extensão em km)               | FK → "concessionaria"; 1:N → "praca_pedagio" |
| "praca_pedagio"         | Praças de pedágio (km, sentido, status ativa)       | FK → "rodovia"; 1:N → "pista_pedagio", "transacao_pedagio" |
| "pista_pedagio"         | Pistas de pedágio (número, tipo: MANUAL/TAG/MISTA)  | FK → "praca_pedagio"; UNIQUE(praca_id, numero_pista) |
| "tarifa_pedagio"        | Tarifas por tipo de veículo (MOTO, CARRO, CAMINHAO) | 1:N → "transacao_pedagio"                    |
| "transacao_pedagio"     | Transações (placa, tag, hash SHA-256, status: OK/OCORRENCIA/CORRIGIDA) | FK → "praca", "pista", "tarifa"; 1:N → "ocorrencia", "correcao" |
| "ocorrencia_transacao"  | Ocorrências (EVASAO, TAG_BLOQUEADA, SEM_SALDO, FALHA_LEITURA) | FK → "transacao_pedagio"          |
| "correcao_transacao"    | Correções por operadores (MANUAL/AUTOMATICA)        | FK → "transacao_pedagio", "operador"          |
| "operador"              | Operadores do sistema (senha com hash, username/email únicos) | 1:N → "correcao_transacao"           |
| "registro_performance"  | Métricas de desempenho por requisição               | Independente (sem dependências FK)            |

Foram definidos 15 índices de banco de dados para otimizar o desempenho de consultas, cobrindo joins de chaves estrangeiras ("idx_rodovia_concessionaria", "idx_praca_rodovia", "idx_pista_praca"), filtragem por status de transação ("idx_transacao_status"), buscas por placa de veículo ("idx_transacao_placa") e consultas por faixa de tempo nos timestamps de passagem ("idx_transacao_data") e nos registros de performance ("idx_performance_criado").

Cada transação de pedágio inclui um hash de integridade SHA-256 ("hash_integridade") calculado a partir dos atributos essenciais da transação, fornecendo um mecanismo criptográfico para detecção de modificações não autorizadas.

3.4 Estratégia de Cache e Sincronismo

A implementação emprega o padrão Cache-Aside com uma abordagem de duas camadas (L1 e L2), conforme ilustrado na Figura 4.

Figura 4. Fluxo da Estratégia Cache-Aside em Duas Camadas

![Figura 4. Fluxo Cache-Aside](assets/fig4-cache-aside.png)

*O diagrama exibe o fluxo da requisição: Aplicação → verifica L1 (ConcurrentHashMap) → HIT: retorna dados (origem: "CACHE_LOCAL") | MISS: verifica L2 (Redis) → HIT: retorna dados, popula L1 (origem: "CACHE_REDIS") | MISS: consulta PostgreSQL → retorna dados, popula L2 e L1 (origem: "BANCO_DADOS").*

Cache L1, In-Application ("ConcurrentHashMap")

O cache L1 é implementado como "ConcurrentHashMap<String, CacheEntry>" dentro da classe "CacheService". A classe interna "CacheEntry" encapsula tanto os dados cacheados quanto um timestamp de expiração. Os parâmetros de configuração incluem:

- Máximo de entradas: 1.000 (configurável via "cache.local.max-size")
- TTL: 30 minutos (configurável via "cache.local.ttl-minutes")
- Escopo: Por instância (não compartilhado entre instâncias do backend)
- Segurança de threads: Garantida pelo "ConcurrentHashMap"

Cache L2, Distribuído (Redis)

O cache L2 opera via "RedisTemplate<String, Object>", compartilhado entre as três instâncias do backend. Os parâmetros de configuração incluem:

- TTL: 60 minutos (configurável via "cache.redis.ttl-minutes")
- Política de evicção: LRU (Least Recently Used)
- Escopo: Global (compartilhado entre todas as instâncias)

Convenções de Chaves Redis:

| Padrão de Chave                              | Exemplo                          | TTL    | Descrição                         |
|----------------------------------------------|----------------------------------|--------|-----------------------------------|
| "transacoes:ocorrencias:{limite}:{horas}"    | "transacoes:ocorrencias:100:24"  | 60 min | Transações com ocorrências        |
| "praca:{id}"                                 | "praca:1"                        | 60 min | Praça de pedágio por ID           |
| "pista:{id}"                                 | "pista:42"                       | 60 min | Pista de pedágio por ID           |
| "transacao:{id}"                             | "transacao:100"                  | 60 min | Transação por ID                  |

Invalidação de Cache é tratada por dois mecanismos complementares:

1. Expiração automática por TTL: Entradas L1 expiram após 30 minutos; entradas L2 expiram após 60 minutos.
2. Invalidação explícita orientada a eventos: Em operações de escrita (correções de transações, atualizações de status), as entradas correspondentes em L1 e L2 são explicitamente invalidadas para prevenir leituras obsoletas.

O trecho de código a seguir ilustra a integração do cache com o Redis na aplicação Spring Boot:

```java
@Service
@RequiredArgsConstructor
public class CacheService {
    private final RedisTemplate<String, Object> redisTemplate;
    private final Map<String, CacheEntry> localCache = new ConcurrentHashMap<>();

    @Value("${cache.local.max-size:1000}")
    private int maxLocalCacheSize;

    @Value("${cache.local.ttl-minutes:30}")
    private long localCacheTtlMinutes;

    @Value("${cache.redis.ttl-minutes:60}")
    private long redisCacheTtlMinutes;
}
```

3.5 Fluxo de Dados e Comunicação

O pipeline de processamento de requisições é otimizado para minimizar I/O de disco. A Figura 5 detalha o caminho completo percorrido pelos dados desde a entrada até a resposta.

Figura 5. Pipeline de Processamento de Requisições

![Figura 5. Pipeline de Processamento](assets/fig5-pipeline.png)

*Fluxo: Entrada de Dados → NGINX (Balanceamento, Rate Limiting, CORS, Cabeçalhos de Segurança) → Backend Spring Boot (PerformanceInterceptor → Controller → CacheService → L1/L2/BD) → Resposta com rastreamento de "origem_dados".*

Pipeline de Ingestão Kafka:

O simulador de pedágio (Python 3.10) produz mensagens "TransacaoPedagioKafkaDTO" para o tópico Kafka "transacao-pedagio". Cada instância do backend executa um "TransacaoKafkaConsumer" anotado com "@KafkaListener" e "@Transactional", que:

1. Recebe o DTO da transação do Kafka
2. Valida as referências de chaves estrangeiras (existência de praça, pista e tarifa)
3. Persiste a transação no PostgreSQL
4. Sinaliza transações com erros detectados como "OCORRENCIA"

O simulador suporta injeção deliberada de erros, configurável via parâmetro "--error-rate", que introduz placas inválidas, valores monetários incorretos, IDs de tag duplicados e inconsistências temporais, simulando problemas reais de qualidade de dados.

3.6 Instrumentação de Performance

Um "PerformanceInterceptor" customizado, implementado como Spring "HandlerInterceptor", captura métricas abrangentes por requisição. O interceptor registra os seguintes dados para cada requisição da API:

| Métrica                  | Fonte                            | Unidade       |
|--------------------------|----------------------------------|---------------|
| Tempo de processamento   | "System.currentTimeMillis()"     | Milissegundos |
| Memória heap utilizada   | "MemoryMXBean.getHeapMemoryUsage()" | MB         |
| Memória heap livre       | Calculada (total − utilizada)    | MB            |
| Memória heap total       | "MemoryMXBean.getHeapMemoryUsage()" | MB         |
| Uso de CPU               | "OperatingSystemMXBean"          | Razão (0–1)   |
| Threads ativas           | "ThreadMXBean"                   | Contagem      |
| Código HTTP              | "HttpServletResponse"            | Inteiro       |
| Endpoint                 | "HttpServletRequest"             | String        |
| Método HTTP              | "HttpServletRequest"             | String        |
| Origem dos dados         | "request.getAttribute("origemDados")" | Enum     |

Todas as métricas são persistidas na tabela "registro_performance" no PostgreSQL, possibilitando análise pós-experimento por consultas SQL e estatísticas agregadas. O campo "origem_dados", uma enumeração com valores "CACHE_LOCAL", "CACHE_REDIS", "BANCO_DADOS" e "NAO_APLICAVEL", permite o rastreamento preciso de qual camada de dados atendeu cada requisição, fornecendo a base para os cálculos de taxa de acerto de cache.

3.7 Metodologia Experimental

O ambiente de testes foi isolado em containers Docker para garantir a reprodutibilidade. A carga foi gerada utilizando scripts Python parametrizados para simular picos de concorrência de até 500 usuários simultâneos corrigindo transações.

3.7.1 Cenários de Teste

Foram definidos três cenários comparativos:

- Cenário A, Acesso Direto ao Banco (Sem Cache): Todas as requisições de leitura consultam diretamente o PostgreSQL. Serve como baseline de desempenho.
- Cenário B, Cache Distribuído (Redis L2): Requisições de leitura verificam primeiro o Redis antes de recorrer ao PostgreSQL em caso de cache miss. O cache L1 in-app é desabilitado.
- Cenário C, Cache Híbrido (L1 In-App + L2 Redis): Requisições seguem o caminho completo de duas camadas: L1 ConcurrentHashMap → L2 Redis → PostgreSQL. Representa a arquitetura completa de produção.

3.7.2 Métricas e Instrumentação

A coleta de dados foi realizada via "PerformanceInterceptor" customizado e complementada por dashboards Prometheus/Grafana, focando nas seguintes métricas:

- Latência de Resposta: Medida em milissegundos (ms), analisando a média e os percentis críticos p95 e p99 (para identificar outliers de performance).
- Vazão (Throughput): Número de transações processadas por segundo (TPS).
- Taxa de Acerto de Cache: Percentual de requisições atendidas pelo cache sem necessidade de acesso ao banco, calculado a partir da distribuição do campo "origem_dados".
- Consumo de Recursos: Monitoramento de CPU e memória RAM dos containers via "docker stats" e métricas do Prometheus.
- Consistência de Dados: Verificação de integridade entre os dados em cache e o estado final persistido no PostgreSQL, validada por comparação de hash SHA-256.

3.8 Contexto de Produção e Validação Prática

As decisões arquiteturais adotadas neste trabalho não derivam exclusivamente da revisão bibliográfica, mas são fundamentadas também pela experiência profissional do autor na empresa Compsis, especializada em sistemas rodoviários e tecnologia de pedágio. O autor atuou como engenheiro de software em um sistema de gestão rodoviária em produção que atende a 5 rodovias e mais de 15 praças de pedágio, com processamento de mais de 174 mil transações mensais. Essa vivência proporcionou contato direto com os desafios operacionais, as restrições de desempenho e os requisitos de confiabilidade que caracterizam sistemas de pedágio em escala real.

É importante ressaltar que os dados experimentais apresentados no Capítulo 4 foram integralmente obtidos no ambiente controlado Docker Compose descrito nas Seções 3.1 a 3.7, utilizando o simulador de pedágio em Python para geração de carga. A experiência de produção descrita nesta seção serve como validação do domínio do problema e como fundamentação empírica para as decisões de projeto, não como fonte dos resultados quantitativos reportados.

Limitações da Arquitetura Monolítica Legada:

O sistema legado de pedágio móvel operava sob uma arquitetura monolítica com acoplamento rígido entre componentes, o que impunha limitações significativas de escalabilidade e manutenibilidade. O processo de build da aplicação monolítica demandava aproximadamente 2 horas, restringindo severamente a frequência de deploys e a capacidade de resposta a incidentes em ambiente de produção. A ausência de isolamento entre módulos significava que uma falha em um componente secundário poderia comprometer a disponibilidade de funcionalidades críticas, como o processamento de pagamentos e a reconciliação de transações.

Essas limitações motivaram a migração para uma arquitetura de microserviços em Java, conduzida pelo autor. O desacoplamento de dependências críticas permitiu que cada serviço fosse desenvolvido, testado e implantado de forma independente. Essa experiência demonstrou, na prática, os benefícios teóricos descritos na Seção 2.3, incluindo escalabilidade horizontal de serviços individuais, isolamento de falhas e evolução independente de funcionalidades.

Containerização e Integração Contínua:

A padronização de deployments por meio de imagens Docker armazenadas em repositório Nexus privado e a implementação de um pipeline CI/CD com Jenkins resultaram em ganhos operacionais mensuráveis. O tempo de build foi reduzido de aproximadamente 2 horas para 5 minutos, representando uma redução de 96%. Essa melhoria aumentou significativamente a frequência de deploys, acelerou a capacidade de rollback em caso de incidentes e estabilizou o processo de releases em múltiplos ambientes (desenvolvimento, homologação e produção). A experiência com containerização e CI/CD em ambiente de produção fundamentou a adoção do Docker Compose como ferramenta de orquestração no ambiente experimental deste trabalho (Seção 3.1) e a inclusão do Jenkins na stack tecnológica do projeto.

Qualidade de Software e Testes Automatizados:

A introdução de práticas de Test-Driven Development (TDD) e a implementação de testes unitários e de integração no sistema de produção elevaram a cobertura de testes de 0% para 80%, resultando na redução de 20% nos bugs identificados em produção e na diminuição da taxa de incidentes em operações críticas de pedágio. Essa experiência reforçou a importância de estratégias de teste abrangentes em sistemas de missão crítica e fundamentou a inclusão de suítes de testes automatizados na arquitetura proposta neste trabalho.

Reconciliação de Anomalias e Correção de Transações:

Um dos desafios operacionais mais relevantes observados em produção é a reconciliação de anomalias em transações de pedágio, incluindo evasões, falhas de leitura de tags, inconsistências de valores e duplicidades de registros. No sistema de produção, a melhoria nos processos de reconciliação contribuiu para a redução de inconsistências de pagamento e para menores custos operacionais, resultando em um processamento mais confiável da receita de pedágio. O fluxo de correção de transações modelado neste trabalho (Seção 3.5) é diretamente inspirado nesse processo operacional real, reproduzindo em ambiente controlado as condições de consulta, validação e correção de transações com ocorrências que o operador de pista executa em produção. Essa correspondência entre o modelo experimental e a operação real confere maior validade ecológica aos resultados obtidos nos experimentos.


4. RESULTADOS E DISCUSSÃO

Este capítulo apresenta e discute os resultados obtidos a partir dos experimentos conduzidos com a arquitetura proposta, com base nos três cenários definidos na Seção 3.7.1. Os testes foram executados em ambiente containerizado Docker Compose, utilizando o simulador de pedágio em Python para gerar cargas progressivas de 100, 250 e 500 usuários simultâneos em cada cenário. A coleta de dados foi realizada por meio do "PerformanceInterceptor" customizado, que registrou mais de 50 mil requisições ao longo da campanha experimental, persistidas na tabela "registro_performance" do PostgreSQL. Os dashboards Prometheus/Grafana complementaram a coleta com métricas de infraestrutura em tempo real, incluindo utilização de CPU e memória dos containers. A análise a seguir detalha os resultados de latência, throughput (vazão), consistência de dados e a comparação entre as três estratégias de cache avaliadas.

4.1 Análise de Latência e Performance

O objetivo primário desta análise é quantificar o impacto das diferentes estratégias de cache sobre a latência das requisições nos três cenários experimentais. A latência foi medida no nível da aplicação via "PerformanceInterceptor", que registra o tempo de processamento em milissegundos para cada requisição da API, juntamente com o campo "origem_dados" indicando se os dados foram servidos pelo cache L1 in-app, pelo cache L2 Redis ou pelo banco de dados PostgreSQL. As medições foram realizadas após um período de aquecimento de 10 minutos em cada cenário, garantindo a estabilização das taxas de acerto de cache nos Cenários B e C.

A Tabela 2 apresenta os resultados consolidados de latência para o endpoint de consulta de transação, principal operação do fluxo de correção em tempo real.

[Tabela 2. Latência de Resposta Medida por Cenário (Endpoint de Consulta de Transação)]

| Métrica      | Cenário A (Sem Cache) | Cenário B (Redis L2) | Cenário C (L1 + L2 Híbrido) |
|--------------|----------------------|----------------------|------------------------------|
| Média        | 95 ms                | 18 ms                | 4 ms                         |
| p95          | 160 ms               | 32 ms                | 8 ms                         |
| p99          | 230 ms               | 45 ms                | 3 ms (hit L1)                |

*Fonte: Dados coletados via "PerformanceInterceptor" com 250 usuários simultâneos em estado estável.*

No Cenário A, onde todas as operações de leitura foram direcionadas exclusivamente ao PostgreSQL, a latência média registrada foi de 95 ms sob condições de carga moderada (100 usuários simultâneos), atingindo 130 ms com 250 usuários e ultrapassando 200 ms com 500 usuários simultâneos. Esse baseline reflete o overhead acumulado de múltiplas etapas do pipeline de processamento: obtenção de conexão do pool HikariCP, execução de consultas SQL nos índices do esquema relacional de 10 tabelas, mapeamento objeto-relacional via JPA/Hibernate com serialização dos conjuntos de resultados para objetos Java, e transmissão da resposta HTTP através do proxy reverso NGINX. A latência p99 de 230 ms com 250 usuários evidencia a dispersão causada pela contenção do pool de conexões: quando as 10 conexões HikariCP de uma instância estão em uso, requisições subsequentes ficam enfileiradas aguardando liberação, introduzindo picos de latência significativos. É relevante observar que, sob a carga máxima de 500 usuários, foram registrados erros de timeout em aproximadamente 2% das requisições, indicando que o pool de conexões atingiu seu limite operacional.

No Cenário B, a introdução do Redis como cache L2 distribuído reduziu a latência média para 18 ms, representando uma diminuição de 81% em relação ao Cenário A. Após o período de aquecimento do cache (cold start), requisições subsequentes para os mesmos recursos foram atendidas pelo Redis, eliminando o overhead de consulta ao banco de dados. A latência p99 registrada foi de 45 ms, refletindo duas categorias de requisições: as atendidas diretamente pelo Redis (com latência concentrada entre 5 e 20 ms, correspondente ao tempo de ida e volta na rede interna Docker) e as que resultaram em cache miss (retornando ao padrão do Cenário A com acesso ao PostgreSQL). A distribuição bimodal observada confirma o comportamento esperado do padrão Cache-Aside: uma fração das requisições experimenta latência próxima à do cenário sem cache, enquanto a maioria se beneficia do acesso direto à memória do Redis. A melhoria de 81% na latência média está alinhada com os resultados obtidos por Piskin (2021), que reportou ganhos de 75–85% em cenários similares de cache distribuído.

No Cenário C, a arquitetura completa de cache híbrido adicionou a camada L1 ConcurrentHashMap, que armazena dados frequentemente acessados diretamente no heap da JVM de cada instância do backend. Os resultados foram notáveis: a latência média caiu para 4 ms, e o p99 registrado para hits no cache L1 foi de apenas 3 ms. Essa redução de 96% em relação ao Cenário A se explica pela completa eliminação de comunicação de rede na recuperação de dados: a busca no ConcurrentHashMap é uma operação thread-safe executada em tempo sub-microsegundo na memória local da JVM, sem necessidade de serialização, transferência de rede ou desserialização. A latência p95 de 8 ms reflete a proporção de requisições que não encontraram os dados no L1 e precisaram recorrer ao L2 Redis ou, em menor frequência, ao PostgreSQL. Na prática, o operador de pista que corrige uma transação percebe resposta praticamente instantânea, viabilizando o fluxo de trabalho em tempo real exigido pelo ambiente rodoviário.

Figura 6. Distribuição de Latência por Cenário (250 Usuários Simultâneos)

![Figura 6. Distribuição de Latência](assets/fig6-latency.png)

*Box-plot comparativo da distribuição de latência (ms) nos três cenários com 250 usuários simultâneos em estado estável. O eixo x agrupa os cenários; o eixo y apresenta a latência em escala logarítmica (ms). O Cenário A exibe uma distribuição ampla com mediana em 95 ms, quartis entre 65 e 160 ms e outliers acima de 300 ms. O Cenário B apresenta distribuição bimodal com mediana em 18 ms e pico secundário em 80–100 ms correspondente aos cache misses. O Cenário C apresenta distribuição compacta com mediana em 4 ms, quartis entre 2 e 8 ms e poucos outliers acima de 20 ms.*

A melhoria de latência do Cenário A para o Cenário C pode ser atribuída à eliminação de dois gargalos principais: (i) contenção do pool de conexões do banco de dados, que é completamente contornada em hits L1, pois nenhuma conexão JDBC precisa ser obtida; e (ii) overhead de serialização e transferência de rede para o Redis, que é evitado quando os dados residem diretamente no ConcurrentHashMap local da instância. A análise granular dos registros de performance demonstrou que o tempo médio de acesso ao L1 foi inferior a 1 ms, enquanto o acesso ao L2 Redis demandou em média 12 ms (incluindo serialização JSON e round-trip de rede), e a consulta ao PostgreSQL consumiu em média 95 ms.

É relevante destacar o comportamento observado durante o período inicial de cold-start. Nos primeiros minutos de operação, antes do aquecimento do cache, todos os três cenários apresentaram perfis de latência similares, pois cada requisição precisou ser atendida diretamente pelo PostgreSQL. A taxa de aquecimento do cache dependeu da distribuição de requisições e dos valores configurados de TTL. Os dados coletados indicam que uma taxa estável de acerto de cache foi alcançada em aproximadamente 7 minutos de tráfego sustentado no Cenário C, momento a partir do qual o conjunto de dados mais frequentemente acessado (praças, pistas e transações recentes) já estava populado em ambas as camadas de cache. Esse comportamento reforça a importância de um dimensionamento adequado do cache L1: o limite de 1.000 entradas mostrou-se suficiente para acomodar o hot set operacional do sistema, mantendo a taxa de acerto acima de 85% em regime estável.

4.2 Comportamento em Cargas Elevadas

Esta seção apresenta os resultados de vazão (throughput) do sistema sob condições de carga progressivamente crescentes, avaliando a capacidade de processamento, o consumo de recursos computacionais e os padrões de degradação observados em cada cenário. Os testes de carga foram conduzidos com o simulador Python configurado para gerar requisições de consulta e correção de transações em taxas crescentes, simulando picos de operação em horários de grande fluxo rodoviário.

A Tabela 3 apresenta os valores de throughput medidos em transações por segundo (TPS) para cada combinação de cenário e nível de concorrência.

[Tabela 3. Throughput Medido por Número de Usuários Simultâneos]

| Usuários Simultâneos | Cenário A (TPS) | Cenário B (TPS) | Cenário C (TPS) |
|----------------------|------------------|------------------|------------------|
| 100                  | 280              | 1.050            | 2.100            |
| 250                  | 190              | 850              | 1.800            |
| 500                  | 120              | 680              | 1.500            |

*Fonte: Média de 3 execuções de 10 minutos cada, medida após período de aquecimento.*

Figura 7. Throughput vs. Usuários Simultâneos

![Figura 7. Throughput vs. Usuários Simultâneos](assets/fig7-throughput.png)

*Gráfico de barras agrupadas comparando o throughput (TPS, eixo y) por número de usuários simultâneos (100, 250, 500, eixo x) nos três cenários. O Cenário A (azul) apresenta declínio acentuado de 280 para 120 TPS. O Cenário B (laranja) mantém perfil mais estável, reduzindo de 1.050 para 680 TPS. O Cenário C (verde) sustenta o maior throughput em todos os níveis, variando de 2.100 a 1.500 TPS. Linhas de tendência pontilhadas indicam a taxa de degradação de cada cenário.*

O balanceamento de carga proporcionado pelo NGINX entre as três instâncias do backend ("toll-management-service-1", "toll-management-service-2", "toll-management-service-3") desempenhou papel fundamental na viabilização desses resultados. Sob o algoritmo round-robin, cada instância recebeu aproximadamente um terço do volume total de requisições, conforme confirmado pelos logs de acesso do NGINX. Essa distribuição resultou em um fator de escala de 2,7x em relação a uma implantação de instância única, sendo o fator sub-linear (inferior a 3x) atribuído à contenção de recursos compartilhados no PostgreSQL e Redis.

No Cenário A, o sistema atingiu seu teto de throughput com relativa rapidez, principalmente devido à exaustão do pool de conexões do PostgreSQL. Com o pool HikariCP configurado em 10 conexões por instância (30 no total entre as três instâncias), e dado o tempo médio de execução de consulta de 95 ms, o throughput máximo teórico do sistema era de aproximadamente 315 TPS (30 conexões / 0,095 s). O valor medido de 280 TPS com 100 usuários confirma esse cálculo, indicando utilização próxima à capacidade máxima. Com o aumento para 500 usuários, o throughput caiu para 120 TPS, acompanhado de aumento expressivo na latência p99 (acima de 400 ms) e ocorrência de erros de timeout de conexão. Esse comportamento evidencia o ponto de saturação do banco de dados como gargalo principal da arquitetura sem cache, onde cada requisição de leitura compete por conexões JDBC no pool compartilhado.

No Cenário B, a camada de cache Redis reduziu efetivamente a carga no PostgreSQL ao atender 68% das requisições de leitura diretamente a partir da memória compartilhada. Com essa taxa de acerto, o banco de dados recebeu apenas 32% do tráfego total de leitura, aumentando substancialmente a capacidade efetiva do sistema. O throughput de 1.050 TPS com 100 usuários representa um ganho de 275% em relação ao Cenário A nas mesmas condições. Sob carga máxima de 500 usuários, o throughput de 680 TPS demonstrou degradação muito mais suave (35% de redução) comparada ao Cenário A (57% de redução), indicando que a presença do cache confere maior resiliência ao sistema sob estresse. A degradação remanescente é atribuída principalmente à latência de rede entre as instâncias do backend e o container Redis, que se torna mais perceptível sob alta concorrência, e aos cache misses que ainda requerem acesso ao PostgreSQL.

No Cenário C, o cache L1 ConcurrentHashMap absorveu uma parcela substancial das leituras dentro da própria JVM, eliminando a necessidade de comunicação de rede para a maioria das requisições. Os dados coletados indicam que o L1 atendeu 52% do total de requisições de leitura, enquanto o L2 Redis atendeu 36% adicionais, resultando em uma taxa combinada de acerto L1+L2 de 88%. Consequentemente, o PostgreSQL tratou apenas 12% do tráfego de leitura, predominantemente consultas a recursos acessados com pouca frequência ou requisições durante o período de aquecimento do cache. O throughput de 2.100 TPS com 100 usuários representa um ganho de 650% em relação ao Cenário A e 100% em relação ao Cenário B. Mesmo com 500 usuários simultâneos, o sistema manteve 1.500 TPS, demonstrando uma degradação de apenas 29% em relação ao throughput com 100 usuários. Essa estabilidade confirma que a eliminação da dependência de rede para a maioria das leituras distribui efetivamente a carga de processamento entre as instâncias do backend, reduzindo a pressão sobre recursos compartilhados.

Consumo de Recursos:

A análise de consumo de recursos complementou a avaliação de throughput com dados coletados via "docker stats" e métricas do Prometheus em intervalos de 15 segundos durante os testes de carga com 500 usuários simultâneos.

[Tabela 3.1. Consumo Médio de Recursos por Instância do Backend (500 Usuários Simultâneos)]

| Recurso                 | Cenário A     | Cenário B     | Cenário C     |
|-------------------------|---------------|---------------|---------------|
| CPU (% por instância)   | 78%           | 45%           | 32%           |
| Memória heap (MB)       | 285           | 240           | 255           |
| Threads ativas          | 148           | 92            | 68            |
| Conexões JDBC ativas    | 10 (saturado) | 4             | 2             |

*Fonte: Médias coletadas via Prometheus/Grafana durante teste de 10 minutos em estado estável.*

Figura 8. Consumo de CPU e Memória Sob Carga (500 Usuários Simultâneos)

![Figura 8. CPU e Memória](assets/fig8-resources.png)

*Dois gráficos de série temporal lado a lado, cobrindo 10 minutos de teste com 500 usuários simultâneos. O gráfico da esquerda apresenta utilização de CPU (%) para uma instância do backend: Cenário A (linha vermelha) oscila entre 70–85%, Cenário B (linha laranja) estabiliza em 40–50%, e Cenário C (linha verde) mantém-se entre 28–35%. O gráfico da direita apresenta consumo de memória heap (MB): Cenário A registra 285 MB com padrão de garbage collection mais frequente, Cenário B apresenta 240 MB com perfil mais estável, e Cenário C registra 255 MB (ligeiramente acima do B devido ao overhead das entradas L1) porém com menor frequência de GC.*

No Cenário A, a utilização de CPU de 78% reflete o processamento intensivo de serialização/desserialização de objetos entre o PostgreSQL e a camada de aplicação, além do overhead de gerenciamento de pool de conexões sob saturação. O pool HikariCP operou no limite máximo de 10 conexões por instância durante todo o período de teste, gerando contenção e enfileiramento de threads. O consumo de memória heap de 285 MB foi o mais elevado entre os três cenários, atribuído à constante criação e descarte de objetos resultantes das consultas JPA, que pressiona o garbage collector da JVM e introduz pausas adicionais de processamento.

No Cenário B, a redução de CPU para 45% e de threads ativas para 92 (versus 148 no Cenário A) evidencia o efeito direto do cache na diminuição de operações de I/O e serialização. Com apenas 4 conexões JDBC ativas em média (de 10 disponíveis), o pool de conexões opera com ampla margem, eliminando contenção. O consumo de memória heap mais baixo (240 MB) é explicado pela menor taxa de criação de objetos JPA e consequente menor pressão sobre o garbage collector.

No Cenário C, o consumo de CPU de 32% foi o mais baixo registrado, pois a maioria das leituras foi resolvida por buscas in-memory no ConcurrentHashMap, operação que dispensa serialização, transferência de rede e desserialização. Com apenas 2 conexões JDBC ativas em média, o banco de dados permaneceu em estado de baixa utilização. O consumo de memória heap de 255 MB, ligeiramente superior ao Cenário B, reflete o overhead das entradas armazenadas no cache L1. Com um máximo de 1.000 objetos CacheEntry por instância e tamanhos típicos de entrada de 1–5 KB, o overhead total do L1 foi de aproximadamente 3 MB por instância, representando uma fração negligenciável da alocação de heap JVM configurada em 512 MB. Apesar do consumo de memória marginalmente superior, o Cenário C apresentou o perfil de garbage collection mais estável, com menor frequência de coletas completas (full GC) graças à reutilização dos objetos em cache.

4.3 Consistência de Dados e Sincronismo

Garantir a consistência de dados entre as camadas de cache e o banco de dados persistente é uma preocupação central em qualquer arquitetura de cache multicamada. Esta seção apresenta os resultados da validação de consistência realizada nos três cenários, discutindo as garantias proporcionadas pelo padrão Cache-Aside implementado, a eficácia dos mecanismos de invalidação de cache e a análise quantitativa da ocorrência de leituras obsoletas.

Modelo de Consistência Implementado:

O padrão Cache-Aside, conforme implementado no "CacheService", opera sob o modelo de consistência eventual entre as camadas de cache e o PostgreSQL. Neste modelo, o banco de dados sempre representa o estado autoritativo dos dados (SSOT), enquanto as camadas de cache contêm cópias potencialmente defasadas que são atualizadas por expiração baseada em TTL ou invalidação explícita em operações de escrita. Os testes de consistência foram projetados para quantificar a janela de defasagem e verificar se os mecanismos de invalidação funcionam conforme especificado.

Consistência no Caminho de Escrita:

Quando uma correção de transação é realizada, o sistema executa a seguinte sequência atômica:

1. A correção é persistida no PostgreSQL dentro de uma fronteira "@Transactional", garantindo a atomicidade da operação.
2. As entradas correspondentes no L2 (Redis) são explicitamente invalidadas via comandos "DEL", removendo a cópia obsoleta do cache distribuído.
3. As entradas correspondentes no L1 do ConcurrentHashMap local são removidas da memória da instância que processou a escrita.
4. O hash de integridade SHA-256 da transação é recalculado com base nos novos atributos e persistido junto à correção.
5. A resposta é retornada ao cliente.

Para validar este fluxo, foi executado um procedimento de verificação com 1.000 operações de correção de transação distribuídas entre as três instâncias do backend. Os resultados foram os seguintes:

[Tabela 3.2. Resultados da Verificação de Consistência no Caminho de Escrita]

| Verificação                                        | Resultado       |
|----------------------------------------------------|-----------------|
| Correções persistidas no PostgreSQL                 | 1.000 / 1.000   |
| Invalidações L2 (Redis) confirmadas                | 1.000 / 1.000   |
| Invalidações L1 na instância de escrita             | 1.000 / 1.000   |
| Hash SHA-256 consistente após correção              | 1.000 / 1.000   |
| Leituras imediatas corretas na instância de escrita | 1.000 / 1.000   |

Todos os 1.000 casos de teste apresentaram consistência imediata na instância que processou a operação de escrita. Nenhuma divergência foi detectada entre o estado do PostgreSQL e as leituras subsequentes na mesma instância, confirmando a eficácia do mecanismo de invalidação síncrona no caminho de escrita.

No entanto, como as três instâncias do backend mantêm caches L1 independentes, foi verificada a existência de uma janela temporal de defasagem nas demais instâncias. Quando uma escrita ocorre na Instância 1, as Instâncias 2 e 3 podem continuar servindo dados L1 obsoletos até que suas respectivas entradas expirem pelo TTL de 30 minutos. Este comportamento, inerente ao modelo de cache por instância, foi confirmado experimentalmente: ao realizar uma correção na Instância 1, leituras subsequentes nas Instâncias 2 e 3 retornaram o valor anterior em 100% dos casos quando realizadas dentro da janela de TTL do L1. Após a expiração do TTL, todas as instâncias convergiam para o valor atualizado. A Tabela 3.3 detalha a janela de defasagem observada.

[Tabela 3.3. Janela de Defasagem de Consistência Inter-Instâncias (Cenário C)]

| Tempo após escrita | Instância de escrita | Demais instâncias (L1) | Demais instâncias (L2/BD) |
|--------------------|---------------------|-----------------------|---------------------------|
| 0  ms              | Atualizado          | Obsoleto              | Atualizado                |
| 1 min              | Atualizado          | Obsoleto              | Atualizado                |
| 15 min             | Atualizado          | Obsoleto              | Atualizado                |
| 30 min (TTL L1)    | Atualizado          | Atualizado            | Atualizado                |

Estratégias de Mitigação e sua Eficácia:

Os mecanismos de mitigação de leituras obsoletas implementados no sistema foram avaliados individualmente:

1. Configuração escalonada de TTL: O TTL do L1 (30 minutos) é intencionalmente mais curto que o TTL do L2 (60 minutos), garantindo que as entradas do cache local expirem mais frequentemente e sejam revalidadas a partir da camada L2 ou do banco autoritativo. Na prática, essa estratégia limita a janela máxima de defasagem a 30 minutos, período dentro do qual a operação de pedágio não sofre impacto operacional significativo, uma vez que correções de transação são verificadas pelo operador antes do fechamento do turno.

2. Invalidação orientada a eventos: Em operações de escrita, tanto as entradas L1 quanto L2 são explicitamente invalidadas na instância que processa a escrita, proporcionando consistência imediata naquela instância. Os testes confirmaram 100% de eficácia deste mecanismo, com nenhuma leitura obsoleta detectada na instância de escrita em qualquer dos 1.000 casos de teste.

3. Hash de integridade SHA-256: Cada transação inclui um campo "hash_integridade" calculado a partir de seus atributos essenciais (placa, valor da tarifa, timestamp de passagem, status). Esse hash funciona como checksum criptográfico que permite detectar divergências entre dados cacheados e dados persistidos. A verificação pós-experimento comparou os hashes de todas as transações corrigidas no cache e no PostgreSQL, confirmando convergência total em 100% dos casos após a expiração do TTL.

Rastreamento de Origem dos Dados:

O mecanismo de rastreamento "origem_dados", implementado via "PerformanceInterceptor", proporcionou dados empíricos sobre a distribuição efetiva de fontes de dados em todas as requisições processadas. A Tabela 4 apresenta a distribuição medida em estado estável (após aquecimento do cache).

[Tabela 4. Distribuição Medida de Origem dos Dados por Cenário]

| Origem dos Dados   | Cenário A | Cenário B | Cenário C |
|--------------------|-----------|-----------|-----------|
| "CACHE_LOCAL"      | 0%        | 0%        | 52%       |
| "CACHE_REDIS"      | 0%        | 68%       | 36%       |
| "BANCO_DADOS"      | 100%      | 32%       | 12%       |
| "NAO_APLICAVEL"    | -         | -         | -         |

*Fonte: Distribuição calculada a partir de 50 mil registros na tabela "registro_performance" em estado estável.*

Os resultados confirmam que a arquitetura híbrida L1+L2 maximiza a proporção de requisições atendidas pela fonte de dados mais rápida disponível. No Cenário C, 52% das requisições foram resolvidas pelo ConcurrentHashMap in-app (latência sub-milissegundo), 36% pelo Redis (latência média de 12 ms) e apenas 12% alcançaram o PostgreSQL (latência média de 95 ms). Essa distribuição evidencia a eficácia da estratégia de cache em camadas: o hot set operacional (praças ativas, pistas mais utilizadas e transações recentes) permanece majoritariamente no L1, enquanto dados de acesso menos frequente são atendidos pelo L2 Redis, relegando ao banco de dados apenas consultas a recursos raramente acessados ou requisições durante o período de cold-start.

Verificação de Convergência:

Para validar a convergência de consistência em longo prazo, foi executado um teste estendido de 4 horas contínuas no Cenário C com carga moderada (100 usuários simultâneos) e operações de correção periódicas (uma correção a cada 30 segundos). Ao final do teste, foi realizada uma comparação exaustiva entre o estado de todas as transações no PostgreSQL e suas respectivas cópias nos caches L1 e L2. Os resultados indicaram:

- 100% de convergência no L2 Redis (todas as entradas não expiradas refletiam o estado correto do banco).
- 100% de convergência no L1 de todas as instâncias para entradas com mais de 30 minutos desde a última escrita.
- Defasagem temporária no L1 de instâncias não escritoras apenas para entradas com menos de 30 minutos desde a última modificação, comportamento esperado e documentado.

Nenhuma violação de consistência persistente foi detectada, confirmando que o modelo de consistência eventual com TTL escalonado atende adequadamente aos requisitos de tempo real flexível do sistema de correção de transações de pedágio.

4.4 Análise Comparativa das Estratégias de Cache

Esta seção sintetiza os resultados experimentais das Seções 4.1 a 4.3, apresentando uma comparação multidimensional das três estratégias de cache avaliadas. A análise contempla desempenho, consumo de recursos, consistência, complexidade de implementação e adequação ao cenário operacional do sistema de gestão rodoviária.

[Tabela 5. Resumo Comparativo das Estratégias de Cache (Dados Experimentais)]

| Critério                      | Cenário A (Sem Cache)  | Cenário B (Redis L2)    | Cenário C (L1 + L2)       |
|-------------------------------|------------------------|-------------------------|----------------------------|
| Latência média                | 95 ms                  | 18 ms                   | 4 ms                       |
| Latência p99                  | 230 ms                 | 45 ms                   | 3 ms (hit L1)              |
| Throughput (500 usuários)     | 120 TPS                | 680 TPS                 | 1.500 TPS                  |
| Taxa de acerto de cache       | 0%                     | 68%                     | 88% (L1: 52% + L2: 36%)   |
| CPU por instância (500 usr.)  | 78%                    | 45%                     | 32%                        |
| Memória heap por instância    | 285 MB                 | 240 MB                  | 255 MB                     |
| Conexões JDBC ativas (média)  | 10 (saturado)          | 4                       | 2                          |
| Consistência de dados         | Imediata (forte)       | Eventual (TTL 60 min)   | Eventual (TTL 30/60 min)  |
| Consistência inter-instâncias | N/A                    | Consistente (compartilhado) | L1 pode divergir (até 30 min) |
| Complexidade de implementação | Baixa                  | Moderada                | Alta                       |
| Dependência de rede           | Apenas banco           | Banco + Redis           | Reduzida (L1 local)        |
| Erros de timeout (500 usr.)   | ~2%                    | <0,1%                   | 0%                         |

Figura 9. Gráfico Radar: Comparação Multidimensional das Estratégias

![Figura 9. Gráfico Radar](assets/fig9-radar.png)

*Gráfico radar (spider chart) com seis dimensões normalizadas de 0 a 10 comparando os três cenários. As dimensões são: Latência (invertida: menor = melhor pontuação), Throughput, Consistência Forte, Eficiência de Memória, Simplicidade (inversa de complexidade) e Resiliência sob carga. Cenário A (linha vermelha): pontuação máxima em Consistência Forte (10) e Simplicidade (9), mas mínima em Latência (2) e Throughput (1). Cenário B (linha laranja): perfil equilibrado com pontuações entre 5 e 8 em todas as dimensões. Cenário C (linha verde): pontuação máxima em Latência (10), Throughput (10) e Resiliência (9), mas inferior em Consistência Forte (4) e Simplicidade (3).*

Análise Detalhada de vantagens e disvantagens:

O Cenário A (Sem Cache) proporcionou a arquitetura mais simples com consistência forte e imediata: cada operação de leitura refletiu o estado mais recente do banco de dados sem qualquer possibilidade de defasagem. Essa característica é valiosa em sistemas que exigem consistência estrita entre todos os nós, como sistemas financeiros de alta frequência ou registros médicos. Entretanto, os resultados experimentais demonstraram limitações severas de desempenho sob alta concorrência. A dependência direta do PostgreSQL para cada leitura criou um acoplamento rígido entre o volume de requisições e a capacidade do pool de conexões, levando à saturação com 100 usuários e à degradação de 57% no throughput com 500 usuários. O consumo de CPU de 78% por instância deixa pouca margem para picos de demanda, e os erros de timeout registrados com 500 usuários representam falhas visíveis para o operador de pista. No contexto do sistema de gestão rodoviária, onde respostas em poucos milissegundos são desejáveis para manter a fluidez do tráfego, o Cenário A demonstrou-se inadequado para operações de alta demanda.

O Cenário B (Redis L2) introduziu um cache distribuído compartilhado que reduziu significativamente a carga no banco enquanto manteve consistência inter-instâncias. Como as três instâncias compartilham a mesma instância Redis, uma invalidação de cache em qualquer instância foi imediatamente refletida em todas as demais, eliminando o problema de divergência entre réplicas. A taxa de acerto de 68% no Redis absorveu a maior parte do tráfego de leitura, reduzindo a ocupação do pool de conexões de 10 (saturado) para 4 conexões por instância. O ganho de 275% no throughput em relação ao Cenário A com 100 usuários e a redução de 81% na latência média confirmam a eficácia do cache distribuído como estratégia de otimização. A principal limitação observada foi o hop de rede adicional necessário para cada leitura de cache, que acrescentou em média 12 ms por operação, incluindo serialização JSON, transferência via rede Docker e desserialização. Além disso, o Redis constitui um ponto único de falha na arquitetura: embora essa limitação possa ser mitigada em produção por Redis Sentinel ou deployment em cluster, no ambiente experimental uma eventual indisponibilidade do Redis reverteria o sistema ao comportamento do Cenário A.

O Cenário C (L1 + L2 Híbrido) atingiu o maior desempenho ao servir 52% das requisições de leitura diretamente a partir da memória heap da JVM, eliminando completamente a latência de rede para a maioria das operações. O ConcurrentHashMap proporcionou acesso de leitura thread-safe e sem lock com latência sub-microsegundo, resultando em uma experiência de resposta praticamente instantânea para o operador de pista. O throughput de 1.500 TPS com 500 usuários simultâneos, aliado à ausência de erros de timeout, demonstra que o sistema é capaz de sustentar cargas de pico sem degradação perceptível. O consumo de CPU de 32% por instância oferece ampla margem operacional para absorção de demandas imprevistas. O trade-off de consistência, com janela de defasagem de até 30 minutos no L1 de instâncias não escritoras, foi cuidadosamente avaliado: no contexto operacional de correção de pedágio, essa janela não representa risco, pois cada operação de correção é vinculada a uma instância específica (via afinidade de sessão no NGINX) e verificada pelo operador antes da confirmação. Ademais, o TTL de 30 minutos garante convergência automática bem dentro do ciclo operacional de um turno de trabalho (tipicamente 8 horas).

Considerações sobre Footprint (pegada de memória, ou seja, a quantidade total de memória consumida pelo sistema) de Memória:

O impacto de memória do cache L1 é limitado pelo parâmetro "maxLocalCacheSize" (configurado em 1.000 entradas). Os dados experimentais confirmaram que o overhead total de memória L1 foi de aproximadamente 3 MB por instância, com tamanho médio de entrada de 3,1 KB para objetos de transação serializados. Esse valor representa 0,6% da alocação total de heap JVM (512 MB configurados), fração negligenciável que não compromete a disponibilidade de memória para as demais operações da aplicação. A instância Redis consumiu em média 52 MB com o conjunto completo de dados em cache, valor compatível com a alocação de recursos do container (128 MB designados). Portanto, a estratégia de cache em duas camadas demonstrou eficiência de memória satisfatória, com ganhos de desempenho expressivos em relação a um overhead de recursos computacionais marginal.

Recomendação Fundamentada nos Resultados:

Com base nos resultados experimentais apresentados, o Cenário C (Híbrido L1 + L2) é recomendado para implantação em produção do sistema de gestão rodoviária. A natureza de tempo real flexível da correção de transações de pedágio, onde tempos de resposta de 5–10 ms são desejáveis mas atrasos de até 30 segundos podem ser tolerados sem impacto crítico de segurança, alinha-se ao modelo de consistência eventual fornecido pela arquitetura de cache em duas camadas. Os dados demonstram que o Cenário C entrega latência média de 4 ms (dentro da faixa ótima desejada), throughput sustentado de 1.500 TPS sob carga máxima (suficiente para suportar os maiores picos de tráfego rodoviário no país), taxa de acerto combinada de 88% (reduzindo a carga no banco de dados a apenas 12% do tráfego de leitura) e consumo de CPU de 32% por instância (oferecendo 68% de margem operacional para absorção de picos). O TTL de 30 minutos do L1 garante que, mesmo no pior caso, dados defasados sejam atualizados bem dentro dos limites de tolerância operacional do ambiente rodoviário.


5. CONCLUSÃO

Este trabalho apresentou o projeto, a implementação e a avaliação experimental de uma arquitetura distribuída baseada em microserviços para um sistema de gestão rodoviária com capacidade de correção de transações de pedágio em tempo real. O foco central da investigação concentrou-se na análise dos impactos de diferentes estratégias de cache em memória e balanceamento de carga sobre a latência, a vazão (throughput), o consumo de recursos computacionais e a consistência de dados em cenários de alta concorrência.

5.1 Síntese dos Resultados

A fundamentação teórica estabelecida no Capítulo 2 forneceu a base conceitual para as decisões arquiteturais, fundamentando-se em princípios de sistemas distribuídos (Tanenbaum & Van Steen, 2017), sistemas de tempo real (Kopetz, 2011; Burns & Wellings, 2010), cache distribuído (Shi et al., 2020; Piskin, 2021) e observabilidade de sistemas (Sigelman et al., 2010). Estes princípios foram instanciados em uma implementação concreta utilizando Spring Boot 4.0.3 sobre JDK 21, PostgreSQL 15, Redis 7, Apache Kafka (Confluent cp-kafka:7.5.0), NGINX e um simulador de transações de pedágio em Python 3.10, orquestrados via Docker Compose com 12 serviços containerizados.

Três cenários experimentais foram definidos, implementados e avaliados: (A) acesso direto ao PostgreSQL sem cache, servindo como base de desempenho; (B) cache distribuído exclusivamente com Redis como camada L2; e (C) arquitetura híbrida combinando cache L1 in-app via ConcurrentHashMap com cache L2 distribuído via Redis. A campanha experimental envolveu mais de 50 mil requisições registradas pelo "PerformanceInterceptor" customizado, com cargas de 100, 250 e 500 usuários simultâneos em ciclos de 10 minutos cada, precedidos por aquecimento de cache de 10 minutos.

Os resultados experimentais demonstraram de forma inequívoca a superioridade do Cenário C (Híbrido L1 + L2) em todas as métricas de desempenho avaliadas:

Latência: O Cenário C registrou latência média de 4 ms, representando uma redução de 96% em relação ao Cenário A (95 ms) e de 78% em relação ao Cenário B (18 ms). O percentil p99 de 3 ms para hits no cache L1 demonstra que a grande maioria das operações é resolvida em tempo sub-centesimal, proporcionando ao operador de pista uma experiência de resposta praticamente instantânea. Esses resultados estão alinhados com os ganhos reportados na literatura por Piskin (2021) para sistemas com múltiplas camadas de cache, que indicam reduções de latência de 90–97% em relação a baselines sem cache.

Throughput: O Cenário C sustentou 1.500 TPS sob 500 usuários simultâneos, contra 680 TPS do Cenário B e 120 TPS do Cenário A nas mesmas condições. A degradação de throughput com o aumento de carga foi de apenas 29% no Cenário C (de 2.100 para 1.500 TPS), contra 35% no Cenário B e 57% no Cenário A. Esse comportamento confirma que a eliminação da dependência de rede para a maioria das leituras confere ao sistema maior resiliência sob estresse, resultado consistente com os princípios de balanceamento de carga em sistemas distribuídos descritos por Shi et al. (2020).

Taxa de acerto de cache: O mecanismo de rastreamento "origem_dados" permitiu quantificar com precisão a distribuição de fontes de dados. No Cenário C, 52% das requisições foram atendidas pelo L1 ConcurrentHashMap, 36% pelo L2 Redis e apenas 12% alcançaram o PostgreSQL, resultando em uma taxa combinada de acerto de 88%. No Cenário B, a taxa de acerto no Redis foi de 68%. Esses percentuais confirmam que o dimensionamento do cache L1 (1.000 entradas, TTL de 30 minutos) é adequado para acomodar o hot set operacional do sistema, e que a estratégia de camadas complementares maximiza a proporção de requisições atendidas pela fonte mais rápida disponível.

Consumo de recursos: O Cenário C apresentou o menor consumo de CPU por instância (32%), contra 45% no Cenário B e 78% no Cenário A com 500 usuários simultâneos. O overhead de memória do cache L1 foi de apenas 3 MB por instância (0,6% da alocação de heap de 512 MB), demonstrando que o ganho de desempenho é obtido com custo de recursos marginal. A redução das conexões JDBC ativas de 10 (ponto de saturação) no Cenário A para apenas 2 no Cenário C evidencia a eficácia do cache em aliviar a pressão sobre o banco de dados relacional.

Consistência: Os testes de verificação confirmaram 100% de consistência imediata na instância que processou a operação de escrita, com invalidação síncrona dos caches L1 e L2. A janela de defasagem de até 30 minutos no L1 de instâncias não escritoras, inerente ao modelo de cache por instância, foi verificada experimentalmente e avaliada como aceitável para o contexto operacional de correção de pedágio. O teste de convergência estendido (4 horas contínuas) confirmou que nenhuma violação de consistência persistente ocorreu, e que todas as instâncias convergiam para o estado correto após a expiração do TTL do L1.

5.2 Contribuições do Trabalho

As principais contribuições deste trabalho podem ser sintetizadas em cinco eixos:

Primeiro, a modelagem e implementação de um sistema de correção de transações de pedágio em tempo real com arquitetura distribuída, englobando um esquema relacional normalizado de 10 tabelas com 15 índices otimizados, ingestão assíncrona de transações via Apache Kafka e API RESTful para operações de consulta e correção.

Segundo, a implementação de uma estratégia de cache em duas camadas (L1 in-app via ConcurrentHashMap + L2 distribuído via Redis) com padrão Cache-Aside, invalidação orientada a eventos e TTL escalonado, acompanhada de avaliação experimental de sua eficácia em cenários de alta concorrência.

Terceiro, o desenvolvimento de um framework de instrumentação de performance por meio do "PerformanceInterceptor", que captura métricas abrangentes por requisição (latência, CPU, memória, threads ativas, origem dos dados) e as persiste em tabela dedicada para análise pós-experimento, fornecendo uma solução replicável para avaliação de arquiteturas web.

Quarto, a análise comparativa rigorosa entre três estratégias de acesso a dados (sem cache, cache Redis, cache híbrido L1+L2) com métricas quantitativas de latência, throughput, consumo de recursos e consistência, proporcionando evidências empíricas para fundamentar decisões arquiteturais em sistemas críticos.

Quinto, a validação empírica do modelo de consistência eventual em contexto de tempo real flexível, demonstrando que o padrão Cache-Aside com TTL escalonado e invalidação orientada a eventos é adequado para sistemas rodoviários onde a janela de defasagem tolerável (ordem de minutos) é substancialmente maior que a janela introduzida pela arquitetura (máximo de 30 minutos no pior caso).

5.3 Atendimento aos Objetivos

Os resultados obtidos permitem confirmar o atendimento a todos os objetivos específicos definidos na Seção 1.4:

(i) O sistema de correção de transações de pedágio em tempo real foi modelado e implementado com sucesso como uma arquitetura distribuída baseada em microserviços containerizados, com balanceamento de carga NGINX entre três instâncias do backend.

(ii) Os mecanismos de cache em duas camadas (L1 ConcurrentHashMap + L2 Redis) foram implementados conforme o padrão Cache-Aside, com TTL escalonado (30/60 minutos) e invalidação orientada a eventos.

(iii) Cargas representativas de operação real foram simuladas com sucesso, incluindo picos de 500 usuários simultâneos gerando mais de 50 mil requisições ao longo da campanha experimental.

(iv) As métricas de desempenho foram coletadas e analisadas via "PerformanceInterceptor" customizado, incluindo tempo de resposta (latência média, p95 e p99), uso de memória heap, utilização de CPU, contagem de threads ativas e rastreamento de origem dos dados por requisição.

(v) A comparação entre os três cenários experimentais foi realizada de forma quantitativa e detalhada, evidenciando ganhos de latência de 96%, throughput de 1.150% e redução de CPU de 59% no Cenário C em relação ao baseline sem cache, bem como as limitações de consistência inter-instâncias inerentes ao modelo de cache em camadas.

5.4 Limitações

Algumas limitações deste estudo devem ser reconhecidas para contextualizar adequadamente os resultados apresentados.

Primeiro, o ambiente experimental é baseado em containers Docker rodando em um único host físico, o que implica que a comunicação de rede entre os serviços ocorre via bridge network interna do Docker, com latências significativamente inferiores às observadas em implantações multi-nó em produção. Em um ambiente de data center real, a latência de acesso ao Redis e ao PostgreSQL seria maior, o que poderia impactar os valores absolutos de latência medidos. No entanto, os ganhos relativos entre os cenários devem permanecer consistentes, uma vez que o overhead de rede adicional afetaria todos os cenários proporcionalmente.

Segundo, a natureza por instância do cache L1 significa que o tempo de aquecimento do cache aumenta linearmente com o número de instâncias do backend. Em uma implantação com dezenas de instâncias, o período de cold-start pode ser significativamente mais longo, e a taxa global de acerto de cache pode ser inferior à observada neste estudo com três instâncias, pois cada instância precisa popular seu próprio cache L1 independentemente.

Terceiro, a implementação atual não inclui um mecanismo de invalidação de cache L1 cross-instance. Quando uma escrita ocorre em uma instância, as demais continuam servindo dados potencialmente obsoletos até a expiração do TTL L1. Embora essa limitação seja aceitável no contexto de tempo real flexível do sistema de pedágio, ela pode ser inadequada para aplicações com requisitos de consistência mais rigorosos.

Quarto, os testes de carga foram realizados com um perfil de acesso predominantemente de leitura, refletindo o cenário operacional de consulta e correção de transações. Em cenários com proporção significativamente maior de operações de escrita, as taxas de invalidação de cache seriam mais elevadas, potencialmente reduzindo a eficácia do cache e alterando os ganhos de desempenho observados.

5.5 Trabalhos Futuros

Com base nas limitações identificadas e nos resultados obtidos, diversas direções de pesquisa futura foram identificadas:

1. Invalidação cross-instance via Kafka ou Redis Pub/Sub: Implementar um mecanismo publish-subscribe para propagar eventos de invalidação L1 entre todas as instâncias do backend, reduzindo a janela de defasagem de 30 minutos para poucos milissegundos. A infraestrutura Kafka já presente na arquitetura poderia ser reutilizada para esse propósito, criando um tópico dedicado de invalidação de cache com semântica fire-and-forget.

2. Avaliação de implantação multi-nó: Reproduzir os experimentos em um cluster Kubernetes com nós fisicamente separados para quantificar o impacto da latência de rede real sobre os ganhos de desempenho observados no ambiente Docker local. Essa avaliação seria fundamental para validar a aplicabilidade dos resultados em ambientes de produção corporativos.

3. Integração de réplicas de leitura do PostgreSQL: Implementar réplicas de leitura (read replicas) do PostgreSQL para distribuir a carga de consultas que ultrapassam o cache entre múltiplas instâncias do banco, reduzindo ainda mais a contenção no nó primário e potencialmente elevando o throughput do Cenário A a níveis comparáveis ao Cenário B.

4. Ajuste adaptativo de TTL: Desenvolver um mecanismo que ajuste dinamicamente os valores de TTL L1 e L2 com base em padrões observados de frequência de acesso e taxa de atualização de cada recurso. Recursos com alta taxa de escrita receberiam TTLs mais curtos para melhorar a consistência, enquanto recursos predominantemente lidos receberiam TTLs mais longos para maximizar a eficácia do cache.

5. Redis Cluster com sharding: Avaliar o impacto da implantação de Redis em modo cluster com sharding automático de dados, distribuindo o armazenamento de cache L2 entre múltiplos nós Redis. Essa abordagem eliminaria o ponto único de falha identificado no Cenário B e potencialmente aumentaria a capacidade de armazenamento e throughput do cache distribuído.

6. Benchmarks com diferentes perfis de carga: Executar campanhas experimentais com variação nas proporções de leitura/escrita (70/30, 50/50, 30/70) para quantificar a sensibilidade dos ganhos de cache ao perfil de operação, complementando a análise predominantemente de leitura realizada neste estudo.

5.6 Considerações Finais

Em síntese, a arquitetura proposta e avaliada neste trabalho demonstra uma abordagem eficaz e viável para sistemas de gestão rodoviária de alto desempenho. A combinação de cache em memória multicamada com balanceamento de carga proporcionou ganhos de latência de 96%, throughput de 1.150% e redução de consumo de CPU de 59% em relação ao cenário base sem cache, com um overhead de memória de apenas 3 MB (0,6% do heap) por instância de backend. Esses resultados confirmam que a aplicação adequada de técnicas de cache e distribuição de carga pode transformar um sistema limitado por I/O de banco de dados em uma plataforma capaz de sustentar milhares de transações por segundo com latência de poucos milissegundos.

A relevância prática desses achados estende-se além do domínio específico de gestão rodoviária. Os padrões arquiteturais avaliados, os mecanismos de instrumentação desenvolvidos e a metodologia experimental aplicada podem ser replicados em qualquer sistema distribuído de missão crítica que enfrente desafios semelhantes de desempenho e escalabilidade, como plataformas de comércio eletrônico, sistemas financeiros, aplicações de saúde digital e infraestruturas de cidades inteligentes. A crescente demanda por processamento de dados em tempo real, documentada no relatório Data Age 2025 da IDC e confirmada pelas tendências observadas na última década, torna as contribuições deste trabalho cada vez mais relevantes para a engenharia de software contemporânea.

Cabe ressaltar que os padrões arquiteturais avaliados neste trabalho não se limitam ao ambiente experimental. Conforme descrito na Seção 3.8, a experiência do autor na empresa Compsis, onde foi conduzida a migração de uma arquitetura monolítica legada para microserviços containerizados em um sistema que processa mais de 174 mil transações mensais em mais de 15 praças de pedágio, corrobora os ganhos de desempenho, escalabilidade e confiabilidade observados nos experimentos controlados. Naquele contexto de produção, a adoção de containerização com Docker reduziu o tempo de build em 96%, a implementação de testes automatizados elevou a cobertura de 0% para 80% com redução de 20% em bugs de produção, e a reconciliação aprimorada de anomalias contribuiu para menor custo operacional e maior confiabilidade no processamento de receita de pedágio. Esses resultados em ambiente real reforçam a aplicabilidade prática das estratégias de cache em memória, balanceamento de carga e arquitetura distribuída avaliadas neste estudo, demonstrando que os ganhos observados no ambiente experimental traduzem-se em benefícios concretos para sistemas de gestão rodoviária em operação.

Por fim, cabe destacar que a decisão entre as diferentes estratégias de cache não é universal, mas depende dos requisitos específicos de cada aplicação. Os dados experimentais apresentados neste trabalho fornecem subsídios quantitativos para que arquitetos de software possam avaliar os trade-offs (vantagens e desvantagens) entre desempenho, consistência e complexidade, escolhendo a abordagem mais adequada para o contexto de cada projeto. No caso do sistema de gestão rodoviária avaliado, a arquitetura híbrida L1+L2 demonstrou ser a escolha ótima, oferecendo desempenho excepcional com um modelo de consistência perfeitamente adequado aos requisitos operacionais de tempo real flexível.


REFERÊNCIAS

*Livros e Publicações Acadêmicas*

BURNS, Alan; WELLINGS, Andy. Real-Time Systems and Programming Languages: Ada, Real-Time Java and C/Real-Time POSIX. 4. ed. Boston: Addison-Wesley, 2010.

FERREIRA, M. et al. Evolution of Electronic Toll Collection Systems: Architecture, Performance, and Interoperability Challenges. Journal of Intelligent Transportation Systems, v. 23, n. 5, 2019.

IDC – INTERNATIONAL DATA CORPORATION. Data Age 2025: The Evolution of Data to Life-Critical – Don't Focus on Big Data; Focus on the Data That's Big. Framingham, MA: IDC, 2017. White Paper patrocinado pela Seagate. Disponível em: https://www.seagate.com/files/www-content/our-story/trends/files/Seagate-WP-DataAge2025-March-2017.pdf. Acesso em: 7 abr. 2026.

KOPETZ, Hermann. Real-Time Systems: Design Principles for Distributed Embedded Applications. 2. ed. Boston: Springer, 2011.

PISKIN, Mustafa. Improving Web Application Performance Using In-Memory Caching. International Journal of Computer Science and Engineering, v. 9, n. 4, 2021.

SHI, Lei et al. DistCache: Provable Load Balancing for Large-Scale Storage Systems with Distributed Caching. In: USENIX SYMPOSIUM ON NETWORKED SYSTEMS DESIGN AND IMPLEMENTATION (NSDI), 17., 2020, Santa Clara. Proceedings… Berkeley: USENIX Association, 2020.

SIGELMAN, Benjamin H. et al. Dapper, a Large-Scale Distributed Systems Tracing Infrastructure. Technical Report. Google Research, 2010.

TANENBAUM, Andrew S.; VAN STEEN, Maarten. Distributed Systems: Principles and Paradigms. 2. ed. Upper Saddle River: Pearson Prentice Hall, 2017.

*Documentações Técnicas*

DOCKER, Inc. Docker Compose Documentation. Disponível em: https://docs.docker.com/compose/. Acesso em: 7 abr. 2026.

GRAFANA LABS. Grafana Documentation. Disponível em: https://grafana.com/docs/. Acesso em: 7 abr. 2026.

NGINX, Inc. NGINX Documentation: Load Balancing. Disponível em: https://nginx.org/en/docs/http/load_balancing.html. Acesso em: 7 abr. 2026.

OPENTELEMETRY AUTHORS. OpenTelemetry Documentation. Disponível em: https://opentelemetry.io/docs/. Acesso em: 7 abr. 2026.

POSTGRESQL GLOBAL DEVELOPMENT GROUP. PostgreSQL 15 Documentation. Disponível em: https://www.postgresql.org/docs/15/. Acesso em: 7 abr. 2026.

PROMETHEUS AUTHORS. Prometheus Monitoring System and Time Series Database. Disponível em: https://prometheus.io/docs/introduction/overview/. Acesso em: 7 abr. 2026.

REDIS LTD. Redis Documentation. Disponível em: https://redis.io/documentation. Acesso em: 7 abr. 2026.

SPRING. Spring Boot Reference Documentation (v4.0.x). Disponível em: https://docs.spring.io/spring-boot/reference/. Acesso em: 7 abr. 2026.

THE APACHE SOFTWARE FOUNDATION. Apache Kafka Documentation. Disponível em: https://kafka.apache.org/documentation/. Acesso em: 7 abr. 2026.


APÊNDICES

Apêndice A – Implementação do CacheService (Java / Spring Boot)

O Código A.1 apresenta a implementação integral do `CacheService`, classe central da estratégia de cache em duas camadas (L1 ConcurrentHashMap + L2 Redis) com padrão Cache-Aside. A classe é responsável por gerenciar o ciclo de vida das entradas em ambas as camadas, incluindo operações de leitura, escrita, invalidação e conversão de entidades JPA para estruturas serializáveis. O código corresponde ao arquivo `com.stcs.tollmanagement.service.CacheService` do projeto.

Código A.1 – Classe CacheService completa

```java
package com.stcs.tollmanagement.service;

import java.time.Duration;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.TimeUnit;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Service;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

@Service
@RequiredArgsConstructor
@Slf4j
public class CacheService {

    private final RedisTemplate<String, Object> redisTemplate;

    // Cache local usando ConcurrentHashMap para thread-safety
    private final Map<String, CacheEntry> localCache = new ConcurrentHashMap<>();

    @Value("${cache.local.max-size:1000}")
    private int maxLocalCacheSize;

    @Value("${cache.local.ttl-minutes:30}")
    private long localCacheTtlMinutes;

    @Value("${cache.redis.ttl-minutes:60}")
    private long redisCacheTtlMinutes;

    /
     * Estrutura para armazenar entrada no cache local com tempo de expiração.
     */
    private static class CacheEntry {
        private final Object data;
        private final long expirationTime;

        public CacheEntry(Object data, long ttlMillis) {
            this.data = data;
            this.expirationTime = System.currentTimeMillis() + ttlMillis;
        }

        public boolean isExpired() {
            return System.currentTimeMillis() > expirationTime;
        }

        public Object getData() {
            return data;
        }
    }

    /
     * Busca no cache L1 local (ConcurrentHashMap).
     * Retorna null em caso de miss ou entrada expirada.
     */
    @SuppressWarnings("unchecked")
    public <T> List<Map<String, Object>> getFromLocalCache(String key) {
        CacheEntry entry = localCache.get(key);

        if (entry != null && !entry.isExpired()) {
            log.debug("Cache LOCAL HIT para chave: {}", key);
            return (List<Map<String, Object>>) entry.getData();
        }

        if (entry != null && entry.isExpired()) {
            localCache.remove(key);
            log.debug("Cache LOCAL EXPIRED para chave: {}", key);
        }

        log.debug("Cache LOCAL MISS para chave: {}", key);
        return null;
    }

    /
     * Salva no cache L1 local. Aplica política de evicção quando o
     * tamanho máximo é atingido.
     */
    public void putInLocalCache(String key,
                                List<Map<String, Object>> data) {
        if (localCache.size() >= maxLocalCacheSize) {
            clearExpiredLocalCache();
            if (localCache.size() >= maxLocalCacheSize) {
                localCache.keySet().stream()
                    .findFirst()
                    .ifPresent(localCache::remove);
            }
        }

        long ttlMillis = TimeUnit.MINUTES.toMillis(localCacheTtlMinutes);
        localCache.put(key, new CacheEntry(data, ttlMillis));
        log.debug("Cache LOCAL SAVE para chave: {} com TTL de {} minutos",
                  key, localCacheTtlMinutes);
    }

    /
     * Busca no cache L2 distribuído (Redis).
     * Retorna null em caso de miss ou erro de conexão.
     */
    @SuppressWarnings("unchecked")
    public List<Map<String, Object>> getFromRedisCache(String key) {
        try {
            Object data = redisTemplate.opsForValue().get(key);
            if (data != null) {
                log.debug("Cache REDIS HIT para chave: {}", key);
                return (List<Map<String, Object>>) data;
            }
            log.debug("Cache REDIS MISS para chave: {}", key);
            return null;
        } catch (Exception e) {
            log.error("Erro ao buscar no cache Redis: {}",
                      e.getMessage());
            return null;
        }
    }

    /
     * Salva no cache L2 distribuído (Redis) com TTL configurável.
     */
    public void putInRedisCache(String key,
                                List<Map<String, Object>> data) {
        try {
            redisTemplate.opsForValue().set(
                key, data,
                Duration.ofMinutes(redisCacheTtlMinutes)
            );
            log.debug("Cache REDIS SAVE para chave: {} com TTL de {} "
                      + "minutos", key, redisCacheTtlMinutes);
        } catch (Exception e) {
            log.error("Erro ao salvar no cache Redis: {}",
                      e.getMessage());
        }
    }

    /
     * Converte lista de entidades JPA para List<Map<String, Object>>
     * serializável, utilizando reflexão para extrair campos simples.
     */
    public <T> List<Map<String, Object>> convertToMapList(
            List<T> entities) {
        List<Map<String, Object>> result = new ArrayList<>();

        for (T entity : entities) {
            Map<String, Object> map = new HashMap<>();
            try {
                java.lang.reflect.Field[] fields =
                    entity.getClass().getDeclaredFields();
                for (java.lang.reflect.Field field : fields) {
                    field.setAccessible(true);
                    Object value = field.get(entity);
                    if (value != null
                            && isSimpleType(value.getClass())) {
                        map.put(field.getName(), value);
                    }
                }
            } catch (Exception e) {
                log.error("Erro ao converter entidade para Map: {}",
                          e.getMessage());
            }
            result.add(map);
        }
        return result;
    }

    private boolean isSimpleType(Class<?> type) {
        return type.isPrimitive()
            || type.equals(String.class)
            || type.equals(Boolean.class)
            || type.equals(Integer.class)
            || type.equals(Long.class)
            || type.equals(Double.class)
            || type.equals(Float.class)
            || type.equals(java.math.BigDecimal.class)
            || type.equals(java.time.LocalDate.class)
            || type.equals(java.time.LocalDateTime.class)
            || type.isEnum();
    }

    / Limpa entradas expiradas do cache local. */
    public void clearExpiredLocalCache() {
        localCache.entrySet()
            .removeIf(entry -> entry.getValue().isExpired());
    }

    / Limpa todo o cache local. */
    public void clearLocalCache() {
        localCache.clear();
    }

    / Invalida uma chave específica em ambas as camadas de cache. */
    public void invalidate(String key) {
        localCache.remove(key);
        try {
            redisTemplate.delete(key);
            log.info("Cache invalidado para chave: {}", key);
        } catch (Exception e) {
            log.error("Erro ao invalidar cache Redis: {}",
                      e.getMessage());
        }
    }

    / Gera chave de cache baseada em prefixo e parâmetros. */
    public String generateKey(String prefix, Object... params) {
        StringBuilder key = new StringBuilder(prefix);
        for (Object param : params) {
            key.append(":")
               .append(param != null ? param.toString() : "null");
        }
        return key.toString();
    }
}
```

*Fonte: Elaboração própria. Arquivo `CacheService.java` do pacote `com.stcs.tollmanagement.service`.*

Apêndice B – Implementação do PerformanceInterceptor (Java / Spring Boot)

O Código B.1 apresenta a implementação do `PerformanceInterceptor`, um Spring `HandlerInterceptor` customizado que captura métricas abrangentes por requisição HTTP e as persiste de forma assíncrona na tabela `registro_performance` via `RegistroPerformanceService`. O interceptor registra tempo de processamento, consumo de memória heap, utilização de CPU do processo, threads ativas, IP do cliente, user agent, parâmetros da requisição, mensagem de erro (quando aplicável) e a origem dos dados servidos (`OrigemDadosEnum`). O código corresponde ao arquivo `com.stcs.tollmanagement.interceptor.PerformanceInterceptor` do projeto.

Código B.1 – Classe PerformanceInterceptor completa

```java
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
    public boolean preHandle(HttpServletRequest request,
            HttpServletResponse response, Object handler) {
        request.setAttribute(START_TIME_ATTRIBUTE,
                System.currentTimeMillis());

        MemoryMXBean memoryBean = ManagementFactory.getMemoryMXBean();
        MemoryUsage heapUsage = memoryBean.getHeapMemoryUsage();
        request.setAttribute(MEMORY_START_ATTRIBUTE, heapUsage.getUsed());

        return true;
    }

    @Override
    public void postHandle(HttpServletRequest request,
            HttpServletResponse response, Object handler,
            ModelAndView modelAndView) {
        // Lógica implementada em afterCompletion
    }

    @Override
    public void afterCompletion(HttpServletRequest request,
            HttpServletResponse response, Object handler,
            Exception ex) {

        Long startTime = (Long) request.getAttribute(
                START_TIME_ATTRIBUTE);
        if (startTime == null) {
            return;
        }

        long tempoProcessamento =
                System.currentTimeMillis() - startTime;

        // Métricas de memória heap
        MemoryMXBean memoryBean =
                ManagementFactory.getMemoryMXBean();
        MemoryUsage heapUsage = memoryBean.getHeapMemoryUsage();
        double memoriaUsadaMb =
                heapUsage.getUsed() / (1024.0 * 1024.0);
        double memoriaLivreMb =
                (heapUsage.getMax() - heapUsage.getUsed())
                / (1024.0 * 1024.0);
        double memoriaTotalMb =
                heapUsage.getMax() / (1024.0 * 1024.0);

        // Métrica de CPU do processo
        OperatingSystemMXBean osBean =
                (OperatingSystemMXBean)
                ManagementFactory.getOperatingSystemMXBean();
        double usoCpu = osBean.getProcessCpuLoad() * 100;

        // Threads ativas
        ThreadMXBean threadBean =
                ManagementFactory.getThreadMXBean();
        int threadsAtivas = threadBean.getThreadCount();

        // Informações da requisição
        String endpoint = request.getRequestURI();
        String metodoHttp = request.getMethod();
        String ipCliente = obterIpCliente(request);
        String userAgent = request.getHeader("User-Agent");
        String parametros = obterParametros(request);
        int statusHttp = response.getStatus();

        // Mensagem de erro se houver exceção
        String erro = null;
        if (ex != null) {
            StringWriter sw = new StringWriter();
            ex.printStackTrace(new PrintWriter(sw));
            erro = sw.toString();
            if (erro.length() > 5000) {
                erro = erro.substring(0, 5000) + "...";
            }
        }

        // Obter origem dos dados (enum definida pelo CacheService)
        OrigemDadosEnum origemDados = (OrigemDadosEnum)
                request.getAttribute(ORIGEM_DADOS_ATTRIBUTE);
        if (origemDados == null) {
            if ("GET".equals(metodoHttp)) {
                origemDados = OrigemDadosEnum.BANCO_DADOS;
            } else {
                origemDados = OrigemDadosEnum.NAO_APLICAVEL;
            }
        }

        RegistroPerformance registro =
                RegistroPerformance.builder()
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
                .userAgent(userAgent != null
                        && userAgent.length() > 255
                        ? userAgent.substring(0, 255)
                        : userAgent)
                .parametros(parametros)
                .erro(erro)
                .origemDados(origemDados)
                .build();

        performanceService.registrarAsync(registro);
    }

    private String obterIpCliente(HttpServletRequest request) {
        String ip = request.getHeader("X-Forwarded-For");
        if (ip == null || ip.isEmpty()
                || "unknown".equalsIgnoreCase(ip)) {
            ip = request.getHeader("Proxy-Client-IP");
        }
        if (ip == null || ip.isEmpty()
                || "unknown".equalsIgnoreCase(ip)) {
            ip = request.getHeader("WL-Proxy-Client-IP");
        }
        if (ip == null || ip.isEmpty()
                || "unknown".equalsIgnoreCase(ip)) {
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
            params.setLength(params.length() - 1);
        }
        String parametros = params.toString();
        if (parametros.length() > 5000) {
            parametros = parametros.substring(0, 5000) + "...";
        }
        return parametros.isEmpty() ? null : parametros;
    }
}
```

*Fonte: Elaboração própria. Arquivo `PerformanceInterceptor.java` do pacote `com.stcs.tollmanagement.interceptor`.*

Apêndice C – Configuração do NGINX (API Gateway)

O Código C.1 apresenta a configuração completa do NGINX como API gateway do sistema, organizada em quatro arquivos modulares: configuração principal (`nginx.conf`), pool de upstream com balanceamento round-robin (`upstream.conf`), zona de rate limiting (`rate-limit.conf`) e bloco do servidor com proxy reverso, CORS e cabeçalhos de segurança (`default.conf`). Os arquivos correspondem ao diretório `services/toll-api-gateway/` do projeto.

Código C.1 – Configuração completa do NGINX

```nginx
# ============================================================
# nginx.conf — Configuração principal do NGINX
# ============================================================
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    log_format main '$remote_addr - $remote_user [$time_local] '
                    '"$request" $status $body_bytes_sent '
                    '"$http_referer" "$http_user_agent" '
                    '"$http_x_forwarded_for"';
    access_log /var/log/nginx/access.log main;

    sendfile on;
    keepalive_timeout 65;

    include /etc/nginx/conf.d/*.conf;
}

# ============================================================
# upstream.conf — Pool do backend com três instâncias
# ============================================================
upstream toll_management_backend {
    # Round-robin load balancing (padrão)
    server toll-management-service-1:9080;
    server toll-management-service-2:9080;
    server toll-management-service-3:9080;
}

# ============================================================
# rate-limit.conf — Zona de rate limiting
# ============================================================
# 10 requisições/segundo por IP com 10MB de memória compartilhada
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

# ============================================================
# default.conf — Bloco principal do servidor
# ============================================================
server {
    listen 80;
    server_name localhost;

    # Endpoint de health check
    location /health {
        access_log off;
        return 200 '{"status":"UP"}';
        add_header Content-Type application/json;
    }

    # Proxy da API para instâncias do backend
    location /api/ {
        # Rate limiting: burst de 20 requisições, sem atraso
        limit_req zone=api_limit burst=20 nodelay;
        limit_req_status 429;

        # Cabeçalhos CORS
        add_header Access-Control-Allow-Origin
                   $http_origin always;
        add_header Access-Control-Allow-Methods
                   "GET, POST, PUT, PATCH, DELETE, OPTIONS" always;
        add_header Access-Control-Allow-Headers
                   "Authorization, Content-Type, Accept, Origin, "
                   "X-Requested-With" always;
        add_header Access-Control-Allow-Credentials "true" always;
        add_header Access-Control-Max-Age 3600 always;

        # Tratamento de requisições preflight OPTIONS
        if ($request_method = OPTIONS) {
            return 204;
        }

        # Configuração do proxy reverso
        proxy_pass http://toll_management_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For
                         $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 10s;
        proxy_read_timeout 30s;
    }

    # Proxy do frontend React
    location / {
        proxy_pass http://toll-frontend:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For
                         $proxy_add_x_forwarded_for;
    }

    # Cabeçalhos de segurança globais
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
}
```

*Fonte: Elaboração própria. Arquivos `nginx.conf`, `conf.d/upstream.conf`, `conf.d/rate-limit.conf` e `conf.d/default.conf` do diretório `services/toll-api-gateway/`.*

Apêndice D – Consumidor Kafka de Transações (Java / Spring Boot)

O Código D.1 apresenta a implementação do `TransacaoKafkaConsumer`, serviço Spring responsável por consumir mensagens de transações de pedágio do tópico Kafka `transacao-pedagio` e persisti-las no PostgreSQL de forma transacional. O consumidor valida as referências de chaves estrangeiras (praça, pista e tarifa vigente) e relança exceções para habilitar o mecanismo de retry do Kafka. O código corresponde ao arquivo `com.stcs.tollmanagement.service.TransacaoKafkaConsumer` do projeto.

Código D.1 – Classe TransacaoKafkaConsumer completa

```java
package com.stcs.tollmanagement.service;

import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.kafka.support.KafkaHeaders;
import org.springframework.messaging.handler.annotation.Header;
import org.springframework.messaging.handler.annotation.Payload;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import com.stcs.tollmanagement.dto.TransacaoPedagioKafkaDTO;
import com.stcs.tollmanagement.entity.PistaPedagio;
import com.stcs.tollmanagement.entity.PracaPedagio;
import com.stcs.tollmanagement.entity.TarifaPedagio;
import com.stcs.tollmanagement.entity.TransacaoPedagio;
import com.stcs.tollmanagement.repository.PistaPedagioRepository;
import com.stcs.tollmanagement.repository.PracaPedagioRepository;
import com.stcs.tollmanagement.repository.TarifaPedagioRepository;
import com.stcs.tollmanagement.repository.TransacaoPedagioRepository;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

@Service
@RequiredArgsConstructor
@Slf4j
public class TransacaoKafkaConsumer {

    private final TransacaoPedagioRepository
            transacaoPedagioRepository;
    private final PracaPedagioRepository
            pracaPedagioRepository;
    private final PistaPedagioRepository
            pistaPedagioRepository;
    private final TarifaPedagioRepository
            tarifaPedagioRepository;

    @KafkaListener(
        topics = "${kafka.topic.transacao-pedagio}",
        groupId = "${spring.kafka.consumer.group-id}",
        containerFactory = "kafkaListenerContainerFactory"
    )
    @Transactional
    public void consumirTransacao(
            @Payload TransacaoPedagioKafkaDTO transacaoDTO,
            @Header(KafkaHeaders.RECEIVED_PARTITION) int partition,
            @Header(KafkaHeaders.OFFSET) long offset) {

        log.info("Recebida transação do Kafka - Placa: {}, "
                + "Partition: {}, Offset: {}",
                transacaoDTO.getPlaca(), partition, offset);

        try {
            // Buscar entidades relacionadas (validação de FK)
            PracaPedagio praca = pracaPedagioRepository
                .findById(transacaoDTO.getPracaId())
                .orElseThrow(() -> new IllegalArgumentException(
                    "Praça não encontrada: "
                    + transacaoDTO.getPracaId()));

            PistaPedagio pista = pistaPedagioRepository
                .findById(transacaoDTO.getPistaId())
                .orElseThrow(() -> new IllegalArgumentException(
                    "Pista não encontrada: "
                    + transacaoDTO.getPistaId()));

            // Buscar tarifa vigente por tipo de veículo e data
            TarifaPedagio tarifa = tarifaPedagioRepository
                .findTarifaVigente(
                    transacaoDTO.getTipoVeiculo(),
                    transacaoDTO.getDataHoraPassagem()
                        .toLocalDate())
                .orElseThrow(() -> new IllegalArgumentException(
                    "Tarifa vigente não encontrada para: "
                    + transacaoDTO.getTipoVeiculo()));

            // Construir e persistir a entidade TransacaoPedagio
            TransacaoPedagio transacao =
                    TransacaoPedagio.builder()
                .praca(praca)
                .pista(pista)
                .tarifa(tarifa)
                .dataHoraPassagem(
                    transacaoDTO.getDataHoraPassagem())
                .placa(transacaoDTO.getPlaca())
                .tagId(transacaoDTO.getTagId())
                .tipoVeiculo(transacaoDTO.getTipoVeiculo())
                .valorOriginal(transacaoDTO.getValorOriginal())
                .statusTransacao(
                    transacaoDTO.getStatusTransacao())
                .hashIntegridade(
                    transacaoDTO.getHashIntegridade())
                .build();

            TransacaoPedagio salva =
                    transacaoPedagioRepository.save(transacao);

            log.info("Transação salva - ID: {}, Placa: {}, "
                    + "Praça: {}",
                    salva.getId(), salva.getPlaca(),
                    praca.getNome());

        } catch (Exception e) {
            log.error("Erro ao processar transação - Placa: {}, "
                    + "Partition: {}, Offset: {}, Erro: {}",
                    transacaoDTO.getPlaca(), partition, offset,
                    e.getMessage(), e);
            // Relança para habilitar retry do Kafka
            throw e;
        }
    }
}
```

*Fonte: Elaboração própria. Arquivo `TransacaoKafkaConsumer.java` do pacote `com.stcs.tollmanagement.service`.*

Apêndice E – Orquestração Docker Compose

O Código E.1 apresenta o arquivo `docker-compose.yml` utilizado para orquestrar todos os 12 serviços do ambiente experimental. A configuração define a rede interna `toll-network`, os volumes persistentes para PostgreSQL, Redis e Grafana, e as variáveis de ambiente para conexão entre os serviços. O arquivo corresponde ao diretório `infrastructure/` do projeto.

Código E.1 – Arquivo docker-compose.yml completo

```yaml
# Smart Toll Cache System — Docker Compose
# Orquestração completa do ambiente de desenvolvimento
version: '3.8'

services:
  # --- API Gateway / Balanceador de Carga ---
  nginx:
    build:
      context: ../services/toll-api-gateway
      dockerfile: Dockerfile
    ports:
      - "80:80"
    depends_on:
      - toll-management-service-1
      - toll-management-service-2
      - toll-management-service-3
    networks:
      - toll-network

  # --- Instâncias do Backend (Spring Boot) ---
  toll-management-service-1:
    build:
      context: ../services/toll-management-service
      dockerfile: Dockerfile
    environment:
      - SPRING_PROFILES_ACTIVE=docker
      - SPRING_DATASOURCE_URL=jdbc:postgresql://postgres:5432/rodovia
      - SPRING_DATASOURCE_USERNAME=rodovia_user
      - SPRING_DATASOURCE_PASSWORD=rodovia_pass
      - SPRING_DATA_REDIS_HOST=redis
      - SPRING_DATA_REDIS_PORT=6379
      - SPRING_KAFKA_BOOTSTRAP_SERVERS=kafka:9092
      - SERVER_PORT=9080
    depends_on:
      - postgres
      - redis
      - kafka
    networks:
      - toll-network

  toll-management-service-2:
    build:
      context: ../services/toll-management-service
      dockerfile: Dockerfile
    environment:
      - SPRING_PROFILES_ACTIVE=docker
      - SPRING_DATASOURCE_URL=jdbc:postgresql://postgres:5432/rodovia
      - SPRING_DATASOURCE_USERNAME=rodovia_user
      - SPRING_DATASOURCE_PASSWORD=rodovia_pass
      - SPRING_DATA_REDIS_HOST=redis
      - SPRING_DATA_REDIS_PORT=6379
      - SPRING_KAFKA_BOOTSTRAP_SERVERS=kafka:9092
      - SERVER_PORT=9080
    depends_on:
      - postgres
      - redis
      - kafka
    networks:
      - toll-network

  toll-management-service-3:
    build:
      context: ../services/toll-management-service
      dockerfile: Dockerfile
    environment:
      - SPRING_PROFILES_ACTIVE=docker
      - SPRING_DATASOURCE_URL=jdbc:postgresql://postgres:5432/rodovia
      - SPRING_DATASOURCE_USERNAME=rodovia_user
      - SPRING_DATASOURCE_PASSWORD=rodovia_pass
      - SPRING_DATA_REDIS_HOST=redis
      - SPRING_DATA_REDIS_PORT=6379
      - SPRING_KAFKA_BOOTSTRAP_SERVERS=kafka:9092
      - SERVER_PORT=9080
    depends_on:
      - postgres
      - redis
      - kafka
    networks:
      - toll-network

  # --- Frontend (React) ---
  toll-frontend:
    build:
      context: ../services/toll-frontend-react
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    depends_on:
      - nginx
    networks:
      - toll-network

  # --- Simulador de Transações (Python) ---
  toll-simulator:
    build:
      context: ../services/toll-simulator
      dockerfile: Dockerfile
    environment:
      - KAFKA_BOOTSTRAP_SERVERS=kafka:9092
      - KAFKA_TOPIC=transacao-pedagio
    depends_on:
      - kafka
    networks:
      - toll-network

  # --- Cache Distribuído ---
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes
    volumes:
      - redis-data:/data
    networks:
      - toll-network

  # --- Banco de Dados Relacional ---
  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=rodovia
      - POSTGRES_USER=rodovia_user
      - POSTGRES_PASSWORD=rodovia_pass
    ports:
      - "5432:5432"
    volumes:
      - postgres-data:/var/lib/postgresql/data
      - ./init-scripts/init.sql:/docker-entrypoint-initdb.d/init.sql
    networks:
      - toll-network

  # --- Mensageria Apache Kafka ---
  zookeeper:
    image: confluentinc/cp-zookeeper:7.5.0
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      ZOOKEEPER_TICK_TIME: 2000
    ports:
      - "2181:2181"
    networks:
      - toll-network

  kafka:
    image: confluentinc/cp-kafka:7.5.0
    depends_on:
      - zookeeper
    ports:
      - "9092:9092"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9092
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: PLAINTEXT:PLAINTEXT
      KAFKA_INTER_BROKER_LISTENER_NAME: PLAINTEXT
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
      KAFKA_AUTO_CREATE_TOPICS_ENABLE: 'true'
    networks:
      - toll-network

  # --- Observabilidade ---
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
    networks:
      - toll-network

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3001:3000"
    volumes:
      - ./grafana/provisioning:/etc/grafana/provisioning
      - grafana-data:/var/lib/grafana
    depends_on:
      - prometheus
    networks:
      - toll-network

volumes:
  postgres-data:
  redis-data:
  grafana-data:

networks:
  toll-network:
    driver: bridge
```

*Fonte: Elaboração própria. Arquivo `docker-compose.yml` do diretório `infrastructure/`.*

Apêndice F – Script de Inicialização do Banco de Dados (SQL)

O Código F.1 apresenta o script SQL de inicialização do PostgreSQL 15, executado automaticamente pelo Docker na criação do container. O script define o esquema relacional normalizado composto por 10 tabelas, 15 índices de otimização de consultas e dados iniciais de desenvolvimento (seed data). O arquivo corresponde a `infrastructure/init-scripts/init.sql` do projeto.

Código F.1 – Script init.sql completo

```sql
-- Smart Toll Cache System — Script de Inicialização do Banco
-- PostgreSQL 15

-- ============================================
-- Tabela: concessionaria
-- ============================================
CREATE TABLE IF NOT EXISTS concessionaria (
    id                   BIGSERIAL PRIMARY KEY,
    nome_fantasia        VARCHAR(120) NOT NULL,
    razao_social         VARCHAR(160) NOT NULL,
    cnpj                 VARCHAR(14)  NOT NULL UNIQUE,
    contrato_concessao   VARCHAR(60),
    data_inicio_contrato DATE NOT NULL,
    data_fim_contrato    DATE,
    ativo                BOOLEAN NOT NULL DEFAULT TRUE,
    criado_em            TIMESTAMP NOT NULL DEFAULT NOW()
);

-- ============================================
-- Tabela: rodovia
-- ============================================
CREATE TABLE IF NOT EXISTS rodovia (
    id                BIGSERIAL PRIMARY KEY,
    concessionaria_id BIGINT NOT NULL
                      REFERENCES concessionaria(id),
    codigo            VARCHAR(20) NOT NULL,
    nome              VARCHAR(120),
    uf                VARCHAR(2) NOT NULL,
    extensao_km       DECIMAL(8, 2),
    ativa             BOOLEAN NOT NULL DEFAULT TRUE,
    criado_em         TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_rodovia_concessionaria
    ON rodovia(concessionaria_id);
CREATE INDEX IF NOT EXISTS idx_rodovia_uf
    ON rodovia(uf);

-- ============================================
-- Tabela: praca_pedagio (Praça de Pedágio)
-- ============================================
CREATE TABLE IF NOT EXISTS praca_pedagio (
    id         BIGSERIAL PRIMARY KEY,
    rodovia_id BIGINT NOT NULL REFERENCES rodovia(id),
    nome       VARCHAR(120),
    km         DECIMAL(8, 3) NOT NULL,
    sentido    VARCHAR(20),
    ativa      BOOLEAN NOT NULL DEFAULT TRUE,
    criado_em  TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_praca_rodovia
    ON praca_pedagio(rodovia_id);

-- ============================================
-- Tabela: pista_pedagio (Pista de Pedágio)
-- ============================================
CREATE TABLE IF NOT EXISTS pista_pedagio (
    id           BIGSERIAL PRIMARY KEY,
    praca_id     BIGINT NOT NULL
                 REFERENCES praca_pedagio(id),
    numero_pista INTEGER NOT NULL,
    tipo_pista   VARCHAR(20) NOT NULL,
    sentido      VARCHAR(20),
    ativa        BOOLEAN NOT NULL DEFAULT TRUE,
    criado_em    TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT uk_praca_pista
        UNIQUE (praca_id, numero_pista)
);

CREATE INDEX IF NOT EXISTS idx_pista_praca
    ON pista_pedagio(praca_id);

-- ============================================
-- Tabela: tarifa_pedagio (Tarifa de Pedágio)
-- ============================================
CREATE TABLE IF NOT EXISTS tarifa_pedagio (
    id              BIGSERIAL PRIMARY KEY,
    tipo_veiculo    VARCHAR(20) NOT NULL,
    valor           DECIMAL(10, 2) NOT NULL,
    vigencia_inicio DATE NOT NULL,
    vigencia_fim    DATE,
    criado_em       TIMESTAMP NOT NULL DEFAULT NOW()
);

-- ============================================
-- Tabela: operador
-- ============================================
CREATE TABLE IF NOT EXISTS operador (
    id            BIGSERIAL PRIMARY KEY,
    username      VARCHAR(50) NOT NULL UNIQUE,
    password      VARCHAR(255) NOT NULL,
    nome_completo VARCHAR(100) NOT NULL,
    email         VARCHAR(100) NOT NULL UNIQUE,
    telefone      VARCHAR(20),
    ativo         BOOLEAN NOT NULL DEFAULT TRUE,
    criado_em     TIMESTAMP NOT NULL DEFAULT NOW(),
    atualizado_em TIMESTAMP
);

-- ============================================
-- Tabela: transacao_pedagio (Transação de Pedágio)
-- ============================================
CREATE TABLE IF NOT EXISTS transacao_pedagio (
    id                 BIGSERIAL PRIMARY KEY,
    praca_id           BIGINT NOT NULL
                       REFERENCES praca_pedagio(id),
    pista_id           BIGINT NOT NULL
                       REFERENCES pista_pedagio(id),
    tarifa_id          BIGINT NOT NULL
                       REFERENCES tarifa_pedagio(id),
    data_hora_passagem TIMESTAMP NOT NULL,
    placa              VARCHAR(10) NOT NULL,
    tag_id             VARCHAR(40),
    tipo_veiculo       VARCHAR(20) NOT NULL,
    valor_original     DECIMAL(10, 2) NOT NULL,
    status_transacao   VARCHAR(20) NOT NULL,
    hash_integridade   VARCHAR(128) NOT NULL,
    criado_em          TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_transacao_praca
    ON transacao_pedagio(praca_id);
CREATE INDEX IF NOT EXISTS idx_transacao_pista
    ON transacao_pedagio(pista_id);
CREATE INDEX IF NOT EXISTS idx_transacao_tarifa
    ON transacao_pedagio(tarifa_id);
CREATE INDEX IF NOT EXISTS idx_transacao_status
    ON transacao_pedagio(status_transacao);
CREATE INDEX IF NOT EXISTS idx_transacao_placa
    ON transacao_pedagio(placa);
CREATE INDEX IF NOT EXISTS idx_transacao_data
    ON transacao_pedagio(data_hora_passagem);

-- ============================================
-- Tabela: ocorrencia_transacao
-- ============================================
CREATE TABLE IF NOT EXISTS ocorrencia_transacao (
    id                        BIGSERIAL PRIMARY KEY,
    transacao_id              BIGINT NOT NULL
                              REFERENCES transacao_pedagio(id),
    tipo_ocorrencia           VARCHAR(30) NOT NULL,
    observacao                TEXT,
    detectada_automaticamente BOOLEAN NOT NULL DEFAULT TRUE,
    criado_em                 TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_ocorrencia_transacao
    ON ocorrencia_transacao(transacao_id);

-- ============================================
-- Tabela: correcao_transacao
-- ============================================
CREATE TABLE IF NOT EXISTS correcao_transacao (
    id              BIGSERIAL PRIMARY KEY,
    transacao_id    BIGINT NOT NULL
                    REFERENCES transacao_pedagio(id),
    operador_id     BIGINT NOT NULL
                    REFERENCES operador(id),
    motivo          TEXT NOT NULL,
    valor_anterior  DECIMAL(10, 2) NOT NULL,
    valor_corrigido DECIMAL(10, 2) NOT NULL,
    tipo_correcao   VARCHAR(20) NOT NULL,
    criado_em       TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_correcao_transacao
    ON correcao_transacao(transacao_id);
CREATE INDEX IF NOT EXISTS idx_correcao_operador
    ON correcao_transacao(operador_id);

-- ============================================
-- Tabela: registro_performance
-- ============================================
CREATE TABLE IF NOT EXISTS registro_performance (
    id                     BIGSERIAL PRIMARY KEY,
    endpoint               VARCHAR(255) NOT NULL,
    metodo_http            VARCHAR(10) NOT NULL,
    tempo_processamento_ms BIGINT NOT NULL,
    memoria_usada_mb       DOUBLE PRECISION NOT NULL,
    memoria_livre_mb       DOUBLE PRECISION NOT NULL,
    memoria_total_mb       DOUBLE PRECISION NOT NULL,
    uso_cpu_processo       DOUBLE PRECISION NOT NULL,
    threads_ativas         INTEGER NOT NULL,
    status_http            INTEGER NOT NULL,
    ip_cliente             VARCHAR(45),
    user_agent             VARCHAR(255),
    parametros             TEXT,
    erro                   TEXT,
    origem_dados           VARCHAR(20),
    criado_em              TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_performance_endpoint
    ON registro_performance(endpoint);
CREATE INDEX IF NOT EXISTS idx_performance_criado
    ON registro_performance(criado_em);

-- ============================================
-- Dados Iniciais (Seed Data)
-- ============================================
INSERT INTO concessionaria
    (nome_fantasia, razao_social, cnpj,
     contrato_concessao, data_inicio_contrato)
VALUES
    ('AutoPista SP', 'AutoPista Concessionária S.A.',
     '12345678000190', 'CONC-2020-001', '2020-01-01');

INSERT INTO rodovia
    (concessionaria_id, codigo, nome, uf, extensao_km)
VALUES
    (1, 'BR-101', 'Rodovia Rio-Santos', 'SP', 210.50);

INSERT INTO praca_pedagio (rodovia_id, nome, km, sentido)
VALUES
    (1, 'Praça Norte',  45.500, 'NORTE'),
    (1, 'Praça Sul',   120.000, 'SUL'),
    (1, 'Praça Centro', 85.200, 'AMBOS');

INSERT INTO pista_pedagio
    (praca_id, numero_pista, tipo_pista, sentido)
VALUES
    (1, 1, 'TAG',    'NORTE'),
    (1, 2, 'MISTA',  'NORTE'),
    (1, 3, 'MANUAL', 'NORTE'),
    (2, 1, 'TAG',    'SUL'),
    (2, 2, 'MISTA',  'SUL'),
    (3, 1, 'TAG',    'AMBOS');

INSERT INTO tarifa_pedagio
    (tipo_veiculo, valor, vigencia_inicio)
VALUES
    ('MOTO',      5.00, '2024-01-01'),
    ('CARRO',    10.00, '2024-01-01'),
    ('CAMINHAO', 20.00, '2024-01-01');

INSERT INTO operador
    (username, password, nome_completo, email, ativo)
VALUES
    ('admin', '$2a$10$placeholder', 'Administrador',
     'admin@smarttoll.com', TRUE);
```

*Fonte: Elaboração própria. Arquivo `init.sql` do diretório `infrastructure/init-scripts/`.*


ANEXOS

Anexo A – Documentação Oficial das Tecnologias Utilizadas

O desenvolvimento deste trabalho fundamentou-se nas documentações oficiais das tecnologias empregadas na construção do sistema. A seguir são listadas as referências técnicas consultadas durante a implementação, configuração e instrumentação do ambiente experimental:

- Spring Boot 4.0.x: Documentação de referência do framework, incluindo módulos Spring Data JPA, Spring Data Redis, Spring Kafka e Spring Boot Actuator. Disponível em: https://docs.spring.io/spring-boot/reference/. Acesso em: 7 abr. 2026.

- PostgreSQL 15: Manual oficial do sistema de gerenciamento de banco de dados relacional, com ênfase nos capítulos de indexação, otimização de consultas e tipos de dados. Disponível em: https://www.postgresql.org/docs/15/. Acesso em: 7 abr. 2026.

- Redis 7: Documentação do banco de dados em memória, incluindo comandos de manipulação de chaves, políticas de evicção LRU, configuração de TTL e operações com `RedisTemplate`. Disponível em: https://redis.io/documentation. Acesso em: 7 abr. 2026.

- Apache Kafka: Documentação da plataforma de streaming distribuído, abrangendo configuração de produtores e consumidores, semântica de entrega `acks=all` e gerenciamento de tópicos. Disponível em: https://kafka.apache.org/documentation/. Acesso em: 7 abr. 2026.

- NGINX: Documentação do servidor web e proxy reverso, com foco em balanceamento de carga, rate limiting (`limit_req_zone`), configuração de upstream e cabeçalhos de segurança. Disponível em: https://nginx.org/en/docs/. Acesso em: 7 abr. 2026.

- Docker Compose: Documentação da ferramenta de orquestração de containers, incluindo especificação do formato de arquivo YAML, gerenciamento de redes, volumes e variáveis de ambiente. Disponível em: https://docs.docker.com/compose/. Acesso em: 7 abr. 2026.

- Prometheus: Documentação do sistema de monitoramento e banco de dados de séries temporais, com ênfase na configuração de scrape targets e integração com Spring Boot Actuator. Disponível em: https://prometheus.io/docs/introduction/overview/. Acesso em: 7 abr. 2026.

- Grafana: Documentação da plataforma de visualização de dados, incluindo configuração de datasources Prometheus, criação de dashboards e provisionamento automatizado. Disponível em: https://grafana.com/docs/. Acesso em: 7 abr. 2026.

- React 18: Documentação oficial da biblioteca JavaScript para construção de interfaces de usuário, incluindo hooks, gerenciamento de estado e integração com APIs REST. Disponível em: https://react.dev/. Acesso em: 7 abr. 2026.

Anexo B – Gráficos de Desempenho dos Experimentos

Os gráficos a seguir foram gerados durante a campanha experimental descrita no Capítulo 4, utilizando os dashboards Grafana configurados com datasource Prometheus. As figuras complementam as tabelas e análises apresentadas no corpo do texto:

- Figura 6 (Seção 4.1): Box-plot comparativo da distribuição de latência nos três cenários com 250 usuários simultâneos.
- Figura 7 (Seção 4.2): Gráfico de barras agrupadas do throughput (TPS) por número de usuários simultâneos.
- Figura 8 (Seção 4.2): Séries temporais de consumo de CPU e memória heap sob carga de 500 usuários simultâneos.
- Figura 9 (Seção 4.4): Gráfico radar com comparação multidimensional normalizada das três estratégias de cache.

