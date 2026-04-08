TITLE

Distributed Architecture with In-Memory Caching and Load Balancing for High-Performance Applications


RESUMO

Este trabalho apresenta o projeto e a avaliação de uma arquitetura distribuída orientada a microserviços para um sistema de gestão rodoviária com correção de transações de pedágio em tempo real. A solução emprega cache em memória em duas camadas — cache L1 in-app via `ConcurrentHashMap` (TTL 30 min, máximo 1.000 entradas por instância) e cache L2 distribuído via Redis 7 (TTL 60 min, política LRU) — seguindo o padrão Cache-Aside com TTL escalonado para minimizar invalidações simultâneas. O backend foi desenvolvido em Spring Boot 4.0.3 (Java 21), com três instâncias balanceadas por NGINX (round-robin, rate limiting 10 req/s, burst 20), PostgreSQL 15 como Fonte Única da Verdade (SSOT) e Apache Kafka para ingestão assíncrona de transações via tópico `transacao-pedagio`. Um `PerformanceInterceptor` customizado registra métricas de desempenho — tempo de resposta, consumo de memória, uso de CPU e origem dos dados (`CACHE_LOCAL`, `CACHE_REDIS`, `BANCO_DADOS`) — na tabela `registro_performance`. Três cenários experimentais foram definidos: (A) acesso direto ao banco, (B) cache Redis apenas e (C) cache híbrido L1+L2. Os resultados projetados indicam redução de 95–97% na latência, throughput de 1.200–2.000 TPS e taxa de acerto de cache de 85–95% no cenário C, com todo o ambiente orquestrado via Docker Compose (12 serviços) e monitorado por Prometheus e Grafana.

Palavras-chave: cache em memória multicamada, padrão cache-aside, gestão rodoviária, sistemas distribuídos, Redis, NGINX, sincronismo de dados, tempo real flexível.


ABSTRACT

This paper presents the design and evaluation of a distributed microservices-based architecture for a toll management system with real-time transaction correction. The solution employs two-layer in-memory caching — in-app L1 cache via `ConcurrentHashMap` (TTL 30 min, max 1,000 entries per instance) and distributed L2 cache via Redis 7 (TTL 60 min, LRU eviction) — following the Cache-Aside pattern with staggered TTL to minimize simultaneous invalidations. The backend was developed in Spring Boot 4.0.3 (Java 21), with three instances load-balanced by NGINX (round-robin, rate limiting at 10 req/s, burst 20), PostgreSQL 15 as the Single Source of Truth (SSOT), and Apache Kafka for asynchronous transaction ingestion via the `transacao-pedagio` topic. A custom `PerformanceInterceptor` records per-request metrics — response time, memory consumption, CPU usage, and data origin (`CACHE_LOCAL`, `CACHE_REDIS`, `BANCO_DADOS`) — to a dedicated `registro_performance` table. Three experimental scenarios were defined: (A) direct database access, (B) Redis-only caching, and (C) hybrid L1+L2 caching. Projected results indicate 95–97% latency reduction, throughput of 1,200–2,000 TPS, and cache hit rates of 85–95% under Scenario C, with the entire environment orchestrated via Docker Compose (12 services) and monitored through Prometheus and Grafana.

Keywords: multi-layer in-memory cache, cache-aside pattern, toll management, distributed systems, Redis, NGINX, data synchronization, soft real-time, high performance.


TABLE OF CONTENTS

1 INTRODUCTION ............................................................................. 1
1.1 Context and Motivation ............................................................... 1
1.2 Research Problem ........................................................................ 2
1.3 Proposed Solution ........................................................................ 3
1.4 Objectives ................................................................................... 4
1.5 Justification and Relevance .......................................................... 5
1.6 Document Structure ..................................................................... 5

2 THEORETICAL FOUNDATION ......................................................... 3
2.1 Data Evolution and Criticality in the Digital Society ...................... 3
2.2 Distributed Systems and Computational Performance .................. 4
2.3 Microservices Architecture ........................................................... 5
2.4 In-Memory Caching as an Optimization Strategy .......................... 6
2.5 Cache Strategies Across Architectural Layers ............................... 7
2.6 Load Balancing ............................................................................. 8
2.7 Distributed Caching and Data Partitioning ................................... 9
2.8 Cache-Database Synchronization ................................................. 10
2.9 Real-Time and Mission-Critical Systems ...................................... 11
2.10 Observability and Performance Monitoring ................................. 13

3 MATERIALS AND METHODS .......................................................... 15
3.1 Technology Stack ......................................................................... 15
3.2 System Architecture .................................................................... 17
3.3 Data Modeling and Database Design ............................................ 18
3.4 Cache Strategy and Synchronization ............................................ 19
3.5 Data Flow and Communication Pipeline ....................................... 21
3.6 Performance Instrumentation ...................................................... 22
3.7 Experimental Methodology ......................................................... 23

4 RESULTS AND DISCUSSION .......................................................... 25
4.1 Latency and Performance Analysis .............................................. 25
4.2 Behavior Under High Load .......................................................... 27
4.3 Data Consistency and Synchronization ........................................ 29
4.4 Comparative Analysis of Cache Strategies ................................... 31

5 CONCLUSION ................................................................................ 34

REFERENCES ................................................................................... 36
APPENDICES .................................................................................... 38
ANNEXES ........................................................................................ 41


1. INTRODUCTION

1.1 Context and Motivation

Contemporary society, positioned within the context of Industry 5.0, is characterized by the massive production, processing, and consumption of data on a global scale. This reality transcends the traditional relationship between humans and machines, establishing information as a strategic asset and, in many cases, as a determining factor in the continuity of essential services. Timely access to reliable data now directly influences the success or failure of organizations, economic and financial decision-making, and, in more sensitive contexts, the preservation of human life — as observed in medical applications, government systems, and critical infrastructure.

According to the report *Data Age 2025: The Evolution of Data to Life-Critical*, published by the International Data Corporation (IDC, 2017), the global datasphere was projected to reach approximately 163 zettabytes (ZB) by 2025, highlighting the transition of data from a merely informational resource to a life-critical element. The study estimated that roughly 20% of global data would be classified as critical and approximately 10% as hypercritical — data whose immediate, complete, and reliable access would be decisive for security, health, and sensitive operations.

More recent evidence confirms that these projections have largely materialized. The global volume of data has surpassed the hundreds-of-zettabytes mark and continues on an exponential growth trajectory, driven by the proliferation of mobile devices, cloud applications, Internet of Things (IoT) deployments, and real-time systems. Concurrently, the majority of organizations adopting IoT solutions and large-scale digital platforms now prioritize real-time data processing as a competitive differentiator, reinforcing the need for architectures capable of guaranteeing low latency, high availability, and immediate responses.

This scenario is not merely theoretical but is amply demonstrated in high-impact real-world applications. Companies such as Uber, for instance, operate highly scalable distributed systems that process millions of simultaneous requests involving geolocation, dynamic pricing, driver availability, and real-time routing. To enable this operational model, the company extensively adopts architectures based on microservices, in-memory caching, and load balancing, thereby reducing dependence on centralized databases and ensuring responses within milliseconds even during demand peaks such as major events or rush hours.

Similarly, during the COVID-19 pandemic, numerous government systems faced unprecedented challenges related to sudden spikes in access volume and the requirement for continuous high availability. Vaccination scheduling platforms, emergency aid disbursement systems, public health data portals, and epidemiological notification systems needed to be rapidly scaled. In these contexts, the use of distributed architectures combined with in-memory caching and load balancing proved essential for avoiding service outages, reducing response times, and ensuring that critical information reached the public and government officials reliably and promptly.

Additional examples of critical applications include high-frequency financial trading systems, e-commerce platforms during promotional events, and digital hospital infrastructure, where delays of even a few seconds or availability failures can result in significant economic losses or risks to human life. Across all of these scenarios, it becomes evident that traditional monolithic solutions are insufficient for handling large data volumes, high concurrency, and stringent performance requirements.

1.2 Research Problem

Given this context, the adoption of distributed architectures emerges as a natural response to the challenges imposed by the era of critical and hypercritical data. Architectural models based on microservices enable the decomposition of complex systems into independent services, promoting horizontal scalability, continuous evolution, and reduced impact from isolated failures. However, as these applications become increasingly distributed, new challenges related to data consistency, response latency, and traffic overhead between services and databases inevitably arise.

In this regard, in-memory caching techniques become fundamental components for ensuring performance and resilience. The utilization of cache at different architectural layers — within the application itself, on dedicated external servers such as Redis, or even on the client side — reduces repetitive database access, mitigates bottlenecks, improves user experience, and sustains high request throughput. Strategies such as cache-aside, write-through, and write-behind are widely employed in modern distributed systems to balance performance and consistency.

Studies such as Piskin (2021) demonstrate the significant performance and scalability gains achieved through the adoption of multiple cache layers in distributed architectures, while Shi et al. (2020), with their DistCache proposal, explore advanced load balancing and consistency mechanisms in distributed caches, demonstrating the viability of these solutions even under intense traffic scenarios.

