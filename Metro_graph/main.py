# Título: MetroGraph - Streamlit
# Nombre: Emiliano Villalobos Luevano
# Fecha: 15 de noviembre de 2026
# Descripción: Programa modular desarrollado en Python que permite registrar conexiones entre nodos de una red de grafos,
# almacenar la información en un archivo CSV y calcular la ruta más corta mediante el algoritmo de Dijkstra.

'''Programa principal para gestionar la red de nodos'''

import math

from grafo import Grafo
from io_handler import (
    cargar_grafo,
    guardar_conexion,
    solicitar_nodo,
    solicitar_peso,
)


def registrar_conexion(grafo: Grafo) -> None:
    '''Registra una conexión nueva o actualiza su peso'''
    print("\n=== REGISTRAR CONEXIÓN ===")

    origen = solicitar_nodo("Nodo origen: ")
    destino = solicitar_nodo("Nodo destino: ")
    peso = solicitar_peso()

    try:
        actualizada = guardar_conexion(origen, destino, peso)

        grafo.agregar_conexion(origen, destino, peso)

        if actualizada:
            print("Peso de la conexión actualizado correctamente")
        else:
            print("Nueva conexión guardada correctamente")

    except ValueError as error:
        print(f"Validación: {error}")

    except OSError as error:
        print(f"Error al guardar la conexión: {error}")


def consultar_ruta(grafo: Grafo) -> None:
    '''Calcula y muestra la ruta más corta entre dos nodos'''
    print("\n=== CONSULTAR RUTA ===")

    if not grafo.nodos:
        print("No hay conexiones registradas")
        return

    inicio = solicitar_nodo("Nodo de inicio: ")
    destino = solicitar_nodo("Nodo de destino: ")

    try:
        distancia, camino = grafo.dijkstra(inicio, destino)

        if math.isinf(distancia):
            print("No existe una ruta entre esos nodos")
            return

        print(f"Ruta más corta: {' -> '.join(camino)}")
        print(f"Peso total: {distancia}")

    except ValueError as error:
        print(f"Validación: {error}")


def mostrar_conexiones(grafo: Grafo) -> None:
    '''Muestra las conexiones registradas en el grafo'''
    print("\n=== CONEXIONES REGISTRADAS ===")

    if not grafo.nodos:
        print("No hay conexiones registradas")
        return

    mostradas: set[frozenset[str]] = set()

    for nombre, nodo in grafo.nodos.items():
        for vecino, peso in nodo.vecinos.items():
            conexion = frozenset((nombre, vecino))

            if conexion not in mostradas:
                print(f"{nombre} <-> {vecino} | Peso: {peso}")
                mostradas.add(conexion)


def menu() -> None:
    '''Ejecuta el menú principal de la aplicación'''
    grafo = cargar_grafo()

    while True:
        print("\n=== RED DE TRANSPORTE ===")
        print("1. Registrar nueva conexión")
        print("2. Consultar ruta más corta")
        print("3. Mostrar conexiones")
        print("4. Salir")

        opcion = input("\nSelecciona una opción: ").strip()

        if opcion == "1":
            registrar_conexion(grafo)

        elif opcion == "2":
            grafo = cargar_grafo()
            consultar_ruta(grafo)

        elif opcion == "3":
            grafo = cargar_grafo()
            mostrar_conexiones(grafo)

        elif opcion == "4" or opcion.lower() == "salir":
            print("Programa finalizado.")
            return

        else:
            print("Opción invalida, selecciona una opción del 1 al 4")


if __name__ == "__main__":
    menu()
