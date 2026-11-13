# PFO3: rediseño como sistema distribuido (sockets + pool de hilos)

> ⚠️ Punto de partida para practicar (PFO3 de Programación sobre Redes),
> no una entrega. El diagrama completo está en [DIAGRAMA.md](DIAGRAMA.md)
> — ahí también se explica qué partes son infraestructura real (Nginx,
> RabbitMQ, Postgres) y cuáles demuestra el código de este repo.

Un servidor recibe tareas por socket y, en vez de atenderlas una por una,
se las entrega a un `ThreadPoolExecutor` (los "workers"). Mientras un
worker está ocupado con una tarea lenta, el servidor sigue aceptando
conexiones nuevas y repartiéndolas a otro worker libre.

## Cómo correrlo

En una terminal:

```bash
python servidor.py
```

En otra:

```bash
python cliente.py sumar 1 2 3
python cliente.py esperar 2
python cliente.py reversa "hola mundo"
```

## Protocolo

Una línea de JSON por mensaje.

```json
Pedido:    {"operacion": "sumar", "datos": [1, 2, 3]}
Respuesta: {"resultado": 6, "atendido_por": "ThreadPoolExecutor-0_1"}
```

Operaciones: `sumar` (lista de números), `esperar` (duerme N segundos —
sirve para probar que la concurrencia funciona), `reversa` (invierte un
texto).

## Prueba de concurrencia (13/11/2026)

Tres clientes pidieron `esperar 2` **al mismo tiempo**:

```
{'resultado': 'esperé 2.0 segundos', 'atendido_por': 'ThreadPoolExecutor-0_0'}
{'resultado': 'esperé 2.0 segundos', 'atendido_por': 'ThreadPoolExecutor-0_1'}
{'resultado': 'esperé 2.0 segundos', 'atendido_por': 'ThreadPoolExecutor-0_2'}
Tiempo total: 3.28 segundos
```

Los atendieron **tres workers distintos** (`0_0`, `0_1`, `0_2`) y el total
dio ~3.3s, no los ~6s que tardaría si el servidor las procesara una
detrás de la otra. Eso confirma que el pool reparte el trabajo de verdad.

## Estructura

- `DIAGRAMA.md` — arquitectura completa (clientes, balanceador, workers,
  cola de mensajes, almacenamiento) y qué de eso demuestra el código.
- `servidor.py` — acepta conexiones y reparte cada tarea a un
  `ThreadPoolExecutor`.
- `cliente.py` — manda una tarea y muestra el resultado.