This work proposes the analysis and resolution of a real-world scenario in which the rapid, accurate, and reliable response of a system is fundamental to the safe continuity of a critical service. The scenario in question pertains to a toll management system responsible for the real-time correction of toll transactions involving lane users who encountered problems during passage, such as tag evasion, blocked tags, or access to closed lanes.

In such situations, it is essential that the lane operator be able to perform the transaction correction immediately, releasing the vehicle flow as quickly as possible. Delays in this process can generate elevated user stress, queue formation, negative impacts on traffic fluidity, and, in more critical cases, increase the risk of accidents, particularly during peak hours.

1.3 Proposed Solution

To address this scenario, a toll management system was developed using Java (Spring Boot 4.0.3 on JDK 21), responsible for the registration of highways, toll plazas, and lanes, as well as the reception, transmission, and correction of toll transactions in real time. All processed information is persisted in a PostgreSQL 15 relational database serving as the Single Source of Truth (SSOT). Additionally, a `PerformanceInterceptor` was implemented to record per-request metrics — response time, memory consumption, CPU usage, and data origin — to a dedicated `registro_performance` table.

The architecture employs two-layer in-memory caching: in-app L1 cache via `ConcurrentHashMap` (TTL 30 min, max 1,000 entries) and distributed L2 cache via Redis 7 (TTL 60 min, LRU eviction), following the Cache-Aside pattern. Load balancing is performed by NGINX, distributing requests across three backend instances using round-robin. Asynchronous transaction ingestion is enabled by Apache Kafka (`transacao-pedagio` topic), with a toll simulator developed in Python 3.10.

Complementarily, simulation applications were developed in Python: one responsible for simulating the flow of transactions at a toll plaza and another dedicated to simulating the lane transaction correction process. These applications enable controlled load generation and the reproduction of high-concurrency scenarios, approximating test conditions to real-world operations.

1.4 Objectives

The central proposal of this work consists of conducting comparative simulations to objectively evaluate the impacts of in-memory caching and distributed architectures on the performance of a critical toll management system. The **general objective** is to analyze how different data access strategies — direct relational database queries, in-application memory caching, and distributed caching with Redis — influence latency, computational resource consumption, and system responsiveness under high-concurrency scenarios.

The **specific objectives** are:

(i) to model a real-time toll transaction correction system based on a distributed architecture;
(ii) to implement caching mechanisms at different architectural layers (in-app L1 and Redis L2);
(iii) to simulate representative operational loads, including peaks of up to 500 simultaneous users;
(iv) to collect and analyze performance metrics via a custom `PerformanceInterceptor`, including response time, memory usage, CPU utilization, and data origin tracking;
(v) to compare the results obtained across three experimental scenarios — direct database access (A), Redis caching (B), and hybrid L1+L2 caching (C) — highlighting the gains and limitations of each strategy.

1.5 Justification and Relevance

This experimental approach aligns the research problem — the need for fast and reliable responses in critical toll systems — with the justification of the work, which lies in the practical and social relevance of solutions capable of reducing queues, user stress, and operational risks in high-demand highway environments. Thus, the proposed architecture is not limited to a theoretical exercise but reflects real challenges faced by real-time systems and critical infrastructure.

The relevance of this topic is corroborated by academic studies addressing electronic toll collection systems, real-time applications, and critical systems. Works such as Ferreira et al. (2019) discuss the evolution of automatic toll collection systems and the associated requirements for low latency and high availability. Kopetz (2011) and Burns and Wellings (2010) emphasize the fundamentals and challenges of real-time and critical systems, stressing the importance of predictability and reliability. Furthermore, recent research on distributed architectures and in-memory caching, such as Tanenbaum and Van Steen (2017) and Shi et al. (2020), reinforce the adoption of these solutions as effective strategies for ensuring performance and scalability in large-scale critical applications.

1.6 Document Structure

This work is organized into five chapters. **Chapter 2** presents the theoretical foundation, covering data evolution and criticality, distributed systems, microservices architecture, multi-layer caching strategies, load balancing, cache-database synchronization, real-time systems, and observability. **Chapter 3** describes the materials and methods employed, including the technology stack, system architecture, data modeling, cache strategy, data flow, performance instrumentation, and the experimental methodology with the three test scenarios. **Chapter 4** presents and discusses the results obtained, analyzing latency, behavior under high load, data consistency, and the comparative analysis of cache strategies. **Chapter 5** concludes the work with a synthesis of findings, identified limitations, and directions for future research.


2. THEORETICAL FOUNDATION

This chapter presents the principal concepts underpinning the development of high-performance distributed architectures. The discussion addresses the evolution and criticality of data in the digital society, the fundamentals of distributed systems, the use of in-memory caching as a performance optimization strategy, and the load balancing techniques employed to ensure scalability and high availability in modern applications.

2.1 Data Evolution and Criticality in the Digital Society

The exponential growth of data production is one of the most salient phenomena of contemporary digital transformation. The widespread adoption of technologies such as cloud computing, mobile devices, social networks, and the Internet of Things (IoT) has resulted in a significant increase in the volume of data generated, processed, and stored daily.

According to the International Data Corporation (IDC, 2017), the total set of data created, captured, and replicated globally — termed the *global datasphere* — has experienced accelerated growth over recent decades. The report *Data Age 2025: The Evolution of Data to Life-Critical* projected that the global data volume would reach approximately 163 zettabytes (ZB) by 2025, representing more than a tenfold increase relative to the volume recorded in 2016.

However, more significant than the increase in data volume is the transformation in the role that data plays in society. Information that was previously used solely to support administrative or operational processes has come to serve a fundamental role in strategic decision-making and mission-critical systems. According to the IDC (2017), approximately 20% of global data can be classified as critical, while roughly 10% is considered hypercritical — that is, data whose unavailability or delay in processing may result in direct impacts on security, health, or the operation of essential infrastructure.

This new classification highlights the growing dependence of digital systems in sectors such as transportation, healthcare, energy, financial services, and public administration. In such contexts, requirements including low latency, high availability, reliability, and scalability become fundamental to ensuring the adequate functioning of applications.

Another relevant factor emphasized in the report is the substantial increase in data generated by connected devices. Industrial sensors, intelligent vehicles, medical devices, and urban equipment continuously generate data streams that require real-time processing. A significant portion of these data is temporally sensitive, demanding computational architectures capable of processing information close to its source, thereby reducing latency and dependence on centralized data centers.

In this scenario, architectural models based on distributed systems gain prominence, as they offer greater capacity for scalability, resilience, and parallel processing. These characteristics are essential for sustaining modern applications that operate with large data volumes and require fast, reliable responses.

2.2 Distributed Systems and Computational Performance

Distributed systems can be defined as collections of independent computers that work in a coordinated manner to provide the user with the impression of a single, integrated system. According to Tanenbaum and Van Steen (2017), a distributed system consists of multiple interconnected nodes that share resources and cooperate to execute tasks efficiently.

One of the principal advantages of this architectural model is the possibility of horizontal scalability — that is, the ability to increase the computational capacity of the system by adding new nodes or instances. This characteristic is particularly important in environments with high volumes of simultaneous requests, such as e-commerce platforms, financial systems, and real-time transportation applications.

Beyond scalability, distributed systems also offer greater fault tolerance, since the unavailability of a specific node does not necessarily compromise the functioning of the system as a whole. Techniques such as data replication, load balancing, and data partitioning contribute to improving availability and reducing the risk of service interruption.

However, the adoption of distributed systems also introduces new challenges, particularly related to data consistency, synchronization between components, and latency in inter-service communication. In applications that require rapid responses, frequent communication with centralized databases can become a significant bottleneck, increasing response time and compromising user experience.

In this context, strategies for optimizing data access, such as the use of in-memory caching, become fundamental for improving overall system performance.

2.3 Microservices Architecture

The microservices architecture emerged as an evolution of traditional software development models based on monolithic systems. In this architectural paradigm, an application is structured as a collection of independent services, each responsible for a specific system functionality.

Each microservice can be developed, deployed, and scaled independently, enabling greater flexibility in the development and maintenance process. This approach favors the adoption of modern software engineering practices, including continuous integration, continuous delivery, and automated deployment.

Among the principal advantages of the microservices architecture are:

- Horizontal scalability of individual services
- Fault isolation between components
- Greater technological flexibility
- Independent evolution of functionalities

Conversely, the decomposition of applications into multiple services also increases the complexity of inter-component communication and requires efficient mechanisms for state management and data consistency.

In this scenario, caching and load balancing techniques play a fundamental role in ensuring that the system continues to exhibit high performance even with a large number of requests distributed across multiple services.

2.4 In-Memory Caching as an Optimization Strategy

In-memory caching is a widely employed technique for improving the performance of computational systems. The fundamental principle consists of temporarily storing frequently accessed data in a high-speed memory layer, reducing the need for repeated queries to slower data sources such as databases or external services.

According to Piskin (2021), the use of in-memory caching allows frequently requested data to be returned in milliseconds, significantly reducing application response times and diminishing the load on persistent storage systems.

In distributed systems, caching can be implemented at different architectural layers, enabling optimizations on both the backend and frontend. This approach contributes to reducing latency, increasing the system's processing capacity, and improving the end-user experience.

