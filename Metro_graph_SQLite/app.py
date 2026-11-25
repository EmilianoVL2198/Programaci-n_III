# Título: MetroGraph - Streamlit
# Nombre del autor: Emiliano Villalobos Luevano
# Fecha: 15 de noviembre de 2026
# Descripción: Interfaz gráfica para gestionar redes de transporte

"""Interfaz web de MetroGraph con Streamlit."""

import math
import matplotlib.pyplot as plt
import networkx as nx
import streamlit as st
from matplotlib.lines import Line2D

from db_handler import (
    inicializar_bd,
    cargar_red,
    guardar_conexion,
    ErrorBaseDatos,
    ErrorIntegridad,
)


st.set_page_config(
    page_title="MetroGraph",
    page_icon="🚇",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🚇 MetroGraph")
st.caption("Construye tu red. Encuentra tu camino.")
st.divider()


def sincronizar_red() -> None:
    """Actualiza los datos de la sesión desde SQLite."""
    grafo, tabla = cargar_red()

    st.session_state.grafo = grafo
    st.session_state.tabla = tabla


# Cargar la red una sola vez por sesión.
if "grafo" not in st.session_state:
    try:
        inicializar_bd()
        sincronizar_red()

    except ErrorIntegridad as error:
        st.error(f"Error de integridad: {error}")
        st.stop()

    except ErrorBaseDatos as error:
        st.error(f"No fue posible cargar la red: {error}")
        st.stop()

    except ValueError as error:
        st.error(f"Datos inválidos en la red: {error}")
        st.stop()


grafo = st.session_state.grafo
tabla = st.session_state.tabla


with st.sidebar:
    st.header("MetroGraph")

    seccion = st.radio(
        "Navegación",
        ["Constructor", "Planificador", "Explorador"],
    )

    st.divider()

    st.metric("Estaciones", len(grafo.nodos))
    st.metric("Conexiones", len(tabla))

    st.caption("🟢 Red sincronizada con SQLite")

    st.divider()

    st.caption("MetroGraph v2.0")
    st.caption("Proyecto IV | Programación III")


def mostrar_tabla() -> None:
    """Muestra las conexiones almacenadas en la sesión."""
    if len(tabla) == 0:
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

    for nombre, nodo in grafo.nodos.items():
        for vecino, peso in nodo.vecinos.items():
            red.add_edge(nombre, vecino, weight=peso)

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

    st.caption(
        "Registra nuevas estaciones o actualiza conexiones existentes."
    )

    if "mensaje" in st.session_state:
        st.success(st.session_state.pop("mensaje"))

    with st.form(
        "formulario_conexion",
        clear_on_submit=True,
    ):
        st.caption(
            "Las conexiones son bidireccionales. Si ya existe una "
            "conexión entre dos estaciones, se actualizará su peso."
        )
        origen = st.text_input("Nombre del nodo origen")
        destino = st.text_input("Nombre del nodo destino")

        peso = st.number_input(
            "Peso de la conexión",
            min_value=0.01,
            value=1.0,
            step=0.1,
            format="%.2f",
        )

        enviar = st.form_submit_button("Guardar conexión")

    if enviar:
        try:
            actualizada = guardar_conexion(
                origen,
                destino,
                peso,
            )

        except ValueError as error:
            st.error(f"Error de validación: {error}")

        except ErrorIntegridad as error:
            st.error(f"Error de integridad: {error}")

        except ErrorBaseDatos as error:
            st.error(f"Error al guardar la conexión: {error}")

        else:
            try:
                sincronizar_red()

            except ErrorIntegridad as error:
                st.error(f"Error de integridad: {error}")
                st.warning("La conexión fue guardada en SQLite.")
                del st.session_state["grafo"]
                st.stop()

            except ErrorBaseDatos as error:
                st.error(f"Error de sincronización: {error}")
                st.warning("La conexión fue guardada en SQLite.")
                del st.session_state["grafo"]
                st.stop()

            except ValueError as error:
                st.error(f"Error en los datos: {error}")
                st.warning("La conexión fue guardada en SQLite.")
                del st.session_state["grafo"]
                st.stop()

            else:
                if actualizada:
                    mensaje = "Conexión actualizada correctamente."
                else:
                    mensaje = "Nueva conexión registrada."

                st.session_state.mensaje = mensaje
                st.rerun()

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
                origen = st.selectbox(
                    "Estación de origen",
                    estaciones,
                    index=0,
                )

            with columna_2:
                destino = st.selectbox(
                    "Estación de destino",
                    estaciones,
                    index=1,
                )

            calcular = st.form_submit_button("Calcular ruta")

        if calcular:
            try:
                if origen == destino:
                    raise ValueError(
                        "Selecciona dos estaciones distintas."
                    )

                distancia, camino = grafo.dijkstra(
                    origen,
                    destino,
                )

                if math.isinf(distancia):
                    st.warning("No existe una ruta disponible.")
                    dibujar_grafo()

                else:
                    st.success("Ruta óptima encontrada.")
                    st.metric("Peso total", f"{distancia:g}")
                    st.write(" → ".join(camino))

                    dibujar_grafo(camino)

            except ValueError as error:
                st.error(f"Error de validación: {error}")

            except KeyError as error:
                st.error(f"Estación no encontrada: {error}")

        else:
            dibujar_grafo()


elif seccion == "Explorador":
    st.header("Explorador de la red")
    st.caption(
        "Consulta las estaciones y conexiones almacenadas en SQLite."
    )

    columna_1, columna_2 = st.columns(2)

    with columna_1:
        st.metric("Estaciones", len(grafo.nodos))

    with columna_2:
        st.metric("Conexiones", len(tabla))

    dibujar_grafo()

    st.subheader("Catálogo de conexiones")

    mostrar_tabla()
    st.caption(
        "Los registros se recuperan mediante una consulta SQL JOIN."
    )
