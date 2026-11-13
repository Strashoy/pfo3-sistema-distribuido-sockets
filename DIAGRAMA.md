# Diagrama: sistema distribuido (PFO3)

> ⚠️ Diagrama y código de práctica, no una entrega.

```mermaid
flowchart TB
    subgraph Clientes
        C1[Cliente móvil]
        C2[Cliente web]
        C3[Cliente de escritorio]
    end

    LB[Balanceador de carga<br/>Nginx / HAProxy]

    subgraph "Servidores (cada uno con su pool de hilos)"
        S1[Servidor worker 1<br/>ThreadPoolExecutor]
        S2[Servidor worker 2<br/>ThreadPoolExecutor]
    end

    MQ[(Cola de mensajes<br/>RabbitMQ)]

    subgraph Almacenamiento
        DB[(PostgreSQL)]
        OBJ[(S3 / object storage)]
    end

    C1 -- socket TCP --> LB
    C2 -- socket TCP --> LB
    C3 -- socket TCP --> LB

    LB -- reparte conexiones --> S1
    LB -- reparte conexiones --> S2

    S1 <-- tareas / resultados --> MQ
    S2 <-- tareas / resultados --> MQ

    S1 --> DB
    S2 --> DB
    S1 --> OBJ
    S2 --> OBJ
```

## Qué implementa el código de este repo (y qué no)

Esto es una práctica de sockets, no una infraestructura real. Lo que se
puede demostrar con código simple en una sola máquina:

- ✅ **Un servidor que recibe tareas por socket y las reparte a un
  `ThreadPoolExecutor`** (el "pool de hilos" de cada worker del diagrama).
  Cada conexión de cliente se atiende en un hilo del pool, así que varios
  clientes se procesan en paralelo sin bloquearse entre sí.
- ✅ **Un cliente que envía tareas y recibe resultados.**
- ❌ **Nginx/HAProxy, RabbitMQ, Postgres y S3 reales**: no tiene sentido
  levantar esa infraestructura para una práctica de una tarde. El
  diagrama de arriba muestra dónde irían si esto fuera a producción; el
  código demuestra el patrón cliente-servidor-workers que es la parte que
  pide la consigna de sockets.