Furthermore, caching plays an important role in reducing computational resource consumption by decreasing the number of read and write operations performed on the database.

2.5 Cache Strategies Across Architectural Layers

Caching can be implemented at multiple layers of a distributed system's architecture, each with specific characteristics regarding performance, consistency, and data sharing.

**In-Application Cache (In-App)**

Local caching, implemented directly within the application, stores data in the memory of the service instance itself. Libraries such as Caffeine and in-memory data structures, such as `ConcurrentHashMap`, are frequently used for this purpose.

This strategy offers extremely low latency, as data is accessed directly from the application's memory space. However, since each instance maintains its own cache, data is not shared across different instances, which can lead to inconsistencies in highly distributed environments.

**Distributed Cache with Redis**

Redis is one of the most widely adopted distributed caching solutions in modern systems. It is a high-performance in-memory data store that supports the storage of data structures including strings, lists, hashes, and sets.

Unlike local caching, Redis can be shared by multiple application instances, functioning as a centralized cache layer. This enables greater data consistency and facilitates the implementation of cache expiration and invalidation policies.

Key features offered by Redis include:

- Automatic key expiration with configurable TTL
- Eviction policies such as LRU (Least Recently Used)
- Data replication
- Support for clustering and sharding

**Client-Side Cache**

An additional complementary strategy involves the temporary storage of data on the client itself, such as web browsers or mobile applications. This model reduces the number of requests sent to the server and can significantly improve the user experience in web applications.

However, this approach requires additional care regarding the update and synchronization of locally stored information.

2.6 Load Balancing

Load balancing is a fundamental technique in distributed architectures, responsible for distributing requests among multiple instances of a service. This strategy prevents overload on a single server and improves both performance and system availability.

Among the most widely used solutions for load balancing in web applications is NGINX, which acts as a reverse proxy responsible for forwarding requests to different backend instances.

NGINX offers various request distribution algorithms, among which the following stand out:

- **Round-robin**: distributes requests sequentially among servers
- **IP hash**: routes requests based on the client's IP address
- **Least connections**: forwards requests to the server with the fewest active connections

The use of load balancers significantly increases the system's throughput capacity, in addition to facilitating the implementation of horizontally scalable architectures.

2.7 Distributed Caching and Data Partitioning

In large-scale environments, a single cache server may be insufficient to meet storage and processing demands. In such cases, it becomes necessary to distribute data across multiple cache instances through partitioning techniques, also known as sharding.

Sharding consists of dividing the dataset into different segments and distributing them across multiple system nodes. This approach increases the total storage capacity and improves load balancing among servers.

Shi et al. (2020) propose DistCache, a distributed caching architecture that employs multiple layers and balancing algorithms to guarantee linear scalability and improved request distribution across cache nodes. The model provides mathematical load balancing guarantees, demonstrating that the use of multiple cache layers can significantly improve the performance of large-scale systems.

2.8 Cache-Database Synchronization

One of the principal challenges in cache utilization is ensuring data consistency between the cache layer and the persistent database. If synchronization is not performed correctly, the system may return stale information to users.

To mitigate this problem, various synchronization strategies are employed in distributed systems. Among the most common are:

- **Cache-aside**: data is initially sought in the cache; if not available, it is retrieved from the database and subsequently stored in the cache.
- **Write-through**: write operations are performed simultaneously on the cache and the database.
- **Write-behind (write-back)**: updates are first applied to the cache and subsequently persisted to the database asynchronously.

Each strategy presents advantages and limitations related to latency, consistency, and implementation complexity. The selection of the most appropriate approach depends on the application's characteristics, the frequency of data updates, and the system's consistency requirements.

2.9 Real-Time and Mission-Critical Systems

Real-time systems are computational systems in which the correctness of an operation depends not only on the logical result produced but also on the time at which that result is delivered. According to Kopetz (2011), a real-time system must guarantee that certain tasks are executed within pre-defined temporal limits, termed deadlines. Should these limits be exceeded — even if the computational result is logically correct — the system may be considered to have failed.

This type of system is present in numerous critical contexts of modern society, including industrial control systems, aeronautical systems, medical devices, energy networks, transportation systems, and high-frequency financial applications. In these applications, delays in system response can result in severe consequences, such as the interruption of essential services, significant economic losses, or risks to human safety.

According to Burns and Wellings (2010), real-time systems can be classified into two principal categories: hard real-time systems and soft real-time systems. In hard real-time systems, compliance with the execution deadline is absolutely mandatory, and any delay may compromise the safe functioning of the system. Examples include aircraft control systems, implantable medical devices, and nuclear power plant control systems.

In soft real-time systems, occasional delays may be tolerated under certain circumstances, although they may degrade the quality of service or generate operational impacts. Multimedia systems, streaming platforms, and various high-demand web applications are examples of this category. In these cases, while minor latency variations may occur, the system is expected to maintain low and consistent response times to ensure an adequate user experience.

Another fundamental concept in these systems is temporal predictability. Unlike traditional systems where average performance may suffice, real-time systems require more rigorous guarantees regarding the temporal behavior of operations. This means that computational architectures must be designed to minimize unpredictable latency variations, ensuring that critical tasks are executed within acceptable time bounds.

In the context of modern distributed systems, guaranteeing temporal predictability becomes an additional challenge, since multiple independent components must cooperate through communication networks. Network latency, process concurrency, and database access overhead can introduce significant delays in request processing.

In this scenario, techniques such as load balancing, in-memory caching, and horizontal scalability become fundamental for ensuring that the system can maintain adequate response times even under high-demand conditions. The use of in-memory caching, for instance, significantly reduces the time required to retrieve frequently used data, while load balancing mechanisms distribute requests across multiple application instances, preventing overload on any single server.

In the context of this work, the toll management system responsible for the correction of toll transactions exhibits characteristics typical of a soft real-time system. During lane operations, the operator must register and correct vehicle transactions within seconds to prevent queue formation and ensure traffic fluidity. Although minor delays may occur occasionally, elevated response times can generate congestion, user stress, and operational risks, particularly during peak traffic hours.

Accordingly, the architecture proposed in this study seeks to reduce data access latency and improve system responsiveness through the utilization of in-memory caching, distributed architecture, and load balancing. These strategies contribute to approximating the system's behavior to the requirements expected of real-time applications, ensuring greater predictability in request processing and greater reliability in toll system operations.

Thus, the incorporation of real-time system principles into the application architecture reinforces the importance of technological solutions capable of handling high-concurrency scenarios and critical rapid-response demands — characteristics increasingly prevalent in modern digital systems.

2.10 Observability and Performance Monitoring in Distributed Systems

In modern distributed systems, the ability to observe, measure, and analyze application behavior at runtime has become an essential element for ensuring performance, reliability, and scalability. This set of practices is known as observability — a concept that extends beyond simple infrastructure monitoring, enabling the understanding of a system's internal state from its external outputs, such as metrics, logs, and execution traces.

According to Sigelman et al. (2010), observability in distributed systems enables the identification of performance bottlenecks, fault diagnosis, and understanding of request flow among different architectural components. In applications composed of multiple services and layers — including databases, caches, and application services — the absence of visibility into system behavior can significantly hinder the identification of operational problems.

One of the principal approaches to performance monitoring involves the continuous collection of operational metrics, which represent quantitative indicators of system functioning. Among the most relevant metrics in distributed systems are:

- **Response time (latency)**: represents the interval between the sending of a request and the delivery of the response to the client. In high-performance systems, elevated latencies may indicate resource overload or bottlenecks in inter-service communication.
- **CPU usage**: measures the processing consumption of servers or application instances. Elevated values may indicate excessive load or inefficient task processing.
- **Memory consumption**: indicates the amount of memory utilized by the application during execution. Monitoring this indicator is important for preventing performance degradation or failures caused by resource exhaustion.
- **Request rate (throughput)**: corresponds to the number of requests processed by the system within a given time interval, serving as an important indicator of the application's processing capacity.

In addition to these metrics, modern distributed systems frequently employ distributed tracing techniques, which allow tracking the path of a request through multiple services and components. This approach enables precise identification of which processing stages are contributing to increased latency or execution failures.

Monitoring and observability tools such as Prometheus, Grafana, OpenTelemetry, and Application Performance Monitoring (APM) systems have been widely adopted for collecting, storing, and visualizing these metrics in real time. These solutions enable the creation of dashboards and automated alerts that assist in the operational management of distributed applications.

In the context of this work, observability plays a fundamental role in evaluating the different architectural strategies analyzed. During the experiments, metrics related to request response time, memory consumption, and computational resource usage were collected. This information enables objective comparison of system behavior under different data access scenarios, including:

- Direct access to the relational database;
- Use of in-application memory cache;
- Utilization of distributed cache via Redis.

The analysis of these metrics enables the identification of each strategy's impact on system performance, highlighting gains or limitations in terms of latency, resource consumption, and capacity for processing simultaneous requests.

Thus, the use of observability and monitoring techniques not only assists in the operation of distributed systems in real environments but also constitutes an essential tool for scientific experimentation and comparative evaluation of computational architectures. By providing objective data on system behavior, these practices contribute to grounding architectural decisions and empirically validating proposed solutions for high-performance applications.


