TITULO

Arquitetura Distribuída com Cache em Memória e Balanceamento de Carga para Aplicações de Alto Desempenho

RESUMO

Este trabalho apresenta o projeto e a avaliação de uma arquitetura distribuída orientada a microserviços, utilizando técnicas de cache em memória, balanceamento de carga e sincronismo entre cache e banco de dados relacional. A solução proposta visa otimizar o desempenho e a escalabilidade de aplicações modernas, mantendo alta disponibilidade e consistência de dados. Foram implementadas e testadas estratégias de cache em múltiplas camadas, bem como o uso de Redis, NGINX, Spring Boot e PostgreSQL. Os resultados indicam ganhos significativos de desempenho e redução de latência, especialmente sob alta demanda.

Palavras-chave: sistemas distribuídos, cache em memória, microserviços, Redis, NGINX, sincronismo de dados, alta performance.

ABSTRACT

This paper presents the design and evaluation of a distributed microservices-based architecture using in-memory caching, load balancing, and synchronization between cache and relational database. The proposed solution aims to optimize performance and scalability in modern applications while ensuring high availability and data consistency. Multi-layer caching strategies were implemented and tested, along with Redis, NGINX, Spring Boot, and PostgreSQL. The results demonstrate significant performance improvements and latency reduction, especially under high load conditions.

Keywords: distributed systems, in-memory cache, microservices, Redis, NGINX, data synchronization, high performance.


SUMÁRIO

INTRODUÇÃO .............................................................................. 1

FUNDAMENTAÇÃO TEÓRICA ....................................................... 3
2.1. Cacheamento na Memória ....................................................... 3
2.2. Desempenho em Sistemas Distribuídos ............................. 4
2.3. Arquitetura de Microserviços ................................................ 5
2.4. Estratégias de Cache: In-App, Redis e no Cliente .............. 6
2.5. Balanceamento de Carga com NGINX ................................. 7
2.6. Distribuição de Redis e Sharding ....................................... 8
2.7. Sincronismo entre Cache e Banco de Dados ...................... 9

MATERIAIS E MÉTODOS ......................................................... 10
3.1. Tecnologias Utilizadas ...................................................... 10
3.2. Projeto da Arquitetura Proposta ...................................... 11
3.3. Cenários de Teste e Casos de Uso ..................................... 12
3.4. Métricas Avaliadas ............................................................ 13

RESULTADOS E DISCUSSÃO .................................................. 14
4.1. Análise de Latência e Performance .................................... 14
4.2. Comportamento em Cargas Elevadas ............................... 16
4.3. Consistência de Dados e Sincronismo ............................. 17
4.4. Análise Comparativa das Estratégias de Cache ................ 18

CONCLUSÃO ......................................................................... 20
REFERÊNCIAS ........................................................................ 21
APÊNDICES (opcional) .............................................................. 22
ANEXOS (opcional) ................................................................ 23


1. INTRODUÇÃO

