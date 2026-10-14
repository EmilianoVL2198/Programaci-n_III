''''
Título:Proyecto 1: Algoritmo de Dijkstra
Autor: Emiliano Villalobos Luevano
Fecha: 15/10/2026
Descripción: Este proyecto implementa el algoritmo de Dijkstra para encontrar el camino más corto en un grafo ponderado. El programa permite al usuario ingresar un grafo, especificar un nodo de inicio y calcular las distancias mínimas a todos los demás nodos.
'''

#Definimos el objeto Nodo, que representa un nodo en el grafo. Cada nodo tiene un nombre y un diccionario de vecinos con sus respectivos pesos.
class Nodo:
  def __init__(self, nombre):
    self.nombre = nombre
    self.vecinos = {}

  def agregar_vecino(self, vecino, peso):
    self.vecinos[vecino] = peso

#Definimos el objeto Grafo, que representa el grafo completo. Contiene un diccionario de nodos y métodos para agregar nodos, agregar conexiones y ejecutar el algoritmo de Dijkstra.
class Grafo:
  def __init__(self):
    self.nodos = {}

  def agregar_nodo(self, nombre):
    self.nodos[nombre] = Nodo(nombre)

  def agregar_conexion(self, origen, destino, peso):
    if origen not in self.nodos:
        self.agregar_nodo(origen)
    if destino not in self.nodos:
        self.agregar_nodo(destino)
    self.nodos[origen].agregar_vecino(destino, peso)
    self.nodos[destino].agregar_vecino(origen, peso)

  def dijkstra(self, inicio, destino):
    distancias = {}
    anteriores = {}
    visitados = set()

    for nombre in self.nodos:
        distancias[nombre] = float("inf")
        anteriores[nombre] = None

    distancias[inicio] = 0

    while len(visitados) < len(self.nodos):
        nodo_actual = None
        menor_distancia = float("inf")

        for nombre in self.nodos:
            if nombre not in visitados:
                if distancias[nombre] < menor_distancia:
                    menor_distancia = distancias[nombre]
                    nodo_actual = nombre

        if nodo_actual is None:
            break

        if nodo_actual == destino:
            break

        visitados.add(nodo_actual)

        nodo = self.nodos[nodo_actual]

        for vecino, peso in nodo.vecinos.items():
            nueva_distancia = (
                distancias[nodo_actual] + peso
            )

            if nueva_distancia < distancias[vecino]:
                distancias[vecino] = nueva_distancia
                anteriores[vecino] = nodo_actual

    camino = []
    actual = destino

    while actual is not None:
        camino.append(actual)
        actual = anteriores[actual]

    camino.reverse()

    return distancias[destino], camino


#Definimos un grafo de ejemplo y ejecutamos el algoritmo de Dijkstra para encontrar el camino más corto desde el nodo "A" hasta el nodo "F".
mi_grafo = Grafo()

mi_grafo.agregar_conexion("A", "B", 8)
mi_grafo.agregar_conexion("A", "C", 3)
mi_grafo.agregar_conexion("B", "D", 2)
mi_grafo.agregar_conexion("C", "D", 7)
mi_grafo.agregar_conexion("C", "E", 3)
mi_grafo.agregar_conexion("D", "F", 2)
mi_grafo.agregar_conexion("E", "F", 1)

distancia_total, camino_optimo = mi_grafo.dijkstra("A", "F")
print(f"Distancia total recorrida: {distancia_total}")
print(f"Camino óptimo: {camino_optimo}")