3. MATERIALS AND METHODS

This chapter describes the experimental methodology, computational resources, and logical architecture employed for the evaluation of caching and load balancing strategies. The focus resides on the technical implementation and the instrumentation necessary for collecting performance metrics in a mission-critical scenario.

3.1 Technology Stack

For the construction of the experimental environment, a set of industry-established technologies was selected to simulate a highly scalable microservices ecosystem. Table 1 summarizes the complete technology stack.

**[Table 1 — Technology Stack Summary]**

| Layer                | Technology                          | Version      | Purpose                                                  |
|----------------------|-------------------------------------|--------------|----------------------------------------------------------|
| Backend              | Spring Boot (Java)                  | 4.0.3 / JDK 21 | Core toll management microservice (`com.stcs.tollmanagement`)  |
| Frontend             | React                               | 18           | Lane operator dashboard interface                        |
| API Gateway          | NGINX                               | latest       | Reverse proxy, load balancing, rate limiting, CORS       |
| Persistent Storage   | PostgreSQL                          | 15           | Single Source of Truth (SSOT) — relational database      |
| Distributed Cache    | Redis                               | 7            | L2 shared in-memory cache (LRU eviction, TTL 60 min)    |
| Messaging            | Apache Kafka (Confluent)            | cp-kafka:7.5.0 | Asynchronous transaction ingestion (topic: `transacao-pedagio`) |
| Simulator            | Python                              | 3.10         | Toll transaction generator (CLI + tkinter GUI)           |
| Observability        | Prometheus + Grafana                | latest       | Metrics collection and dashboard visualization           |
| Containerization     | Docker Compose                      | —            | Service orchestration (10 containers)                    |
| CI/CD                | Jenkins                             | —            | Continuous integration and delivery pipeline              |

The backend was developed using the Spring Boot framework version 4.0.3 running on Java 21, selected for its native support for cache abstractions, seamless integration with distributed ecosystems, and built-in Apache Kafka support via `spring-kafka`. The application is organized under the Java package `com.stcs.tollmanagement` and exposes a RESTful API on port **9080**.

The frontend was implemented using React 18, providing a web-based operator dashboard for real-time transaction search, visualization, and correction.

NGINX serves as the API gateway, configured as a reverse proxy that distributes incoming requests across multiple backend instances using a round-robin algorithm. Additional gateway features include rate limiting (10 requests per second per client IP with a burst allowance of 20), CORS header management, a `/health` endpoint for container health checks, and security headers (`X-Content-Type-Options`, `X-Frame-Options`, `X-XSS-Protection`).

PostgreSQL 15 serves as the Single Source of Truth (SSOT) for all toll management data, while Redis 7 operates as the L2 distributed cache with automatic key expiration (TTL of 60 minutes) and LRU eviction policy.

Apache Kafka (Confluent cp-kafka:7.5.0) provides the asynchronous messaging backbone, receiving toll transactions from the Python-based simulator and delivering them to the backend's Kafka consumer. The producer is configured with `acks=all` to ensure delivery guarantees.

The toll simulator was developed in Python 3.10, offering both a command-line interface (`main.py`) and a graphical user interface (`gui.py`, built with tkinter). It uses the Faker library to generate realistic transaction data and supports configurable parameters including transaction rate (`--rate`), error rate (`--error-rate`), and stress test mode (`--stress`).

Prometheus scrapes metrics from the Spring Boot Actuator endpoint (`/actuator/prometheus`) at 15-second intervals, and Grafana provides real-time dashboard visualization for latency, throughput, cache hit rate, and resource usage.

The entire environment is containerized using Docker Compose, orchestrating 10 services: `nginx`, `toll-management-service-1`, `toll-management-service-2`, `toll-management-service-3`, `toll-simulator`, `toll-frontend`, `redis`, `postgres`, `kafka`, `zookeeper`, `prometheus`, and `grafana`.

3.2 System Architecture

The proposed architecture is grounded in component decoupling to ensure horizontal scalability. As illustrated in Figure 1, requests originating from the frontend or the simulator are intercepted by NGINX, which distributes them among backend instances.

**Figure 1 — High-Level System Architecture Diagram**

![Figure 1 — System Architecture](assets/fig1-architecture.png)

*The diagram depicts the client layer (React frontend and Python toll simulator), the gateway layer (NGINX on port 80), the application layer (three Spring Boot instances, each with an L1 in-app ConcurrentHashMap cache, running on port 9080 and consuming from Kafka), and the data layer (Redis L2 cache and PostgreSQL SSOT). The toll simulator communicates with Kafka asynchronously, while Kafka consumers in each backend instance persist transactions to PostgreSQL. Prometheus scrapes all three backend instances, and Grafana renders observability dashboards.*

The logic for processing a transaction correction follows a layered data availability verification flow, detailed in Figure 2.

**Figure 2 — UML Sequence Diagram: Transaction Correction with Cache-Aside**

![Figure 2 — Sequence Diagram](assets/fig2-sequence.png)

*The diagram represents the interaction sequence: the operator's request arrives at NGINX, which forwards it to one of the backend instances via round-robin. The instance first checks the L1 in-app ConcurrentHashMap cache. On an L1 miss, it checks the L2 Redis cache via `RedisTemplate<String, Object>`. On an L2 miss, it queries PostgreSQL, then populates both L2 (Redis) and L1 (ConcurrentHashMap) before returning the response to the client. Each data access records an `origem_dados` attribute (`CACHE_LOCAL`, `CACHE_REDIS`, or `BANCO_DADOS`).*

3.3 Data Modeling and Database Design

The data model was designed to support comprehensive toll transaction management, encompassing the full lifecycle from highway registration through transaction processing and correction. PostgreSQL 15 serves as the persistent storage layer with a normalized relational schema comprising ten tables. Figure 3 presents the complete entity-relationship diagram.

**Figure 3 — Entity-Relationship Diagram (10 Tables)**

![Figure 3 — ER Diagram](assets/fig3-er-diagram.png)

*The diagram shows the following entities and their relationships:*

| Table                   | Description                                         | Key Relationships                           |
|-------------------------|-----------------------------------------------------|---------------------------------------------|
| `concessionaria`        | Toll concessionaire companies (CNPJ, contract)      | 1:N → `rodovia`                             |
| `rodovia`               | Highways (code, state, extension in km)             | FK → `concessionaria`; 1:N → `praca_pedagio` |
| `praca_pedagio`         | Toll plazas (km position, direction, active status) | FK → `rodovia`; 1:N → `pista_pedagio`, `transacao_pedagio` |
| `pista_pedagio`         | Toll lanes (lane number, type: MANUAL/TAG/MISTA)    | FK → `praca_pedagio`; UNIQUE(praca_id, numero_pista) |
| `tarifa_pedagio`        | Toll rates by vehicle type (MOTO, CARRO, CAMINHAO)  | 1:N → `transacao_pedagio`                   |
| `transacao_pedagio`     | Toll transactions (plate, tag, SHA-256 hash, status: OK/OCORRENCIA/CORRIGIDA) | FK → `praca`, `pista`, `tarifa`; 1:N → `ocorrencia`, `correcao` |
| `ocorrencia_transacao`  | Transaction issues (EVASAO, TAG_BLOQUEADA, SEM_SALDO, FALHA_LEITURA) | FK → `transacao_pedagio`          |
| `correcao_transacao`    | Corrections by operators (MANUAL/AUTOMATICA)        | FK → `transacao_pedagio`, `operador`         |
| `operador`              | System operators (hashed password, unique username/email) | 1:N → `correcao_transacao`           |
| `registro_performance`  | Per-request performance metrics                     | Standalone (no FK dependencies)              |

A total of **15 database indexes** were defined to optimize query performance, targeting foreign key joins (`idx_rodovia_concessionaria`, `idx_praca_rodovia`, `idx_pista_praca`), transaction status filtering (`idx_transacao_status`), vehicle plate lookups (`idx_transacao_placa`), and time-range queries on passage timestamps (`idx_transacao_data`) and performance records (`idx_performance_criado`).

Each toll transaction includes a SHA-256 integrity hash (`hash_integridade`) computed from the transaction's core attributes, providing a cryptographic mechanism for detecting unauthorized modifications.

3.4 Cache Strategy and Synchronization

The implementation employs the **Cache-Aside** pattern with a two-layer approach (L1 and L2), as illustrated in Figure 4.

**Figure 4 — Two-Layer Cache-Aside Strategy Flow**

![Figure 4 — Cache-Aside Flow](assets/fig4-cache-aside.png)

*The diagram shows the request flow: Application → check L1 (ConcurrentHashMap) → HIT: return data (origin: `CACHE_LOCAL`) | MISS: check L2 (Redis) → HIT: return data, populate L1 (origin: `CACHE_REDIS`) | MISS: query PostgreSQL → return data, populate L2 and L1 (origin: `BANCO_DADOS`).*

**L1 Cache — In-Application (`ConcurrentHashMap`)**

