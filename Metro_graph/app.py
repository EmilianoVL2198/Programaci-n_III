# Título: MetroGraph - Streamlit
# Nombre: Emiliano Villalobos Luevano
# Fecha: 15 de noviembre de 2026
# Descripción: Interfaz gráfica para gestionar redes de transporte

"""Interfaz web de MetroGraph con Streamlit."""

import math

import matplotlib.pyplot as plt
import networkx as nx
import streamlit as st

from io_handler import cargar_grafo, guardar_conexion

st.set_page_config(
    page_title="MetroGraph",
    page_icon="🚇",
    layout="wide",
)

st.title("MetroGraph")
st.caption("Diseña, conecta y optimiza tu propia red.")

st.sidebar.header("Navegación")

seccion = st.sidebar.radio(
    "Selecciona una sección",
    ["Constructor", "Planificador", "Explorador"],
)

grafo = cargar_grafo()


def dibujar_grafo(camino: list[str] | None = None) -> None:
    red = nx.Graph()

    for nombre, nodo in grafo.nodos.items():
        red.add_node(nombre)

        for vecino, peso in nodo.vecinos.items():
            red.add_edge(nombre, vecino, weight=peso)

    if red.number_of_nodes() == 0:
        st.info("Todavía no hay estaciones para visualizar.")
        return

    posiciones = nx.spring_layout(red, seed=42)

    fig, ax = plt.subplots(figsize=(11, 6))

    fig.patch.set_facecolor("#0e1726")
    ax.set_facecolor("#0e1726")

    nx.draw_networkx_edges(
        red,
        posiciones,
        ax=ax,
        edge_color="#64748b",
        width=2,
        alpha=0.7,
    )

    if camino and len(camino) > 1:
        aristas_camino = list(zip(camino[:-1], camino[1:]))

        nx.draw_networkx_edges(
            red,
            posiciones,
            edgelist=aristas_camino,
            edge_color="#22c55e",
            width=4,
            ax=ax,
        )

    nx.draw_networkx_nodes(
        red,
        posiciones,
        ax=ax,
        node_color="#38bdf8",
        node_size=1400,
        edgecolors="#ffffff",
        linewidths=1.5,
    )

    nx.draw_networkx_labels(
        red,
        posiciones,
        ax=ax,
        font_size=10,
        font_weight="bold",
        font_color="#0f172a",
    )

    etiquetas = nx.get_edge_attributes(red, "weight")

    nx.draw_networkx_edge_labels(
        red,
        posiciones,
        edge_labels=etiquetas,
        ax=ax,
        font_size=10,
        font_color="#ffffff",
        bbox={
            "facecolor": "#334155",
            "edgecolor": "none",
            "alpha": 0.9,
        },
    )

    ax.axis("off")
    fig.tight_layout()

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
            actualizada = guardar_conexion(origen, destino, peso)

            if actualizada:
                st.success("Conexión actualizada correctamente.")
            else:
                st.success("Nueva conexión registrada.")

            st.rerun()

        except (ValueError, OSError) as error:
            st.error(str(error))

    dibujar_grafo()


elif seccion == "Planificador":
    st.header("Planificador de rutas")

    estaciones = sorted(grafo.nodos.keys())

    if len(estaciones) < 2:
        st.warning("Registra al menos dos estaciones.")
    else:
        origen = st.selectbox("Origen", estaciones)

        destino = st.selectbox(
            "Destino",
            estaciones,
            index=1,
        )

        if st.button("Calcular ruta"):
            distancia, camino = grafo.dijkstra(origen, destino)

            if math.isinf(distancia):
                st.warning("No existe una ruta disponible.")
            else:
                st.success("Ruta óptima encontrada.")
                st.write(" → ".join(camino))
                st.metric("Peso total", f"{distancia:g}")

                dibujar_grafo(camino)


elif seccion == "Explorador":
    st.header("Explorador de la red")

    st.metric("Estaciones", len(grafo.nodos))

    conexiones = sum(
        len(nodo.vecinos)
        for nodo in grafo.nodos.values()
    ) // 2

    st.metric("Conexiones", conexiones)

    dibujar_grafo()
