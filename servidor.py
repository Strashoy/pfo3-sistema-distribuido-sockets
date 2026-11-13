"""
Servidor TCP que reparte tareas a un pool de hilos (PFO3: rediseño como
sistema distribuido).

Cada cliente que se conecta manda una tarea en una línea de JSON. El
servidor no la procesa en el hilo principal: la entrega a un
ThreadPoolExecutor ("los workers") y sigue aceptando otras conexiones
mientras tanto. Así un cliente con una tarea lenta no bloquea a los
demás — que es justamente lo que demuestra el diagrama de arquitectura
(DIAGRAMA.md).

Protocolo (una línea de JSON por mensaje):
  Pedido:    {"operacion": "sumar", "datos": [1, 2, 3]}
  Respuesta: {"resultado": 6, "atendido_por": "ThreadPoolExecutor-0_1"}

Operaciones soportadas: "sumar" (lista de números), "esperar" (duerme N
segundos, útil para probar que la concurrencia funciona de verdad),
"reversa" (invierte un texto).
"""
import json
import socket
import threading
import time
from concurrent.futures import ThreadPoolExecutor

HOST = "0.0.0.0"
PUERTO = 9100
CANTIDAD_DE_WORKERS = 4


def procesar_tarea(operacion, datos):
    if operacion == "sumar":
        return sum(datos)
    if operacion == "esperar":
        time.sleep(float(datos))
        return f"esperé {datos} segundos"
    if operacion == "reversa":
        return datos[::-1]
    raise ValueError(f"Operación desconocida: {operacion}")


def atender_tarea(conexion, direccion):
    try:
        datos_crudos = conexion.recv(4096)
        if not datos_crudos:
            return

        pedido = json.loads(datos_crudos.decode("utf-8"))
        print(f"[worker {threading.current_thread().name}] tarea de {direccion}: {pedido}")

        try:
            resultado = procesar_tarea(pedido["operacion"], pedido["datos"])
            respuesta = {"resultado": resultado, "atendido_por": threading.current_thread().name}
        except (KeyError, ValueError) as error:
            respuesta = {"error": str(error)}

        conexion.sendall(json.dumps(respuesta).encode("utf-8"))
    except (ConnectionResetError, json.JSONDecodeError) as error:
        print(f"[worker] error atendiendo a {direccion}: {error}")
    finally:
        conexion.close()


def main():
    with ThreadPoolExecutor(max_workers=CANTIDAD_DE_WORKERS) as pool:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servidor:
            servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            servidor.bind((HOST, PUERTO))
            servidor.listen()
            print(f"[servidor] Escuchando en {HOST}:{PUERTO} con {CANTIDAD_DE_WORKERS} workers")

            while True:
                conexion, direccion = servidor.accept()
                # No procesamos acá: se lo pasamos al pool y volvemos
                # enseguida a aceptar la próxima conexión.
                pool.submit(atender_tarea, conexion, direccion)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[servidor] Apagado por el usuario")
