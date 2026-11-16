# Título: MetroGraph - Streamlit
# Nombre: Emiliano Villalobos Luevano
# Fecha: 15 de noviembre de 2026
# Descripción: Interfaz gráfica para gestionar redes de transporte

"""Interfaz web de MetroGraph con Streamlit."""

import math
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
import streamlit as st
import csv
from matplotlib.lines import Line2D

from io_handler import (
    cargar_grafo,
    guardar_conexion,
    obtener_conexiones,
    validar_nodo,
    validar_peso,
)

st.set_page_config(
    page_title="MetroGraph",
    page_icon="🚇",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🚇 MetroGraph")

st.caption(
    "Construye tu red. Encuentra tu camino."
)

st.divider()


# Cargar el grafo una sola vez por sesión.
if "grafo" not in st.session_state:
    avisos: list[str] = []

    try:
        st.session_state.grafo = cargar_grafo(
            notificar=avisos.append,
            estricto=True,
        )

    except (KeyError, OSError, UnicodeError, csv.Error) as error:
        st.error(f"No fue posible cargar la red: {error}")
        st.stop()

    st.session_state.avisos = avisos

grafo = st.session_state.grafo

for aviso in st.session_state.avisos:
    st.warning(aviso)


with st.sidebar:
    st.title("MetroGraph")
    st.caption("NETWORK & ROUTE PLANNER")

    st.divider()

    seccion = st.radio(
        "Navegación",
        ["Constructor", "Planificador", "Explorador"],
    )

    st.divider()

    st.subheader("Red actual")

    st.metric("Estaciones", len(grafo.nodos))

    st.metric(
        "Conexiones",
        len(obtener_conexiones(grafo)),
    )

    st.divider()

    st.caption("MetroGraph v1.0")
    st.caption("Proyecto III | Programación III")


def mostrar_tabla() -> None:
    """Muestra las conexiones del grafo mediante Pandas."""
    conexiones = obtener_conexiones(grafo)

    datos = [
        (origen, destino, peso)
        for (origen, destino), peso in conexiones.items()
    ]

    tabla = pd.DataFrame(
        datos,
        columns=["Origen", "Destino", "Peso"],
    )

    if tabla.empty:
        st.info("No hay conexiones registradas.")
    else:
        st.dataframe(
            tabla,
            hide_index=True,
        )


def dibujar_grafo(camino: list[str] | None = None) -> None:
    """Representa la red y resalta la ruta óptima."""
    red = nx.Graph()

    red.add_nodes_from(grafo.nodos)

    for (origen, destino), peso in obtener_conexiones(grafo).items():
        red.add_edge(origen, destino, weight=peso)

    if red.number_of_nodes() == 0:
        st.info("Registra conexiones para visualizar tu red.")
        return

    posiciones = nx.spring_layout(red, seed=42)

    fig, ax = plt.subplots(figsize=(10, 6))

    fig.patch.set_facecolor("#0B1120")
    ax.set_facecolor("#0B1120")

    ruta = camino or []

    aristas_ruta = {
        frozenset((ruta[i], ruta[i + 1]))
        for i in range(len(ruta) - 1)
    }

    colores_nodos = [
        "#22C55E" if nodo in ruta else "#38BDF8"
        for nodo in red.nodes()
    ]

    colores_aristas = [
        "#22C55E"
        if frozenset((origen, destino)) in aristas_ruta
        else "#475569"
        for origen, destino in red.edges()
    ]

    nx.draw_networkx_edges(
        red,
        posiciones,
        edge_color=colores_aristas,
        width=2.5,
        ax=ax,
    )

    nx.draw_networkx_nodes(
        red,
        posiciones,
        node_color=colores_nodos,
        node_size=1000,
        edgecolors="#F8FAFC",
        linewidths=1.5,
        ax=ax,
    )

    nx.draw_networkx_labels(
        red,
        posiciones,
        font_color="#0B1120",
        font_weight="bold",
        font_size=10,
        ax=ax,
    )

    pesos = nx.get_edge_attributes(red, "weight")

    nx.draw_networkx_edge_labels(
        red,
        posiciones,
        edge_labels=pesos,
        font_color="#F8FAFC",
        font_size=9,
        bbox={
            "facecolor": "#172235",
            "edgecolor": "none",
        },
        ax=ax,
    )

    leyenda = [
        Line2D([0], [0], color="#38BDF8", label="Estación"),
        Line2D([0], [0], color="#475569", label="Conexión"),
        Line2D([0], [0], color="#22C55E", label="Ruta óptima"),
    ]

    ax.legend(
        handles=leyenda,
        loc="lower center",
        facecolor="#172235",
        labelcolor="#F8FAFC",
        edgecolor="none",
        ncol=3,
    )

    ax.margins(0.2)
    ax.set_axis_off()

    st.pyplot(fig)
    plt.close(fig)


if seccion == "Constructor":
    st.header("Constructor de redes")

    with st.form("formulario_conexion"):
        origen = st.text_input("Nombre del nodo origen")
        destino = st.text_input("Nombre del nodo destino")

        peso = st.number_input(
            "Peso de la conexión",
            min_value=0.0,
            value=1.0,
            step=1.0,
        )

        enviar = st.form_submit_button("Guardar conexión")


    if enviar:
        try:
            origen = validar_nodo(origen)
            destino = validar_nodo(destino)
            peso = validar_peso(str(peso))

            # Guardar la conexión sin volver a leer el CSV.
            actualizada = guardar_conexion(
                origen,
                destino,
                peso,
                grafo=grafo,
            )

            # Actualizar el grafo almacenado en memoria.
            grafo.agregar_conexion(origen, destino, peso)

            if actualizada:
                st.success("Conexión actualizada correctamente.")
            else:
                st.success("Nueva conexión registrada.")

        except ValueError as error:
            st.error(f"Error de validación: {error}")

        except PermissionError as error:
            st.error(f"Permiso denegado: {error}")

        except OSError as error:
            st.error(f"Error al guardar la conexión: {error}")


    dibujar_grafo()


elif seccion == "Planificador":
    st.header("Planificador de rutas")

    estaciones = sorted(grafo.nodos.keys())

    if len(estaciones) < 2:
        st.warning("Registra al menos dos estaciones.")

    else:
        st.caption(
            "Estaciones disponibles: " + ", ".join(estaciones)
        )

        with st.form("formulario_ruta"):
            columna_1, columna_2 = st.columns(2)

            with columna_1:
                origen = st.text_input("Estación de origen")

            with columna_2:
                destino = st.text_input("Estación de destino")

            calcular = st.form_submit_button("Calcular ruta")

        if calcular:
            try:
                origen = validar_nodo(origen)
                destino = validar_nodo(destino)

                distancia, camino = grafo.dijkstra(
                    origen,
                    destino,
                )

                if math.isinf(distancia):
                    st.warning("No existe una ruta disponible.")

                else:
                    st.success("Ruta óptima encontrada.")
                    st.metric("Peso total", f"{distancia:g}")
                    st.write(" → ".join(camino))

                    dibujar_grafo(camino)

            except (ValueError, KeyError) as error:
                st.error(f"Error de validación: {error}")
        else:
            dibujar_grafo()


elif seccion == "Explorador":
    st.header("Explorador de la red")

    columna_1, columna_2 = st.columns(2)

    with columna_1:
        st.metric("Estaciones", len(grafo.nodos))

    with columna_2:
        st.metric(
            "Conexiones",
            len(obtener_conexiones(grafo)),
        )

    dibujar_grafo()

    st.subheader("Catálogo de conexiones")

    mostrar_tabla()

