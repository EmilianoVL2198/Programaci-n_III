# Título: Persistencia relacional de MetroGraph
# Nombre del autor: Emiliano Villalobos Luevano
# Fecha: 24 de noviembre de 2026
# Descripción: Gestión de la base de datos SQLite.

"""Gestión y persistencia de datos mediante SQLite."""

import sqlite3
import math
import pandas as pd

from grafos import Grafo
from pathlib import Path
from contextlib import closing


ARCHIVO_DB = Path(__file__).resolve().parent / "nodos.db"

CONSULTA_CONEXIONES = """
    SELECT
        n1.nombre AS Origen,
        n2.nombre AS Destino,
        c.peso AS Peso
    FROM conexiones AS c
    INNER JOIN nodos AS n1
        ON c.id_origen = n1.id_nodo
    INNER JOIN nodos AS n2
        ON c.id_destino = n2.id_nodo
    ORDER BY n1.nombre, n2.nombre
"""


class ErrorBaseDatos(Exception):
    """Representa un error de operación en la base de datos."""


class ErrorIntegridad(Exception):
    """Representa una violación de integridad de los datos."""


def conectar_bd() -> sqlite3.Connection:
    """Establece una conexión con la base de datos."""
    conexion = sqlite3.connect(ARCHIVO_DB)
    conexion.execute("PRAGMA foreign_keys = ON")
    return conexion


def _crear_tablas() -> None:
    """Crea las tablas necesarias para MetroGraph."""
    with closing(conectar_bd()) as conexion:
        with conexion:
            conexion.execute("""
                CREATE TABLE IF NOT EXISTS nodos (
                    id_nodo INTEGER PRIMARY KEY,
                    nombre TEXT NOT NULL UNIQUE,
                    CHECK (length(trim(nombre)) > 0)
                )
            """)

            conexion.execute("""
                CREATE TABLE IF NOT EXISTS conexiones (
                    id_conexion INTEGER PRIMARY KEY,
                    id_origen INTEGER NOT NULL,
                    id_destino INTEGER NOT NULL,
                    peso REAL NOT NULL CHECK (peso > 0),
                    FOREIGN KEY (id_origen)
                        REFERENCES nodos(id_nodo),
                    FOREIGN KEY (id_destino)
                        REFERENCES nodos(id_nodo),
                    CHECK (id_origen < id_destino),
                    UNIQUE (id_origen, id_destino)
                )
            """)


def inicializar_bd() -> None:
    """Inicializa la base de datos de forma segura."""
    try:
        _crear_tablas()

    except sqlite3.IntegrityError as error:
        raise ErrorIntegridad(str(error)) from error

    except sqlite3.DatabaseError as error:
        raise ErrorBaseDatos(str(error)) from error


def obtener_id_nodo(
    conexion: sqlite3.Connection,
    nombre: str
) -> int:
    """Obtiene el identificador de un nodo o lo crea."""
    nombre = nombre.strip().upper()

    if not nombre:
        raise ValueError("El nombre del nodo no puede estar vacío.")

    conexion.execute("""
        INSERT INTO nodos (nombre)
        VALUES (?)
        ON CONFLICT(nombre) DO NOTHING
    """, (nombre,))

    cursor = conexion.execute("""
        SELECT id_nodo
        FROM nodos
        WHERE nombre = ?
    """, (nombre,))

    resultado = cursor.fetchone()

    if resultado is None:
        raise ValueError("No fue posible obtener el nodo.")

    return int(resultado[0])


def insertar_conexion(
    conexion: sqlite3.Connection,
    origen: str,
    destino: str,
    peso: float
) -> bool:
    """Inserta una conexión o actualiza su peso existente."""
    origen = origen.strip().upper()
    destino = destino.strip().upper()

    if not origen or not destino:
        raise ValueError("Los nombres no pueden estar vacíos.")

    if origen == destino:
        raise ValueError("El origen y destino deben ser distintos.")

    if not math.isfinite(peso) or peso <= 0:
        raise ValueError("El peso debe ser positivo y finito.")

    id_origen = obtener_id_nodo(conexion, origen)
    id_destino = obtener_id_nodo(conexion, destino)

    id_origen, id_destino = sorted((id_origen, id_destino))

    cursor = conexion.execute("""
        SELECT id_conexion
        FROM conexiones
        WHERE id_origen = ? AND id_destino = ?
    """, (id_origen, id_destino))

    existe = cursor.fetchone() is not None

    conexion.execute("""
        INSERT INTO conexiones (id_origen, id_destino, peso)
        VALUES (?, ?, ?)
        ON CONFLICT(id_origen, id_destino)
        DO UPDATE SET peso = excluded.peso
    """, (id_origen, id_destino, peso))

    return existe


def guardar_conexion(
    origen: str,
    destino: str,
    peso: float
) -> bool:
    """Guarda una conexión en la base de datos."""
    try:
        with closing(conectar_bd()) as conexion:
            with conexion:
                return insertar_conexion(
                    conexion, origen, destino, peso
                )

    except sqlite3.IntegrityError as error:
        raise ErrorIntegridad(str(error)) from error

    except sqlite3.DatabaseError as error:
        raise ErrorBaseDatos(str(error)) from error


def cargar_red() -> tuple[Grafo, pd.DataFrame]:
    """Recupera el grafo y la tabla desde SQLite."""
    try:
        with closing(conectar_bd()) as conexion:
            conexion.execute("BEGIN")

            cursor = conexion.execute("""
                SELECT nombre
                FROM nodos
                ORDER BY nombre
            """)

            nodos = cursor.fetchall()

            cursor = conexion.execute(CONSULTA_CONEXIONES)
            conexiones = cursor.fetchall()

        grafo = Grafo()

        for (nombre,) in nodos:
            grafo.agregar_nodo(nombre)

        for origen, destino, peso in conexiones:
            grafo.agregar_conexion(
                origen, destino, float(peso)
            )

        tabla = pd.DataFrame(
            conexiones,
            columns=["Origen", "Destino", "Peso"],
        )

        return grafo, tabla

    except sqlite3.IntegrityError as error:
        raise ErrorIntegridad(str(error)) from error

    except sqlite3.DatabaseError as error:
        raise ErrorBaseDatos(str(error)) from error
