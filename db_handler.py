import sqlite3

# Conectar
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Crear una tabla simple

cursor.execute('''
CREATE TABLE IF NOT EXISTS tramos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    origen TEXT NOT NULL,
    destino TEXT NOT NULL,
    minutos REAL NOT NULL

)''')

# Insert: Agrega 3 rutas usando marcadores de posición
rutas_iniciales = [
    ('Ciudad A', 'Ciudad B', 120.5),
    ('Ciudad B', 'Ciudad C', 90.0),
    ('Ciudad A', 'Ciudad C', 200.0)
]

cursor.executemany('''
    INSERT INTO tramos (origen, destino, minutos)
    VALUES (?, ?, ?)
''', rutas_iniciales)

conn.commit()