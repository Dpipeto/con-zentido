"""
Con Zentido — un blog con sentido sobre salud mental, identidad y más.

Cómo ejecutarlo:
    pip install -r requirements.txt
    python app.py
    Luego abre http://127.0.0.1:5000 en tu navegador.
"""
import os
from functools import wraps
from flask import (
    Flask, render_template, request, redirect, url_for, flash, abort, session
)
import db

app = Flask(__name__)
# Necesaria para las sesiones y los mensajes flash. Cámbiala por algo secreto
# (idealmente con la variable de entorno CON_ZENTIDO_SECRET).
app.secret_key = os.environ.get("CON_ZENTIDO_SECRET", "cambia-esta-clave-por-una-secreta")

# Contraseña para entrar como administrador (responder dudas y editar el panel).
# Cámbiala con la variable de entorno CON_ZENTIDO_ADMIN.
ADMIN_PASSWORD = os.environ.get("CON_ZENTIDO_ADMIN", "consentido")

# Cerrar la conexión a la base de datos al final de cada petición.
app.teardown_appcontext(db.close_db)


def solo_admin(vista):
    """Protege una vista: solo entra quien haya iniciado sesión como admin."""
    @wraps(vista)
    def envoltura(*args, **kwargs):
        if not session.get("admin"):
            flash("Necesitas entrar como administrador para hacer eso.", "error")
            return redirect(url_for("login", volver=request.path))
        return vista(*args, **kwargs)
    return envoltura


@app.context_processor
def inyectar_globales():
    """Pone datos a disposición de todas las plantillas."""
    return {
        "es_admin": session.get("admin", False),
        "liked_ids": set(session.get("me_gusta", [])),
    }

# Temas disponibles (puedes ir agregando más con el tiempo).
TEMAS = [
    "Salud mental",
    "Identidad",
    "Autoestima",
    "Relaciones",
    "Emociones",
    "General",
]


@app.route("/")
def inicio():
    tema = request.args.get("tema")
    if tema and tema in TEMAS:
        posts = db.query(
            "SELECT * FROM posts WHERE tema = ? ORDER BY creado_en DESC", (tema,)
        )
    else:
        tema = None
        posts = db.query("SELECT * FROM posts ORDER BY creado_en DESC")

    dudas = db.query(
        "SELECT * FROM dudas ORDER BY creado_en DESC LIMIT 5"
    )
    return render_template(
        "index.html",
        posts=posts,
        dudas=dudas,
        diario=db.get_diario(),
        temas=TEMAS,
        tema_activo=tema,
    )


@app.route("/post/<int:post_id>")
def ver_post(post_id):
    post = db.query("SELECT * FROM posts WHERE id = ?", (post_id,), one=True)
    if post is None:
        abort(404)
    comentarios = db.query(
        "SELECT * FROM comentarios WHERE post_id = ? ORDER BY creado_en ASC",
        (post_id,),
    )
    return render_template(
        "post.html",
        post=post,
        comentarios=comentarios,
        diario=db.get_diario(),
    )


@app.route("/post/<int:post_id>/comentar", methods=["POST"])
def comentar(post_id):
    if db.query("SELECT id FROM posts WHERE id = ?", (post_id,), one=True) is None:
        abort(404)
    nombre = (request.form.get("nombre") or "Anónimo").strip() or "Anónimo"
    mensaje = (request.form.get("mensaje") or "").strip()
    if not mensaje:
        flash("Escribe algo antes de comentar 🙂", "error")
    else:
        db.execute(
            "INSERT INTO comentarios (post_id, nombre, mensaje) VALUES (?, ?, ?)",
            (post_id, nombre, mensaje),
        )
        flash("¡Gracias por comentar!", "ok")
    return redirect(url_for("ver_post", post_id=post_id) + "#comentarios")


@app.route("/publicar", methods=["GET", "POST"])
@solo_admin
def publicar():
    if request.method == "POST":
        titulo = (request.form.get("titulo") or "").strip()
        cuerpo = (request.form.get("cuerpo") or "").strip()
        tema = request.form.get("tema") or "General"
        autor = (request.form.get("autor") or "Anónimo").strip() or "Anónimo"
        extracto = (request.form.get("extracto") or "").strip()

        if not titulo or not cuerpo:
            flash("El título y el contenido no pueden estar vacíos.", "error")
        else:
            if not extracto:
                # Si no hay extracto, tomamos las primeras líneas del cuerpo.
                extracto = cuerpo.strip().replace("\n", " ")[:160]
                if len(cuerpo) > 160:
                    extracto += "…"
            nuevo_id = db.execute(
                """INSERT INTO posts (titulo, tema, autor, extracto, cuerpo)
                   VALUES (?, ?, ?, ?, ?)""",
                (titulo, tema, autor, extracto, cuerpo),
            )
            flash("¡Tu publicación ya está en línea!", "ok")
            return redirect(url_for("ver_post", post_id=nuevo_id))

    return render_template("nuevo_post.html", temas=TEMAS, diario=db.get_diario())