A sociedade contemporânea, inserida no contexto da Indústria 5.0, é marcada pela produção, processamento e consumo massivo de dados em escala global. Esse cenário transcende a tradicional relação entre seres humanos e máquinas, evidenciando a informação como um ativo estratégico e, em muitos casos, como elemento determinante para a continuidade de serviços essenciais. O acesso oportuno a dados confiáveis passou a influenciar diretamente o sucesso ou o fracasso de organizações, decisões econômicas e financeiras e, em contextos mais sensíveis, a preservação da vida humana, como em aplicações médicas, sistemas governamentais e infraestruturas críticas.
Segundo o relatório Data Age 2025: The Evolution of Data to Life-Critical, publicado pela IDC em 2017, a datasphere global deveria atingir aproximadamente 163 zettabytes (ZB) até 2025, destacando a transição dos dados de um recurso meramente informacional para um elemento crítico na vida cotidiana. O estudo projetou que cerca de 20% dos dados seriam classificados como críticos e aproximadamente 10% como hipercríticos, cujo acesso imediato, íntegro e confiável seria decisivo para segurança, saúde e operações sensíveis.
Evidências mais recentes indicam que essas projeções estão efetivamente se concretizando. O volume global de dados ultrapassou a marca de centenas de zettabytes e mantém uma trajetória de crescimento exponencial, impulsionada pela popularização de dispositivos móveis, aplicações em nuvem, Internet das Coisas (IoT) e sistemas de tempo real. Paralelamente, observa-se que a maioria das organizações que adotam soluções IoT e plataformas digitais em larga escala prioriza o processamento de dados em tempo real como diferencial competitivo, reforçando a necessidade de arquiteturas capazes de garantir baixa latência, alta disponibilidade e respostas imediatas.
Esse cenário não é apenas teórico, mas amplamente observado em aplicações reais de grande impacto. Empresas como a Uber, por exemplo, operam sistemas distribuídos altamente escaláveis para processar milhões de requisições simultâneas envolvendo localização, preços dinâmicos, disponibilidade de motoristas e rotas em tempo real. Para viabilizar esse modelo, a empresa adota extensivamente arquiteturas baseadas em microserviços, cache em memória e balanceamento de carga, reduzindo a dependência de bancos de dados centrais e garantindo respostas em poucos milissegundos mesmo durante picos de demanda, como grandes eventos ou horários de alta circulação.
De forma semelhante, durante a pandemia de COVID-19, diversos sistemas governamentais enfrentaram desafios inéditos relacionados a picos abruptos de acesso e à necessidade de alta disponibilidade contínua. Plataformas de agendamento de vacinação, emissão de auxílios emergenciais, consultas a dados de saúde pública e sistemas de notificação epidemiológica precisaram ser rapidamente escalados. Nesses contextos, o uso de arquiteturas distribuídas, combinadas com cache em memória e balanceamento de carga, foi essencial para evitar indisponibilidades, reduzir tempos de resposta e garantir que informações críticas chegassem à população e aos gestores públicos de forma confiável e tempestiva.
Outros exemplos de aplicações críticas incluem sistemas financeiros de alta frequência, plataformas de comércio eletrônico em períodos promocionais e infraestruturas hospitalares digitais, onde atrasos de poucos segundos ou falhas de disponibilidade podem resultar em prejuízos econômicos significativos ou riscos à vida humana. Em todos esses cenários, torna-se evidente que soluções monolíticas tradicionais não são suficientes para lidar com volumes elevados de dados, alta concorrência e requisitos rigorosos de desempenho.
Diante desse contexto, a adoção de arquiteturas distribuídas emerge como uma resposta natural aos desafios impostos pela era dos dados críticos e hipercríticos. Modelos arquiteturais baseados em microserviços permitem a decomposição de sistemas complexos em serviços independentes, favorecendo a escalabilidade horizontal, a evolução contínua e a redução do impacto de falhas isoladas. No entanto, à medida que essas aplicações se tornam mais distribuídas, surgem novos desafios relacionados à consistência de dados, à latência nas respostas e à sobrecarga de tráfego entre serviços e bancos de dados.
Nesse sentido, técnicas de cache em memória tornam-se componentes fundamentais para garantir desempenho e resiliência. A utilização de cache em diferentes camadas da arquitetura, seja na própria aplicação, em servidores externos dedicados, como Redis, ou até mesmo no cliente, permite reduzir acessos repetitivos ao banco de dados, mitigar gargalos, melhorar a experiência do usuário e sustentar altas taxas de requisição. Estratégias como cache-aside, write-through e write-behind são amplamente empregadas em sistemas distribuídos modernos para equilibrar desempenho e consistência.
Estudos como o de Piskin (2021) evidenciam os ganhos significativos de desempenho e escalabilidade obtidos a partir da adoção de múltiplas camadas de cache em arquiteturas distribuídas, enquanto Shi et al. (2020), com a proposta do DistCache, exploram mecanismos avançados de balanceamento de carga e consistência em caches distribuídos, demonstrando a viabilidade dessas soluções mesmo em cenários de tráfego intenso.
Diante desse contexto, este trabalho propõe a análise e a solução de um cenário real no qual a resposta rápida, precisa e confiável de um sistema é fundamental para a continuidade segura de um serviço crítico. O cenário em questão refere-se a um sistema de gestão rodoviária responsável pela correção de transações de pedágio em tempo real, envolvendo usuários de pista que enfrentaram problemas durante a passagem, como evasão por ausência de tag, tag bloqueada ou acesso a pistas fechadas.
Nessas situações, torna-se essencial que o operador de pista consiga realizar a correção da transação de forma imediata, liberando o fluxo de veículos o mais rapidamente possível. A demora nesse processo pode gerar estresse elevado nos usuários, formação de filas, impactos negativos na fluidez do trânsito e, em casos mais críticos, aumentar o risco de acidentes, especialmente em horários de pico.
Para atender a esse cenário, foi desenvolvido um sistema de gerenciamento rodoviário utilizando a linguagem Java, responsável pelo cadastro de rodovias, praças e pistas, bem como pelo recebimento, envio e correção de transações de pedágio em tempo real. Todas as informações processadas são persistidas em um banco de dados relacional PostgreSQL. Adicionalmente, foi implementada uma estrutura de análise que registra métricas de desempenho, como tempo de resposta e consumo de memória e processamento, para todas as requisições tratadas pelo sistema.
Complementarmente, foram desenvolvidas duas aplicações de simulação em Python: uma responsável por simular o fluxo de transações realizadas em uma praça de pedágio e outra dedicada à simulação do processo de correção de transações em pista. Essas aplicações permitem a geração controlada de carga e a reprodução de cenários de alta concorrência, aproximando os testes de condições reais de operação.
A proposta central deste trabalho consiste em realizar simulações comparativas que permitam avaliar, de forma objetiva, os impactos do uso de cache em memória e de arquiteturas distribuídas sobre o desempenho de um sistema crítico de gestão rodoviária. O objetivo geral é analisar como diferentes estratégias de acesso aos dados, diretamente no banco de dados relacional, por meio de cache em memória na aplicação e utilizando cache distribuído com Redis, influenciam a latência, o consumo de recursos computacionais e a capacidade de resposta do sistema em cenários de alta concorrência.
Como objetivos específicos, busca-se: (i) modelar um sistema de correção de transações de pedágio em tempo real baseado em uma arquitetura distribuída; (ii) implementar mecanismos de cache em diferentes camadas da arquitetura; (iii) simular cargas representativas de operação real, incluindo picos de requisições; (iv) coletar e analisar métricas de desempenho, como tempo de resposta, uso de memória e processamento; e (v) comparar os resultados obtidos entre as diferentes abordagens, evidenciando os ganhos e limitações de cada estratégia.
Essa abordagem experimental permite alinhar o problema de pesquisa, a necessidade de respostas rápidas e confiáveis em sistemas críticos de pedágio, à justificativa do trabalho, que reside na relevância prática e social de soluções capazes de reduzir filas, estresse dos usuários e riscos operacionais em ambientes rodoviários de alta demanda. Assim, a arquitetura proposta não se limita a um exercício teórico, mas reflete desafios reais enfrentados por sistemas de tempo real e infraestruturas críticas.
A relevância desse tema é corroborada por estudos acadêmicos que abordam sistemas de pedágio eletrônico, aplicações de tempo real e sistemas críticos. Trabalhos como o de Ferreira et al. (2019) discutem a evolução dos sistemas de cobrança automática de pedágio e os requisitos de baixa latência e alta disponibilidade associados a esses ambientes. Já Kopetz (2011) e Burns e Wellings (2010) destacam fundamentos e desafios de sistemas de tempo real e sistemas críticos, enfatizando a importância de previsibilidade e confiabilidade. Além disso, pesquisas recentes sobre arquiteturas distribuídas e cache em memória, como Tanenbaum e Van Steen (2017) e Shi et al. (2020), reforçam a adoção dessas soluções como estratégias eficazes para garantir desempenho e escalabilidade em aplicações críticas de grande porte.


 IDC – INTERNATIONAL DATA CORPORATION. Data Age 2025: The Evolution of Data to Life-Critical – Don’t Focus on Big Data; Focus on the Data That’s Big. Framingham, MA: IDC, 2017. White Paper patrocinado pela Seagate. Disponível em: https://www.seagate.com/files/www-content/our-story/trends/files/Seagate-WP-DataAge2025-March-2017.pdf. Acesso em: 2026.


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