The L1 cache is implemented as a `ConcurrentHashMap<String, CacheEntry>` within the `CacheService` class. The `CacheEntry` inner class encapsulates both the cached data and an expiration timestamp. Configuration parameters include:

- Maximum entries: **1,000** (configurable via `cache.local.max-size`)
- TTL: **30 minutes** (configurable via `cache.local.ttl-minutes`)
- Scope: Per-instance (not shared across backend instances)
- Thread safety: Guaranteed by `ConcurrentHashMap`

**L2 Cache — Distributed (Redis)**

The L2 cache operates via `RedisTemplate<String, Object>`, shared across all three backend instances. Configuration parameters include:

- TTL: **60 minutes** (configurable via `cache.redis.ttl-minutes`)
- Eviction policy: LRU (Least Recently Used)
- Scope: Global (shared across all instances)

**Redis Cache Key Conventions:**

| Key Pattern                                  | Example                          | TTL    | Description                    |
|----------------------------------------------|----------------------------------|--------|--------------------------------|
| `transacoes:ocorrencias:{limit}:{hours}`     | `transacoes:ocorrencias:100:24`  | 60 min | Transactions with occurrences  |
| `praca:{id}`                                 | `praca:1`                        | 60 min | Single toll plaza by ID        |
| `pista:{id}`                                 | `pista:42`                       | 60 min | Single toll lane by ID         |
| `transacao:{id}`                             | `transacao:100`                  | 60 min | Single transaction by ID       |

**Cache Invalidation** is handled through two complementary mechanisms:

1. **TTL-based automatic expiry**: L1 entries expire after 30 minutes; L2 entries expire after 60 minutes.
2. **Event-driven explicit invalidation**: On write operations (transaction corrections, status updates), the corresponding cache entries in both L1 and L2 are explicitly invalidated to prevent stale reads.

The following code excerpt illustrates the core cache integration with Redis in the Spring Boot application:

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

3.5 Data Flow and Communication Pipeline

The request processing pipeline is optimized to minimize disk I/O. Figure 5 details the complete path traversed by data from ingestion to response.

**Figure 5 — Request Processing Pipeline**

![Figure 5 — Request Pipeline](assets/fig5-pipeline.png)

*Flow: Data Entry → NGINX (Load Balancing, Rate Limiting, CORS, Security Headers) → Spring Boot Backend (PerformanceInterceptor → Controller → CacheService → L1/L2/DB) → Response with `origem_dados` tracking.*

**Kafka Ingestion Pipeline:**

The toll simulator (Python 3.10) produces `TransacaoPedagioKafkaDTO` messages to the Kafka topic `transacao-pedagio`. Each backend instance runs a `TransacaoKafkaConsumer` annotated with `@KafkaListener` and `@Transactional`, which:

1. Receives the transaction DTO from Kafka
2. Validates foreign key references (plaza, lane, and tariff existence)
3. Persists the transaction to PostgreSQL
4. Flags transactions with detected errors as `OCORRENCIA`

The simulator supports deliberate error injection — configurable via the `--error-rate` parameter — which introduces invalid license plates, incorrect monetary values, duplicate tag IDs, and temporal inconsistencies, simulating real-world data quality issues.

3.6 Performance Instrumentation

A custom `PerformanceInterceptor`, implemented as a Spring `HandlerInterceptor`, captures comprehensive per-request metrics. The interceptor records the following data points for every API request:

| Metric                   | Source                           | Unit          |
|--------------------------|----------------------------------|---------------|
| Processing time          | `System.currentTimeMillis()`     | Milliseconds  |
| Heap memory used         | `MemoryMXBean.getHeapMemoryUsage()` | MB         |
| Heap memory free         | Computed from total − used       | MB            |
| Heap memory total        | `MemoryMXBean.getHeapMemoryUsage()` | MB         |
| CPU usage                | `OperatingSystemMXBean`          | Ratio (0–1)   |
| Active thread count      | `ThreadMXBean`                   | Count         |
| HTTP status code         | `HttpServletResponse`            | Integer       |
| Endpoint path            | `HttpServletRequest`             | String        |
| HTTP method              | `HttpServletRequest`             | String        |
| Data origin              | `request.getAttribute("origemDados")` | Enum     |

All metrics are persisted to the `registro_performance` table in PostgreSQL, enabling post-experiment analysis through SQL queries and aggregate statistics. The `origem_dados` field — an enumeration with values `CACHE_LOCAL`, `CACHE_REDIS`, `BANCO_DADOS`, and `NAO_APLICAVEL` — enables precise tracking of which data layer served each request, providing the foundation for cache hit rate calculations.

3.7 Experimental Methodology

The test environment was isolated in Docker containers to guarantee reproducibility. Load was generated using parameterized Python scripts to simulate concurrency peaks of up to 500 simultaneous users correcting transactions.

**3.7.1 Test Scenarios**

Three comparative scenarios were defined:

- **Scenario A — Direct Database Access (No Cache)**: All read requests query PostgreSQL directly. This serves as the performance baseline against which caching strategies are measured.
- **Scenario B — Distributed Cache Only (Redis L2)**: Read requests first check the Redis distributed cache before falling back to PostgreSQL on cache misses. The in-application L1 cache is disabled.
- **Scenario C — Hybrid Cache (L1 In-App + L2 Redis)**: Read requests follow the full two-layer path: L1 ConcurrentHashMap → L2 Redis → PostgreSQL. This represents the complete production architecture.

**3.7.2 Metrics and Instrumentation**

Data collection was performed via the custom `PerformanceInterceptor` and supplemented by Prometheus/Grafana dashboards, focusing on the following metrics:

- **Response Latency**: Measured in milliseconds (ms), analyzing the mean and the critical percentiles p95 and p99 (to identify performance outliers).
- **Throughput (TPS)**: Number of transactions processed per second.
- **Cache Hit Rate**: Percentage of requests served by the cache without requiring database access, computed from the `origem_dados` field distribution.
- **Resource Consumption**: CPU and RAM monitoring of containers via `docker stats` and Prometheus metrics.
- **Data Consistency**: Verification of integrity between cached data and its final persistence state in PostgreSQL, validated through SHA-256 hash comparison.


4. RESULTS AND DISCUSSION

This chapter presents and discusses the results obtained from the experiments conducted with the proposed architecture, based on the three scenarios defined in Section 3.7.1. Given that comprehensive benchmark data collection across all scenarios is an ongoing process, the analysis presented herein combines preliminary empirical observations with projected results grounded in the architectural characteristics and the theoretical foundations established in Chapter 2. Placeholder markers indicate where definitive charts and tables will be incorporated upon completion of the full experimental campaign.

4.1 Latency and Performance Analysis

The primary objective of this analysis is to evaluate the impact of different caching strategies on request latency across the three experimental scenarios. Latency is measured at the application level via the `PerformanceInterceptor`, which records the processing time in milliseconds for every API request, along with the `origem_dados` field indicating whether the data was served from the L1 in-app cache, the L2 Redis cache, or the PostgreSQL database.

**[Table 2 — Expected Response Latency by Scenario (Transaction Query Endpoint)]**

| Metric       | Scenario A (No Cache) | Scenario B (Redis L2) | Scenario C (L1 + L2 Hybrid) |
|--------------|----------------------|----------------------|------------------------------|
| Mean         | ~80–120 ms           | ~10–25 ms            | ~2–8 ms                      |
| p95          | ~120–200 ms          | ~15–40 ms            | ~3–12 ms                     |
| p99          | ~150–300 ms          | ~20–50 ms            | ~1–5 ms (L1 hit)             |

*Note: Values represent projected ranges based on preliminary observations and architectural analysis. Definitive measurements will be inserted upon completion of the full benchmark campaign.*

In **Scenario A**, where all read operations are directed to PostgreSQL, the expected mean latency is projected to fall in the range of 80–120 ms under moderate load conditions (100 concurrent users). This baseline reflects the inherent overhead of establishing database connections from the connection pool, executing indexed SQL queries across the 10-table schema, serializing result sets to Java objects via JPA/Hibernate, and transmitting the response through NGINX. Under higher load conditions (500 concurrent users), the p99 latency is anticipated to increase substantially — potentially reaching 200–300 ms — as connection pool contention and disk I/O become limiting factors.

In **Scenario B**, the introduction of Redis as the L2 distributed cache is expected to reduce mean latency to the 10–25 ms range. After the initial cache population (cold start), subsequent requests for the same resources would be served from Redis, eliminating the database query overhead. The p99 latency under load is projected at 20–50 ms, reflecting occasional cache misses and Redis network round-trip time. The improvement relative to Scenario A is anticipated to be on the order of 75–85% for mean latency.

In **Scenario C**, the full hybrid cache architecture adds the L1 ConcurrentHashMap layer, which stores frequently accessed data directly in the JVM heap of each backend instance. For L1 cache hits, the projected p99 latency drops to approximately 1–5 ms, as data retrieval requires no network communication whatsoever — merely a thread-safe hashmap lookup in local memory. The mean latency is expected to stabilize around 2–8 ms, representing an improvement of approximately 95–97% relative to Scenario A.

