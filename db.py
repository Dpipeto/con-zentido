"""Pequeño ayudante para trabajar con SQLite sin dependencias extra."""
import os
import sqlite3
from pathlib import Path
from flask import g

# La ruta de la base de datos se puede configurar con la variable de entorno
# DATABASE_PATH. En Render apuntará al disco persistente (p. ej.
# /var/data/con_zentido.db); en local, si no se define, usa un archivo aquí al lado.
DB_PATH = Path(os.environ.get("DATABASE_PATH") or (Path(__file__).parent / "con_zentido.db"))
SCHEMA_PATH = Path(__file__).parent / "schema.sql"

# Nos aseguramos de que la carpeta donde vive la base de datos exista.
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def get_db():
    """Devuelve una conexión reutilizable durante la petición actual."""
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row              # acceder a columnas por nombre
        # WAL mejora la concurrencia (varias lecturas + una escritura a la vez);
        # busy_timeout evita errores de "database is locked" bajo carga ligera.
        g.db.execute("PRAGMA journal_mode = WAL")
        g.db.execute("PRAGMA busy_timeout = 5000")
        g.db.execute("PRAGMA foreign_keys = ON")    # respetar ON DELETE CASCADE
    return g.db


def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def query(sql, args=(), one=False):
    cur = get_db().execute(sql, args)
    rows = cur.fetchall()
    cur.close()
    return (rows[0] if rows else None) if one else rows


def execute(sql, args=()):
    db = get_db()
    cur = db.execute(sql, args)
    db.commit()
    last_id = cur.lastrowid
    cur.close()
    return last_id


def _asegurar_columna(db, tabla, columna, definicion):
    """Agrega una columna a una tabla existente si todavía no está.

    Sirve para actualizar bases de datos creadas con versiones anteriores
    sin perder los datos que ya tengan.
    """
    columnas = [fila["name"] for fila in db.execute(f"PRAGMA table_info({tabla})")]
    if columna not in columnas:
        db.execute(f"ALTER TABLE {tabla} ADD COLUMN {columna} {definicion}")


def init_db(app):
    """Crea las tablas si no existen y guarda valores por defecto."""
    with app.app_context():
        db = get_db()
        db.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        # Migraciones suaves para bases de datos antiguas.
        _asegurar_columna(db, "posts", "me_gusta", "INTEGER NOT NULL DEFAULT 0")
        # Valores por defecto del apartado "del día"
        defaults = {
            "cancion_titulo": "Breathin — Ariana Grande",
            "cancion_enlace": "https://www.youtube.com/results?search_query=breathin+ariana+grande",
            "cancion_nota": "Para los días en que respirar cuesta un poquito más.",
            "tema_debate": "¿La identidad se descubre o se construye?",
            "mensaje": "No tienes que tenerlo todo resuelto hoy. Avanzar despacio también es avanzar.",
            "mensaje_tipo": "Mensaje motivacional",
        }
        for clave, valor in defaults.items():
            db.execute(
                "INSERT OR IGNORE INTO diario (clave, valor) VALUES (?, ?)",
                (clave, valor),
            )
        db.commit()
        close_db()


def get_diario():
    """Devuelve el contenido 'del día' como diccionario."""
    filas = query("SELECT clave, valor FROM diario")
    return {fila["clave"]: fila["valor"] for fila in filas}