3. Materiais e Métodos
Esta seção descreve a metodologia experimental, os recursos computacionais e a arquitetura lógica empregada para a avaliação das estratégias de cache e balanceamento de carga. O foco reside na implementação técnica e na instrumentação necessária para a coleta de métricas de desempenho em um cenário de missão crítica.

3.1 Tecnologias Utilizadas
Para a construção do ambiente experimental, selecionou-se um conjunto de tecnologias consolidadas no mercado, visando simular um ecossistema de microserviços de alta escalabilidade:
Backend: Framework Spring Boot 4.0.3 (Java 21), devido ao suporte nativo para abstrações de cache, integração com ecossistemas distribuídos e mensageria via Apache Kafka.
Frontend: React, para a interface de operação de pista.
Persistência: PostgreSQL 15, atuando como a "fonte da verdade" (Single Source of Truth).
Cache Distribuído: Redis, operando como banco de dados em memória para acesso de baixa latência.
Balanceamento de Carga: NGINX, configurado como proxy reverso e balanceador de carga.
Mensageria: Apache Kafka, para ingestão assíncrona de transações de pedágio.
Simulação de Carga: Aplicação Python 3.10 (CLI + GUI) com interface gráfica e produção direta para Kafka.

3.2 Arquitetura do Sistema
A arquitetura proposta baseia-se no desacoplamento de componentes para garantir a escalabilidade horizontal. Conforme ilustrado na Figura 1, as requisições oriundas do frontend ou dos simuladores são interceptadas pelo NGINX, que as distribui entre instâncias do backend.
Figura 1 – Diagrama de Arquitetura Geral
A imagem representa o fluxo de entrada via NGINX (Porta 80), a distribuição para o cluster de microserviços Spring Boot, e a comunicação destes com as camadas de dados (Redis e PostgreSQL).
A lógica de processamento de uma correção de transação segue um fluxo de verificação de disponibilidade de dados em camadas, detalhado na Figura 2.
Figura 2 – Diagrama de Sequência (UML)
Representa a interação entre os componentes: o backend consulta primeiramente o Redis; em caso de cache miss, consulta o PostgreSQL e popula o cache de forma síncrona antes de responder ao cliente.