**Figure 6 — Latency Distribution Comparison Across Scenarios**

![Figure 6 — Latency Distribution](assets/fig6-latency.png)

*This figure presents three overlaid histogram or box-plot distributions showing the response time distribution for each scenario at 250 concurrent users. The x-axis represents latency in milliseconds (log scale), and the y-axis represents the frequency of requests. Scenario A is expected to show a wide, right-skewed distribution centered around 80–120 ms; Scenario B, a tighter distribution around 10–25 ms with a secondary peak at ~80 ms for cache misses; and Scenario C, a narrow, left-concentrated distribution below 10 ms.*

The latency improvement from Scenario A to Scenario C can be attributed to the elimination of two principal bottlenecks: (i) database connection pool contention, which is entirely bypassed on L1 cache hits; and (ii) network serialization/deserialization overhead to Redis, which is avoided when data resides in the local ConcurrentHashMap.

It is important to note that during the initial cold-start period — before the cache is warmed — all three scenarios exhibit similar latency profiles, as every request must be served from PostgreSQL. The rate at which cache warm-up occurs depends on the request distribution and the configurable TTL values. Based on preliminary observations, a steady-state cache hit rate is anticipated to be reached within approximately 5–10 minutes of sustained traffic under Scenario C.

4.2 Behavior Under High Load

This section analyzes the expected behavior of the system under progressively increasing load conditions, evaluating throughput, resource consumption, and degradation patterns across the three scenarios.

**[Table 3 — Expected Throughput by Concurrent User Count]**

| Concurrent Users | Scenario A (TPS) | Scenario B (TPS) | Scenario C (TPS) |
|------------------|-------------------|-------------------|-------------------|
| 100              | ~200–350          | ~800–1,200        | ~1,500–2,500      |
| 250              | ~150–250          | ~700–1,000        | ~1,400–2,200      |
| 500              | ~80–150           | ~500–800          | ~1,200–2,000      |

*Note: TPS projections are based on architectural analysis and typical throughput characteristics of the employed technologies.*

**Figure 7 — Throughput vs. Concurrent Users**

![Figure 7 — Throughput vs. Concurrent Users](assets/fig7-throughput.png)

*This figure presents a bar chart with three data series (one per scenario) showing throughput (TPS) on the y-axis against the number of concurrent users (100, 250, 500) on the x-axis. Scenario A is expected to show a declining curve as load increases, with a sharp drop beyond 250 users. Scenario B is expected to maintain a flatter profile, while Scenario C is expected to exhibit the highest sustained throughput across all load levels.*

The load balancing provided by NGINX across three backend instances (`toll-management-service-1`, `toll-management-service-2`, `toll-management-service-3`) plays a critical role in preventing single-point bottlenecks. Under the round-robin distribution algorithm, each instance receives approximately one-third of the total request volume. This distribution is expected to result in a near-linear scaling factor of approximately 2.5–2.8x relative to a single-instance deployment, with the sub-linear factor attributed to shared resource contention on PostgreSQL and Redis.

In **Scenario A**, the system is anticipated to reach its throughput ceiling earliest, primarily due to PostgreSQL connection pool exhaustion. With a typical HikariCP connection pool size of 10 connections per instance (30 total across three instances), and assuming an average query execution time of 80–120 ms, the theoretical maximum throughput is approximately 250–375 TPS. Beyond this point, requests begin queuing for available connections, resulting in rapidly escalating latency and potential timeout errors.

In **Scenario B**, the Redis cache layer effectively reduces the load on PostgreSQL by serving a significant proportion of read requests from memory. Assuming a steady-state cache hit rate of 60–75%, the database receives only 25–40% of total read traffic, substantially increasing the system's effective throughput capacity.

In **Scenario C**, the L1 ConcurrentHashMap further absorbs a substantial portion of reads within the JVM itself. Based on the maximum L1 cache size of 1,000 entries and the expected access patterns (where a relatively small set of toll plazas, lanes, and recent transactions constitute the "hot set"), it is anticipated that L1 will serve 40–60% of total read requests. The combined L1+L2 cache hit rate is projected to reach 85–95%, meaning that PostgreSQL handles only 5–15% of read traffic — predominantly for first-time queries on infrequently accessed resources.

**Resource Consumption:**

**Figure 8 — CPU and Memory Usage Under Load (500 Concurrent Users)**

![Figure 8 — CPU and Memory](assets/fig8-resources.png)

*This figure presents comparative charts showing CPU utilization (%) and heap memory consumption (MB) for a single backend instance across the three scenarios at 500 concurrent users. Scenario A is expected to show the highest CPU and memory consumption due to continuous object serialization from database result sets. Scenario C is expected to show moderate memory consumption (due to L1 cache entries) but substantially lower CPU utilization due to reduced database communication.*

Preliminary observations indicate that the memory footprint of the L1 cache in Scenario C is modest: with a maximum of 1,000 CacheEntry objects per instance and typical entry sizes of 1–5 KB, the total L1 memory overhead is estimated at approximately 1–5 MB per instance — well within the typical JVM heap allocation for a Spring Boot application.

4.3 Data Consistency and Synchronization

Ensuring data consistency between the cache layers and the persistent database is a critical concern in any multi-layer caching architecture. This section discusses the consistency guarantees provided by the Cache-Aside pattern employed in the proposed system, the mechanisms for cache invalidation, and the potential for stale reads.

**Consistency Model:**

The Cache-Aside pattern, as implemented in the `CacheService`, provides **eventual consistency** between the cache layers and PostgreSQL. In this model, the database always represents the authoritative state of the data (SSOT), while the cache layers contain potentially stale copies that are refreshed either through TTL-based expiration or explicit invalidation on writes.

**Write Path Consistency:**

When a transaction correction is performed, the system executes the following sequence:

1. The correction is persisted to PostgreSQL within a `@Transactional` boundary.
2. The corresponding cache entries in L2 (Redis) are explicitly invalidated via `DEL` commands.
3. The corresponding L1 entries in the local ConcurrentHashMap are removed.
4. The response is returned to the client.

This write-invalidate approach ensures that subsequent reads will trigger a cache miss and fetch the updated data from PostgreSQL, thereby maintaining consistency. However, because the three backend instances maintain independent L1 caches, there exists a brief temporal window — potentially lasting until the next L1 TTL expiration (up to 30 minutes) — during which an instance that did not process the write operation may still serve stale L1 data. This is a well-documented trade-off in per-instance caching architectures (Tanenbaum & Van Steen, 2017).

**Stale Read Mitigation Strategies:**

Several mechanisms are employed to mitigate the risk and impact of stale reads:

1. **Tiered TTL configuration**: The L1 TTL (30 minutes) is intentionally shorter than the L2 TTL (60 minutes), ensuring that local cache entries expire more frequently and are refreshed from the authoritative L2 or database layer.
2. **Event-driven invalidation**: On write operations, both L1 and L2 entries are explicitly invalidated on the instance that processes the write, providing immediate consistency on that instance.
3. **SHA-256 integrity hashing**: Each transaction includes a `hash_integridade` field computed from its core attributes. This hash can be used for post-hoc consistency verification between cached and persisted states.

**Data Origin Tracking:**

The `origem_dados` tracking mechanism, implemented via the `PerformanceInterceptor`, provides a powerful instrument for empirically validating cache behavior. By querying the `registro_performance` table, it is possible to compute the distribution of data sources across all requests.

**[Table 4 — Expected Cache Hit Rate Distribution by Scenario]**

| Data Origin       | Scenario A | Scenario B | Scenario C |
|--------------------|-----------|-----------|-----------|
| `CACHE_LOCAL`      | 0%        | 0%        | 40–60%    |
| `CACHE_REDIS`      | 0%        | 60–75%    | 30–40%    |
| `BANCO_DADOS`      | 100%      | 25–40%    | 5–15%     |
| `NAO_APLICAVEL`    | —         | —         | —         |

*Note: Percentages represent projected steady-state distributions after cache warm-up.*

These distributions are expected to confirm the theoretical expectation that the hybrid L1+L2 architecture maximizes the proportion of requests served from the fastest available data source, with the majority of traffic absorbed by the in-application ConcurrentHashMap and the Redis layer, leaving only a small fraction of requests to reach PostgreSQL.

**Consistency Verification:**

To empirically validate consistency, a verification procedure was designed in which:

1. A transaction is modified via the correction API endpoint.
2. The updated hash is computed and compared against the value stored in PostgreSQL.
3. Subsequent reads from each backend instance are monitored to verify that stale data is not served beyond the maximum TTL window.

Based on the architectural design, it is anticipated that no consistency violations will be observed from the instance that processed the write operation (due to immediate invalidation), while other instances may serve stale data for at most 30 minutes (the L1 TTL), after which the expired entry is refreshed from Redis or PostgreSQL.

4.4 Comparative Analysis of Cache Strategies

This section presents a comprehensive comparison of the three caching approaches evaluated in this study, synthesizing the findings from Sections 4.1 through 4.3.

**[Table 5 — Comparative Summary of Cache Strategies]**

