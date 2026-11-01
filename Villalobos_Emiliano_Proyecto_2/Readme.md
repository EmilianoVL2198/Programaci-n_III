# Proyecto 2 — Gestor de grafos con Dijkstra

## Descripción

Programa modular desarrollado en Python que permite registrar conexiones entre nodos de una red de grafos, almacenar la información en un archivo CSV y calcular la ruta más corta mediante el algoritmo de Dijkstra.

El proyecto reutiliza y adapta el algoritmo desarrollado en la Unidad 1, incorporando buenas prácticas de ingeniería de software.

## Estructura del proyecto

- `main.py`: menú interactivo y coordinación de operaciones.
- `grafo.py`: clases Nodo y Grafo e implementación de Dijkstra.
- `io_handler.py`: validación, lectura y escritura de archivos CSV.
- `nodos.csv`: almacenamiento persistente de conexiones.
- `requirements.txt`: dependencia de desarrollo Flake8.
- `README.md`: documentación del proyecto.

## Requisitos

- Python 3.10 o superior.
- Flake8 para comprobar las buenas practicas en el código.
- Todas las demás bibliotecas utilizadas son parte de la biblioteca estándar de Python y no requieren instalación adicional.

## Instalación

Instalar las dependencias:

```bash
python -m pip install -r requirements.txt
```

## Ejecución

Desde la carpeta del proyecto:

```bash
python main.py
```

## Funcionalidades

1. Registrar nuevas conexiones entre nodos.
2. Validar los datos ingresados por el usuario.
3. Guardar las conexiones en `nodos.csv`.
4. Reconstruir el grafo desde el archivo CSV.
5. Calcular la ruta más corta mediante Dijkstra.
6. Mostrar las conexiones registradas.

## Formato CSV

```csv
Origen,Destino,Peso
A,B,4
A,C,2
B,D,3
C,D,1
```

Las conexiones son bidireccionales y los pesos deben ser números finitos no negativos.

## Buenas prácticas

El código utiliza anotaciones de tipo, docstrings, manejo de excepciones específicas, administradores de contexto `with` y programación modular.

## Verificación con Flake8

```bash
python -m flake8 main.py grafo.py io_handler.py
```

## Autor

Emiliano Villalobos Luevano

## Asignatura

Programación III