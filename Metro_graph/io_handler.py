# Título: Persistencia de datos de MetroGraph
# Nombre del autor: Emiliano Villalobos Luevano
# Fecha: 15 de noviembre de 2026
# Descripción: Validación, lectura y escritura de conexiones.

"""Validación y persistencia de conexiones en archivos CSV."""

import os
from typing import Callable
import tempfile
import csv
import math
from pathlib import Path

from grafo import Grafo


ARCHIVO_CSV = Path(__file__).resolve().parent / "nodos.csv"
ENCABEZADOS = ["Origen", "Destino", "Peso"]


def validar_nodo(nombre: str) -> str:
    '''Valida que el nombre del nodo no esté vacío'''
    nombre = nombre.strip().upper()

    if not nombre:
        raise ValueError("El nombre del nodo no puede estar vacío")

    return nombre


def validar_peso(entrada: str) -> float:
    '''Convierte y valida un peso numérico no negativo'''
    if not entrada.strip():
        raise ValueError("El peso no puede estar vacío")

    peso = float(entrada)

    if not math.isfinite(peso):
        raise ValueError("El peso debe ser un número finito")

    if peso < 0:
        raise ValueError("El peso no puede ser negativo")

    return peso


def clave_conexion(origen: str, destino: str) -> tuple[str, str]:
    '''Genera una clave única para una conexión bidireccional'''
    return tuple(sorted((origen, destino)))


def obtener_conexiones(
    grafo: Grafo,
) -> dict[tuple[str, str], float]:
    """Obtiene las conexiones únicas del grafo en memoria."""
    conexiones: dict[tuple[str, str], float] = {}

    for origen, nodo in grafo.nodos.items():
        for destino, peso in nodo.vecinos.items():
            clave = clave_conexion(origen, destino)
            conexiones[clave] = peso

    return conexiones


def solicitar_nodo(mensaje: str) -> str:
    '''Solicita un nombre de nodo hasta recibir uno válido'''
    while True:
        try:
            return validar_nodo(input(mensaje))
        except ValueError as error:
            print(f"Validación: {error}")


def solicitar_peso() -> float:
    '''Solicita un peso hasta recibir un número válido'''
    while True:
        try:
            return validar_peso(input("Peso de la conexión: "))
        except ValueError as error:
            print(f"Validación: {error}")


def leer_conexiones(
    ruta: Path = ARCHIVO_CSV,
) -> dict[tuple[str, str], float]:
    '''Lee conexiones válidas y elimina duplicados en memoria'''
    conexiones: dict[tuple[str, str], float] = {}

    with open(ruta, "r", newline="", encoding="utf-8") as archivo:
        lector = csv.DictReader(archivo)

        if lector.fieldnames != ENCABEZADOS:
            raise ValueError("El CSV tiene encabezados incorrectos")

        for numero_fila, fila in enumerate(lector, start=2):
            try:
                origen = validar_nodo(fila["Origen"] or "")
                destino = validar_nodo(fila["Destino"] or "")
                peso = validar_peso(fila["Peso"] or "")

                if origen == destino:
                    raise ValueError(
                        "El origen y destino deben ser distintos"
                    )

                clave = clave_conexion(origen, destino)
                conexiones[clave] = peso

            except (ValueError, KeyError, TypeError) as error:
                print(f"Fila {numero_fila} omitida: {error}")

    return conexiones


def guardar_conexion(
    origen: str,
    destino: str,
    peso: float,
    ruta: Path = ARCHIVO_CSV,
    grafo: Grafo | None = None,
) -> bool:
    '''Guarda una conexión nueva o actualiza su peso en el CSV'''
    origen = validar_nodo(origen)
    destino = validar_nodo(destino)
    peso = validar_peso(str(peso))

    if origen == destino:
        raise ValueError(
            "El origen y destino deben ser distintos"
        )

    clave = clave_conexion(origen, destino)

    if not ruta.exists() or ruta.stat().st_size == 0:
        with open(ruta, "a", newline="", encoding="utf-8") as archivo:
            escritor = csv.writer(archivo)
            escritor.writerow(ENCABEZADOS)
            escritor.writerow([origen, destino, peso])
        return False

    if grafo is None:
        conexiones = leer_conexiones(ruta)
    else:
        conexiones = obtener_conexiones(grafo)

    if clave not in conexiones:
        with open(ruta, "a", newline="", encoding="utf-8") as archivo:
            escritor = csv.writer(archivo)
            escritor.writerow([origen, destino, peso])
        return False

    conexiones[clave] = peso
    temporal: str | None = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            newline="",
            encoding="utf-8",
            dir=ruta.parent,
            prefix=".nodos_",
            suffix=".csv",
            delete=False,
        ) as archivo:
            temporal = archivo.name
            escritor = csv.writer(archivo)
            escritor.writerow(ENCABEZADOS)

            for (nodo_a, nodo_b), valor in conexiones.items():
                escritor.writerow([nodo_a, nodo_b, valor])

        os.replace(temporal, ruta)

    finally:
        if temporal is not None and os.path.exists(temporal):
            os.unlink(temporal)

    return True


def cargar_grafo(
    ruta: Path = ARCHIVO_CSV,
    notificar: Callable[[str], None] = print,
    estricto: bool = False,
) -> Grafo:
    """Construye un grafo usando las conexiones válidas del CSV."""
    grafo = Grafo()

    try:
        with open(ruta, "r", newline="", encoding="utf-8") as archivo:
            lector = csv.DictReader(archivo)

            if lector.fieldnames != ENCABEZADOS:
                raise KeyError(
                    "El CSV tiene encabezados incorrectos"
                )

            for numero_fila, fila in enumerate(lector, start=2):
                try:
                    origen = validar_nodo(fila["Origen"] or "")
                    destino = validar_nodo(fila["Destino"] or "")
                    peso = validar_peso(fila["Peso"] or "")

                    grafo.agregar_conexion(origen, destino, peso)

                except (ValueError, KeyError, TypeError) as error:
                    notificar(
                        f"Fila {numero_fila} omitida: {error}"
                    )

    except FileNotFoundError:
        notificar("No existe nodos.csv. El grafo inicia vacío.")

    except KeyError as error:
        if estricto:
            raise
        notificar(f"Error en los encabezados: {error}")

    except (OSError, UnicodeError, csv.Error) as error:
        if estricto:
            raise
        notificar(f"Error al leer el CSV: {error}")

    return grafo