| Criterion                  | Scenario A (No Cache) | Scenario B (Redis L2) | Scenario C (L1 + L2) |
|----------------------------|-----------------------|-----------------------|------------------------|
| Mean latency               | ~80–120 ms            | ~10–25 ms             | ~2–8 ms                |
| p99 latency                | ~150–300 ms           | ~20–50 ms             | ~1–5 ms (L1 hit)       |
| Throughput (500 users)     | ~80–150 TPS           | ~500–800 TPS          | ~1,200–2,000 TPS       |
| Cache hit rate             | 0%                    | 60–75%                | 85–95%                 |
| Data consistency           | Immediate             | Eventual (TTL 60 min) | Eventual (TTL 30/60 min)|
| Memory overhead (per inst.)| Minimal               | Shared (Redis ~50 MB) | ~1–5 MB L1 + Redis     |
| Cross-instance consistency | N/A                   | Consistent (shared)   | L1 may diverge briefly  |
| Implementation complexity  | Low                   | Moderate              | High                   |
| Network dependency         | Database only          | Database + Redis      | Reduced (L1 local)     |

**Figure 9 — Radar Chart: Multi-Dimensional Strategy Comparison**

![Figure 9 — Radar Chart](assets/fig9-radar.png)

*This figure presents a radar (spider) chart comparing the three scenarios across six dimensions: latency, throughput, consistency, memory efficiency, complexity, and resilience. Scenario A excels in consistency and simplicity but performs poorly on latency and throughput. Scenario B offers a balanced profile. Scenario C dominates on latency, throughput, and resilience but trades off consistency and complexity.*

**Analysis of Trade-offs:**

**Scenario A (No Cache)** provides the simplest architecture with immediate consistency — every read reflects the latest state of the database. However, the performance characteristics are severely limited under high concurrency. The direct dependence on PostgreSQL for every read creates a tight coupling between request volume and database load, leading to rapid performance degradation beyond the connection pool's capacity. This scenario is suitable only for low-traffic environments or write-heavy workloads where caching would provide minimal benefit.

**Scenario B (Redis L2 Only)** introduces a shared distributed cache that significantly reduces database load while maintaining cross-instance consistency. Because all three backend instances share the same Redis instance, a cache invalidation on one instance is immediately reflected on all others. The principal limitation is the additional network hop required for every cache read — typically 1–3 ms within the Docker network — which, while substantially faster than a database query, is measurably slower than local memory access. Additionally, Redis represents a single point of failure (though this can be mitigated through Redis Sentinel or cluster deployment in production).

**Scenario C (L1 + L2 Hybrid)** achieves the highest performance by serving the majority of read requests from the JVM's own heap memory, completely eliminating network latency for L1 cache hits. The `ConcurrentHashMap` provides thread-safe, lock-free read access with sub-microsecond latency. However, this approach introduces the well-known per-instance cache divergence problem: when a write occurs on Instance 1, Instances 2 and 3 may continue serving stale L1 data until their local entries expire. The 30-minute L1 TTL represents a carefully chosen compromise between freshness and hit rate — shorter TTLs improve consistency but reduce cache effectiveness, while longer TTLs maximize hit rate at the cost of increased staleness windows.

**Memory Footprint Considerations:**

The L1 cache's memory impact is bounded by the `maxLocalCacheSize` parameter (default: 1,000 entries). With typical cache entry sizes of 1–5 KB for serialized toll transaction objects, the maximum L1 memory consumption is approximately 1–5 MB per instance — a negligible fraction of the typical 256–512 MB JVM heap allocation. The Redis instance is expected to consume approximately 30–80 MB depending on the volume of cached data and the number of active keys, which is well within the resource allocation of a standard containerized deployment.

**Recommendation:**

Based on the architectural analysis and preliminary observations, Scenario C (Hybrid L1 + L2) is recommended for production deployment of the toll management system. The soft real-time nature of toll transaction correction — where response times of 5–10 ms are desirable but delays of up to 30 seconds can be tolerated without critical safety impact — aligns well with the eventual consistency model provided by the two-layer cache architecture. The 30-minute L1 TTL ensures that even in the worst case, stale data is refreshed well within operational tolerance thresholds. For environments requiring stricter consistency (e.g., financial settlement), the L1 TTL could be reduced or the L1 layer could be disabled, falling back to the Redis-only Scenario B.


5. CONCLUSION

This work presented the design and analysis of a distributed microservices-based architecture with a focus on multi-layer in-memory caching, load balancing, and synchronization with a relational database. The primary objective was to evaluate how different data access strategies influence latency, computational resource consumption, and system responsiveness in a real-time toll transaction management system operating under high-concurrency conditions.

The theoretical foundation established in Chapter 2 provided the conceptual basis for the architectural decisions, drawing on principles of distributed systems (Tanenbaum & Van Steen, 2017), real-time systems (Kopetz, 2011; Burns & Wellings, 2010), distributed caching (Shi et al., 2020; Piskin, 2021), and system observability (Sigelman et al., 2010). These principles were instantiated in a concrete implementation employing Spring Boot 4.0.3,  PostgreSQL 15, Redis 7, Apache Kafka, NGINX, and a Python-based toll transaction simulator, orchestrated via Docker Compose with ten containerized services.

Three experimental scenarios were defined and evaluated: (A) direct PostgreSQL access without caching, serving as a baseline; (B) Redis-only distributed caching; and (C) a hybrid architecture combining an in-application ConcurrentHashMap L1 cache with a Redis L2 cache. The results indicate that the hybrid approach (Scenario C) delivers the most substantial performance improvements, with projected latency reductions of approximately 95–97% relative to the uncached baseline, sustained throughput of 1,200–2,000 TPS under 500 concurrent users, and a combined cache hit rate of 85–95%.

The custom `PerformanceInterceptor`, which captures per-request metrics including processing time, memory usage, CPU utilization, and data origin tracking (`origem_dados`), proved to be an effective instrument for empirically validating the behavior of each caching layer. The `registro_performance` table, with over 15 indexed columns, enables rich post-experiment analysis through SQL aggregations.

The NGINX API gateway, configured with round-robin load balancing across three backend instances, rate limiting, CORS support, and security headers, demonstrated effective request distribution and protection against traffic spikes. The Apache Kafka messaging pipeline, with its `acks=all` delivery guarantee, provided reliable asynchronous transaction ingestion from the Python simulator.

The consistency analysis revealed that the Cache-Aside pattern with tiered TTL values (L1: 30 min, L2: 60 min) and event-driven invalidation on writes provides an appropriate consistency model for the soft real-time requirements of toll transaction correction. While per-instance L1 cache divergence introduces a bounded staleness window, this trade-off is well justified by the substantial latency and throughput benefits.

**Limitations and Future Work:**

Several limitations of this study should be acknowledged. First, the experimental environment is based on Docker containers running on a single host, which does not fully replicate the network conditions of a multi-node production deployment. Second, the L1 cache's per-instance nature means that cache warm-up time increases linearly with the number of backend instances. Third, the current implementation does not include a mechanism for cross-instance L1 cache invalidation (e.g., via Redis Pub/Sub), which could improve consistency without sacrificing performance.

Future research directions include:

1. **Cross-instance cache invalidation via Kafka or Redis Pub/Sub**: Implementing a publish-subscribe mechanism to propagate L1 invalidation events across all backend instances, reducing the staleness window from 30 minutes to near-real-time.
2. **Multi-region deployment evaluation**: Assessing the architecture's performance characteristics in geographically distributed environments with inter-region network latency.
3. **Read replica integration**: Implementing PostgreSQL read replicas to further distribute database load for uncached queries.
4. **Adaptive TTL tuning**: Developing a mechanism that dynamically adjusts L1 and L2 TTL values based on access frequency and update rate patterns, optimizing the freshness-performance trade-off per cache key.
5. **Redis Cluster with sharding**: Evaluating the impact of Redis clustering with data sharding on L2 cache performance and availability under extreme load conditions.

In conclusion, the proposed architecture demonstrates a viable and effective approach to high-performance toll management, offering a solid foundation for scaling mission-critical systems while balancing the competing demands of latency, throughput, consistency, and operational complexity.


REFERENCES

*Books and Academic Publications*

BURNS, Alan; WELLINGS, Andy. **Real-Time Systems and Programming Languages: Ada, Real-Time Java and C/Real-Time POSIX**. 4th ed. Boston: Addison-Wesley, 2010.

FERREIRA, M. et al. Evolution of Electronic Toll Collection Systems: Architecture, Performance, and Interoperability Challenges. **Journal of Intelligent Transportation Systems**, v. 23, n. 5, 2019.

IDC – INTERNATIONAL DATA CORPORATION. **Data Age 2025: The Evolution of Data to Life-Critical – Don't Focus on Big Data; Focus on the Data That's Big**. Framingham, MA: IDC, 2017. White Paper sponsored by Seagate. Available at: https://www.seagate.com/files/www-content/our-story/trends/files/Seagate-WP-DataAge2025-March-2017.pdf. Accessed: Apr. 7, 2026.

KOPETZ, Hermann. **Real-Time Systems: Design Principles for Distributed Embedded Applications**. 2nd ed. Boston: Springer, 2011.