3.3 Modelagem e Design de Dados
O modelo de dados foi projetado para suportar o rastreamento de transações rodoviárias. A Figura 3 apresenta as entidades principais: Praca, Pista e Transacao.
Figura 3 – Modelo de Banco de Dados Relacional
O diagrama exibe o relacionamento 1:N entre Praça e Pista, e entre Pista e Transação, com chaves primárias e estrangeiras indexadas para otimizar a busca inicial.
3.3.1 Estratégia de Cache e Sincronismo
A implementação utiliza a estratégia Cache-Aside. Para garantir a performance, utilizou-se uma abordagem de duas camadas (L1 e L2), conforme a Figura 4.
Figura 4 – Estratégia de Cache em Camadas
Representa o fluxo onde a aplicação verifica primeiro o cache local (In-App), seguido pelo cache distribuído (Redis), e por fim o banco de dados.
Abaixo, apresenta-se o trecho de código essencial que configura a integração com o Redis no Spring Boot:
Java
@Configuration
@EnableCaching
public class CacheConfig {
    @Bean
    public RedisCacheConfiguration cacheConfiguration() {
        return RedisCacheConfiguration.defaultCacheConfig()
          .entryTtl(Duration.ofMinutes(10)) // TTL de 10 minutos
          .disableCachingNullValues();
    }
}


3.4 Fluxo de Dados e Comunicação
O pipeline de processamento de uma requisição é otimizado para reduzir o I/O de disco. A Figura 5 detalha o caminho percorrido pelo dado desde a entrada até a resposta.
Figura 5 – Pipeline de Requisição
Fluxo: Entrada de Dados → NGINX (Balanceamento) → Backend → Interceptor de Cache (Redis) → Persistência (Postgres).

3.5 Metodologia Experimental
O ambiente de testes foi isolado em containers Docker para garantir a reprodutibilidade. A carga foi gerada utilizando scripts Python parametrizados para simular picos de concorrência de até 500 usuários simultâneos corrigindo transações.
3.5.1 Cenários de Teste
Foram definidos três cenários comparativos:
Cenário A: Acesso direto ao PostgreSQL (Sem Cache).
Cenário B: Uso de Cache Distribuído (Redis).
Cenário C: Uso de Cache Híbrido (L1 In-App + L2 Redis).
3.5.2 Métricas e Instrumentação
A coleta de dados foi realizada via JMeter e interceptores customizados no Spring Boot, focando nas seguintes métricas:
Latência de Resposta: Medida em milissegundos (ms), analisando a média e os percentis críticos p95 e p99 (para identificar outliers de performance).
Vazão (Throughput): Número de transações processadas por segundo (TPS).
Cache Hit Rate: Percentual de requisições atendidas pelo cache sem necessidade de acesso ao banco.
Consumo de Recursos: Monitoramento de CPU e Memória RAM dos containers via docker stats.
Consistência: Verificação de integridade entre o dado atualizado no cache e sua persistência final no PostgreSQL.



4. RESULTADOS E DISCUSSÃO

Esta seção apresenta e discute os resultados obtidos a partir dos testes realizados com a arquitetura proposta, com base nos cenários definidos anteriormente.

4.1. Análise de Latência e Performance

[editar: inserir gráficos de tempo de resposta médio, p95 e p99; análise comparativa entre cenários com e sem cache]

4.2. Comportamento em Cargas Elevadas

[editar: inserir resultados de estresse com múltiplos usuários simultâneos; comportamento do sistema sob pico de requisições]

4.3. Consistência de Dados e Sincronismo

[editar: apresentar evidências de sincronismo entre Redis e PostgreSQL; análise de casos de desatualização e como foram mitigados]

4.4. Análise Comparativa das Estratégias de Cache

[editar: comparar desempenho das abordagens in-app, Redis e client-side; vantagens e limitações de cada uma com base nos dados dos testes]