@app.route("/dudas", methods=["GET", "POST"])
def dudas():
    if request.method == "POST":
        nombre = (request.form.get("nombre") or "Anónimo").strip() or "Anónimo"
        pregunta = (request.form.get("pregunta") or "").strip()
        if not pregunta:
            flash("Escribe tu duda antes de enviarla.", "error")
        else:
            db.execute(
                "INSERT INTO dudas (nombre, pregunta) VALUES (?, ?)",
                (nombre, pregunta),
            )
            flash("Tu duda fue enviada. ¡Gracias por confiar!", "ok")
        return redirect(url_for("dudas"))

    todas = db.query("SELECT * FROM dudas ORDER BY creado_en DESC")
    return render_template("dudas.html", dudas=todas, diario=db.get_diario())


@app.route("/dudas/<int:duda_id>/responder", methods=["POST"])
@solo_admin
def responder_duda(duda_id):
    respuesta = (request.form.get("respuesta") or "").strip()
    if respuesta:
        db.execute(
            "UPDATE dudas SET respuesta = ? WHERE id = ?", (respuesta, duda_id)
        )
        flash("Respuesta guardada.", "ok")
    return redirect(url_for("dudas") + f"#duda-{duda_id}")


@app.route("/post/<int:post_id>/megusta", methods=["POST"])
def megusta(post_id):
    """Da o quita 'me gusta' a una publicación (se recuerda en la sesión)."""
    if db.query("SELECT id FROM posts WHERE id = ?", (post_id,), one=True) is None:
        abort(404)
    dados = session.get("me_gusta", [])
    if post_id in dados:
        dados.remove(post_id)
        db.execute("UPDATE posts SET me_gusta = MAX(me_gusta - 1, 0) WHERE id = ?", (post_id,))
    else:
        dados.append(post_id)
        db.execute("UPDATE posts SET me_gusta = me_gusta + 1 WHERE id = ?", (post_id,))
    session["me_gusta"] = dados
    destino = request.form.get("volver") or url_for("inicio")
    return redirect(destino)


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("admin"):
        return redirect(url_for("panel"))
    if request.method == "POST":
        if (request.form.get("clave") or "") == ADMIN_PASSWORD:
            session["admin"] = True
            flash("¡Hola! Entraste como administrador.", "ok")
            volver = request.form.get("volver") or url_for("panel")
            return redirect(volver)
        flash("Contraseña incorrecta.", "error")
    return render_template(
        "login.html",
        diario=db.get_diario(),
        volver=request.args.get("volver", ""),
    )


@app.route("/logout")
def logout():
    session.pop("admin", None)
    flash("Cerraste sesión.", "ok")
    return redirect(url_for("inicio"))


@app.route("/panel", methods=["GET", "POST"])
@solo_admin
def panel():
    """Panel para actualizar la canción, el tema y el mensaje del día.

    Protegido: solo entra quien haya iniciado sesión como administrador.
    """
    if request.method == "POST":
        campos = [
            "cancion_titulo", "cancion_enlace", "cancion_nota",
            "tema_debate", "mensaje", "mensaje_tipo",
        ]
        for clave in campos:
            valor = (request.form.get(clave) or "").strip()
            db.execute(
                "UPDATE diario SET valor = ? WHERE clave = ?", (valor, clave)
            )
        flash("Contenido del día actualizado ✨", "ok")
        return redirect(url_for("panel"))

    return render_template("panel.html", diario=db.get_diario())


@app.errorhandler(404)
def no_encontrado(e):
    return render_template("404.html", diario=db.get_diario()), 404


# Filtro para mostrar fechas de forma amable en las plantillas.
@app.template_filter("fecha")
def formatear_fecha(valor):
    # valor viene como 'YYYY-MM-DD HH:MM:SS'
    try:
        fecha, hora = valor.split(" ")
        y, m, d = fecha.split("-")
        meses = ["", "ene", "feb", "mar", "abr", "may", "jun",
                 "jul", "ago", "sep", "oct", "nov", "dic"]
        return f"{int(d)} {meses[int(m)]} {y} · {hora[:5]}"
    except Exception:
        return valor


# Inicializar la base de datos al importar el módulo. Esto hace que las tablas
# existan tanto si arrancas con `python app.py` (local) como si lo hace gunicorn
# en Render. Es idempotente: no borra ni duplica nada si ya existe.
db.init_db(app)


if __name__ == "__main__":
    # Solo para desarrollo local. En Render se usa gunicorn (ver Procfile / render.yaml).
    puerto = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "true").lower() in ("1", "true", "yes")
    app.run(host="0.0.0.0", port=puerto, debug=debug)
