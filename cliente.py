"""
Cliente que manda una tarea al servidor y muestra el resultado.

Uso:
    python cliente.py sumar 1 2 3
    python cliente.py esperar 2
    python cliente.py reversa hola
"""
import json
import socket
import sys

HOST = "127.0.0.1"
PUERTO = 9100


def armar_tarea(argv):
    operacion = argv[1]
    if operacion == "sumar":
        datos = [float(x) for x in argv[2:]]
    elif operacion == "esperar":
        datos = float(argv[2])
    elif operacion == "reversa":
        datos = argv[2]
    else:
        raise ValueError(f"Operación desconocida: {operacion}")
    return {"operacion": operacion, "datos": datos}


def main():
    if len(sys.argv) < 3:
        print(f"Uso: python {sys.argv[0]} <sumar|esperar|reversa> <datos...>")
        sys.exit(1)

    tarea = armar_tarea(sys.argv)

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as cliente:
            cliente.connect((HOST, PUERTO))
            cliente.sendall(json.dumps(tarea).encode("utf-8"))
            respuesta = cliente.recv(4096)
            print(json.loads(respuesta.decode("utf-8")))
    except ConnectionRefusedError:
        print("[cliente] No se pudo conectar: ¿está el servidor corriendo?")
        sys.exit(1)


if __name__ == "__main__":
    main()
