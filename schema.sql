-- Esquema de la base de datos de "Con Zentido"

-- Publicaciones del blog
CREATE TABLE IF NOT EXISTS posts (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo      TEXT    NOT NULL,
    tema        TEXT    NOT NULL DEFAULT 'General',
    autor       TEXT    NOT NULL DEFAULT 'Anónimo',
    extracto    TEXT    NOT NULL DEFAULT '',
    cuerpo      TEXT    NOT NULL,
    me_gusta    INTEGER NOT NULL DEFAULT 0,
    creado_en   TEXT    NOT NULL DEFAULT (datetime('now', 'localtime'))
);

-- Comentarios que dejan las personas en cada publicación
CREATE TABLE IF NOT EXISTS comentarios (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id     INTEGER NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    nombre      TEXT    NOT NULL DEFAULT 'Anónimo',
    mensaje     TEXT    NOT NULL,
    creado_en   TEXT    NOT NULL DEFAULT (datetime('now', 'localtime'))
);

-- Buzón de dudas (se pueden enviar de forma anónima)
CREATE TABLE IF NOT EXISTS dudas (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre      TEXT    NOT NULL DEFAULT 'Anónimo',
    pregunta    TEXT    NOT NULL,
    respuesta   TEXT,
    creado_en   TEXT    NOT NULL DEFAULT (datetime('now', 'localtime'))
);

-- Contenido "del día": canción, tema a debatir y mensaje/fun fact.
-- Guardamos por clave para poder editarlos desde el panel.
CREATE TABLE IF NOT EXISTS diario (
    clave       TEXT PRIMARY KEY,
    valor       TEXT NOT NULL DEFAULT ''
);