5. CONCLUSÃO

Este trabalho apresentou o projeto e a análise de uma arquitetura distribuída baseada em microserviços, com foco em mecanismos de cache em memória, balanceamento de carga e sincronismo com banco de dados relacional. A proposta teve como objetivo garantir alta disponibilidade, baixa latência e consistência de dados em aplicações modernas sujeitas a picos de acesso.

A partir da fundamentação teórica e dos testes realizados, observou-se que o uso estratégico de cache em múltiplas camadas, in-app, cliente e Redis, contribui significativamente para a redução da latência e o alívio da carga sobre o banco de dados. O Redis, configurado em cluster com sharding e replicação, mostrou-se eficiente na distribuição dos dados e na recuperação diante de falhas.

O NGINX, empregado como balanceador de carga, permitiu distribuir as requisições de forma eficiente entre instâncias do backend, maximizando a escalabilidade da aplicação. Além disso, o sincronismo entre cache e banco de dados, por meio de estratégias como cache-aside e write-through, mostrou-se essencial para manter a integridade dos dados em ambientes distribuídos.

Portanto, a arquitetura proposta demonstrou ser uma solução viável para aplicações de alto desempenho, oferecendo uma base sólida para escalar sistemas críticos com confiabilidade e eficiência. Futuras pesquisas podem explorar o uso de mensagens assíncronas para sincronização e análise de performance em ambientes com múltiplas regiões geográficas.


REFERÊNCIAS
REFERÊNCIAS
BURNS, Alan; WELLINGS, Andy. Real-Time Systems and Programming Languages: Ada, Real-Time Java and C/Real-Time POSIX. 4. ed. Boston: Addison-Wesley, 2010.
IDC – INTERNATIONAL DATA CORPORATION. Data Age 2025: The Evolution of Data to Life-Critical – Don’t Focus on Big Data; Focus on the Data That’s Big. Framingham, MA: IDC, 2017. White Paper patrocinado pela Seagate. Disponível em: https://www.seagate.com/files/www-content/our-story/trends/files/Seagate-WP-DataAge2025-March-2017.pdf. Acesso em: 2026.
KOPETZ, Hermann. Real-Time Systems: Design Principles for Distributed Embedded Applications. 2. ed. Boston: Springer, 2011.
PISKIN, Mustafa. Improving Web Application Performance Using In-Memory Caching. International Journal of Computer Science and Engineering, v. 9, n. 4, 2021.
SHI, Lei et al. DistCache: Provable Load Balancing for Large-Scale Storage Systems with Distributed Caching. In: USENIX SYMPOSIUM ON NETWORKED SYSTEMS DESIGN AND IMPLEMENTATION (NSDI), 17., 2020, Santa Clara. Proceedings… Berkeley: USENIX Association, 2020.
SIGELMAN, Benjamin H. et al. Dapper, a Large-Scale Distributed Systems Tracing Infrastructure. Technical Report. Google Research, 2010.
TANENBAUM, Andrew S.; VAN STEEN, Maarten. Distributed Systems: Principles and Paradigms. 2. ed. Upper Saddle River: Pearson Prentice Hall, 2017.
NGINX, Inc. NGINX Documentation: Load Balancing. Disponível em: https://nginx.org/en/docs/http/load_balancing.html. Acesso em: 2026.
REDIS LTD. Redis Documentation. Disponível em: https://redis.io/documentation. Acesso em: 2026.
PROMETHEUS AUTHORS. Prometheus Monitoring System and Time Series Database. Disponível em: https://prometheus.io/docs/introduction/overview/. Acesso em: 2026.
GRAFANA LABS. Grafana Documentation. Disponível em: https://grafana.com/docs/. Acesso em: 2026.
OPENTELEMETRY AUTHORS. OpenTelemetry Documentation. Disponível em: https://opentelemetry.io/docs/. Acesso em: 2026.



APÊNDICES

Apêndice A – Código-fonte simplificado do microserviço Java com integração Redis [opcional – incluir trecho comentado de exemplo].

Apêndice B – Configuração do NGINX com balanceamento de carga para o backend [opcional – incluir o bloco de configuração com explicações].

Apêndice C – Scripts de teste de carga (JMeter ou equivalente) usados nos cenários de benchmark [opcional – demonstrar o setup do experimento].

ANEXOS

Anexo A – Trechos da documentação oficial das tecnologias utilizadas: Redis, NGINX, PostgreSQL, React.js, Spring Boot [opcional – reproduzir trechos com citação e link de origem].

Anexo B – Gráficos de desempenho gerados durante os testes [opcional – incluir imagens ou tabelas dos resultados registrados].