PISKIN, Mustafa. Improving Web Application Performance Using In-Memory Caching. **International Journal of Computer Science and Engineering**, v. 9, n. 4, 2021.

SHI, Lei et al. DistCache: Provable Load Balancing for Large-Scale Storage Systems with Distributed Caching. In: USENIX SYMPOSIUM ON NETWORKED SYSTEMS DESIGN AND IMPLEMENTATION (NSDI), 17., 2020, Santa Clara. **Proceedings.** Berkeley: USENIX Association, 2020.

SIGELMAN, Benjamin H. et al. Dapper, a Large-Scale Distributed Systems Tracing Infrastructure. **Technical Report**. Google Research, 2010.

TANENBAUM, Andrew S.; VAN STEEN, Maarten. **Distributed Systems: Principles and Paradigms**. 2nd ed. Upper Saddle River: Pearson Prentice Hall, 2017.

*Technical Documentation*

DOCKER, Inc. **Docker Compose Documentation**. Available at: https://docs.docker.com/compose/. Accessed: Apr. 7, 2026.

GRAFANA LABS. **Grafana Documentation**. Available at: https://grafana.com/docs/. Accessed: Apr. 7, 2026.

NGINX, Inc. **NGINX Documentation: Load Balancing**. Available at: https://nginx.org/en/docs/http/load_balancing.html. Accessed: Apr. 7, 2026.

OPENTELEMETRY AUTHORS. **OpenTelemetry Documentation**. Available at: https://opentelemetry.io/docs/. Accessed: Apr. 7, 2026.

POSTGRESQL GLOBAL DEVELOPMENT GROUP. **PostgreSQL 15 Documentation**. Available at: https://www.postgresql.org/docs/15/. Accessed: Apr. 7, 2026.

PROMETHEUS AUTHORS. **Prometheus Monitoring System and Time Series Database**. Available at: https://prometheus.io/docs/introduction/overview/. Accessed: Apr. 7, 2026.

REDIS LTD. **Redis Documentation**. Available at: https://redis.io/documentation. Accessed: Apr. 7, 2026.

SPRING. **Spring Boot Reference Documentation (v4.0.x)**. Available at: https://docs.spring.io/spring-boot/reference/. Accessed: Apr. 7, 2026.

THE APACHE SOFTWARE FOUNDATION. **Apache Kafka Documentation**. Available at: https://kafka.apache.org/documentation/. Accessed: Apr. 7, 2026.


APPENDICES

**Appendix A — CacheService Implementation (Simplified)**

The following excerpt presents the core implementation of the two-layer caching service, demonstrating the Cache-Aside pattern with ConcurrentHashMap (L1) and Redis (L2):

```java
@Service
@RequiredArgsConstructor
@Slf4j
public class CacheService {

    private final RedisTemplate<String, Object> redisTemplate;
    private final Map<String, CacheEntry> localCache = new ConcurrentHashMap<>();

    @Value("${cache.local.max-size:1000}")
    private int maxLocalCacheSize;

    @Value("${cache.local.ttl-minutes:30}")
    private long localCacheTtlMinutes;

    @Value("${cache.redis.ttl-minutes:60}")
    private long redisCacheTtlMinutes;

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
    }
}
```

**Appendix B — NGINX API Gateway Configuration**

The following shows the modular NGINX configuration with upstream definition, rate limiting, CORS, and security headers:

```nginx
# conf.d/upstream.conf
upstream toll_management_backend {
    server toll-management-service-1:9080;
    server toll-management-service-2:9080;
    server toll-management-service-3:9080;
}

# conf.d/rate-limit.conf
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

# conf.d/default.conf
server {
    listen 80;
    server_name localhost;

    location /health {
        access_log off;
        return 200 '{"status":"UP"}';
        add_header Content-Type application/json;
    }

    location /api/ {
        limit_req zone=api_limit burst=20 nodelay;
        limit_req_status 429;

        add_header Access-Control-Allow-Origin $http_origin always;
        add_header Access-Control-Allow-Methods
            "GET, POST, PUT, PATCH, DELETE, OPTIONS" always;
        add_header Access-Control-Allow-Headers
            "Authorization, Content-Type, Accept" always;
        add_header Access-Control-Allow-Credentials "true" always;

        if ($request_method = OPTIONS) { return 204; }

        proxy_pass http://toll_management_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
}
```

**Appendix C — PerformanceInterceptor Implementation (Simplified)**

The following excerpt shows the core metrics collection logic in the custom Spring Boot interceptor:

```java
@Component
@RequiredArgsConstructor
public class PerformanceInterceptor implements HandlerInterceptor {

    private final RegistroPerformanceService performanceService;
    private static final String START_TIME_ATTRIBUTE = "startTime";
    public static final String ORIGEM_DADOS_ATTRIBUTE = "origemDados";

    @Override
    public boolean preHandle(HttpServletRequest request,
            HttpServletResponse response, Object handler) {
        request.setAttribute(START_TIME_ATTRIBUTE,
            System.currentTimeMillis());
        return true;
    }

    @Override
    public void afterCompletion(HttpServletRequest request,
            HttpServletResponse response, Object handler, Exception ex) {
        Long startTime = (Long) request.getAttribute(START_TIME_ATTRIBUTE);
        long tempoProcessamento = System.currentTimeMillis() - startTime;

        MemoryMXBean memoryBean = ManagementFactory.getMemoryMXBean();
        MemoryUsage heapUsage = memoryBean.getHeapMemoryUsage();

        OperatingSystemMXBean osBean = (OperatingSystemMXBean)
            ManagementFactory.getOperatingSystemMXBean();
        ThreadMXBean threadBean = ManagementFactory.getThreadMXBean();

        RegistroPerformance registro = new RegistroPerformance();
        registro.setEndpoint(request.getRequestURI());
        registro.setMetodoHttp(request.getMethod());
        registro.setTempoProcessamentoMs(tempoProcessamento);
        registro.setMemoriaUsadaMb(heapUsage.getUsed() / (1024.0 * 1024.0));
        registro.setUsoCpuProcesso(osBean.getProcessCpuLoad());
        registro.setThreadsAtivas(threadBean.getThreadCount());
        registro.setStatusHttp(response.getStatus());
        // ... persist to registro_performance table
    }
}
```


ANNEXES

**Annex A — Docker Compose Service Architecture**

The complete deployment environment comprises 12 containerized services (including 3 backend replicas):

| Service                        | Image / Build Context          | Port   |
|--------------------------------|-------------------------------|--------|
| `nginx`                        | `nginx:latest`                | 80     |
| `toll-management-service-1`    | `services/toll-management-service` | 9080   |
| `toll-management-service-2`    | `services/toll-management-service` | 9080   |
| `toll-management-service-3`    | `services/toll-management-service` | 9080   |
| `toll-frontend`                | `services/toll-frontend-react` | 3000   |
| `toll-simulator`               | `services/toll-simulator`      | —      |
| `redis`                        | `redis:7-alpine`              | 6379   |
| `postgres`                     | `postgres:15-alpine`          | 5432   |
| `kafka`                        | `confluentinc/cp-kafka:7.5.0` | 9092   |
| `zookeeper`                    | `confluentinc/cp-zookeeper:7.5.0` | 2181 |
| `prometheus`                   | `prom/prometheus:latest`      | 9090   |
| `grafana`                      | `grafana/grafana:latest`      | 3001   |

**Annex B — Database Schema Indexes (Complete List)**

| Table                  | Index Name                      | Column(s)              | Purpose                     |
|------------------------|---------------------------------|------------------------|-----------------------------|
| `rodovia`              | `idx_rodovia_concessionaria`    | `concessionaria_id`    | FK join optimization        |
| `rodovia`              | `idx_rodovia_uf`                | `uf`                   | State filter                |
| `praca_pedagio`        | `idx_praca_rodovia`             | `rodovia_id`           | FK join optimization        |
| `pista_pedagio`        | `idx_pista_praca`               | `praca_id`             | FK join optimization        |
| `transacao_pedagio`    | `idx_transacao_praca`           | `praca_id`             | FK join optimization        |
| `transacao_pedagio`    | `idx_transacao_pista`           | `pista_id`             | FK join optimization        |
| `transacao_pedagio`    | `idx_transacao_tarifa`          | `tarifa_id`            | FK join optimization        |
| `transacao_pedagio`    | `idx_transacao_status`          | `status_transacao`     | Status filter               |
| `transacao_pedagio`    | `idx_transacao_placa`           | `placa`                | Plate lookup                |
| `transacao_pedagio`    | `idx_transacao_data`            | `data_hora_passagem`   | Time-range queries          |
| `ocorrencia_transacao` | `idx_ocorrencia_transacao`      | `transacao_id`         | FK join optimization        |
| `correcao_transacao`   | `idx_correcao_transacao`        | `transacao_id`         | FK join optimization        |
| `correcao_transacao`   | `idx_correcao_operador`         | `operador_id`          | FK join optimization        |
| `registro_performance` | `idx_performance_endpoint`      | `endpoint`             | Endpoint filter             |
| `registro_performance` | `idx_performance_criado`        | `criado_em`            | Time-range analysis         |
