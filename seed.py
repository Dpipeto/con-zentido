"""Llena la base de datos con contenido de ejemplo.

Ejecuta:  python seed.py
"""
import db
from app import app

POSTS = [
    {
        "titulo": "Empezar terapia no es rendirse, es cuidarse",
        "tema": "Salud mental",
        "autor": "Sofi",
        "extracto": "Pedir ayuda no significa que estés roto. Significa que te importas lo suficiente como para no cargar con todo tú solo.",
        "cuerpo": (
            "Durante mucho tiempo pensé que ir a terapia era admitir una derrota. "
            "Como si necesitar ayuda fuera una prueba de que algo en mí estaba mal.\n\n"
            "Con el tiempo entendí que es justo al revés. Ir a terapia es como ir al "
            "dentista antes de que la muela reviente: es prevención, es cuidado, es "
            "darte el mismo cariño que le darías a un amigo que la está pasando mal.\n\n"
            "Si estás pensando en dar el paso, empieza pequeño. Busca opciones gratuitas "
            "o de bajo costo en tu zona, pregunta en tu escuela o centro de salud, y "
            "recuerda: la primera sesión no te compromete a nada. Solo es una "
            "conversación."
        ),
    },
    {
        "titulo": "¿Quién soy cuando nadie me está mirando?",
        "tema": "Identidad",
        "autor": "Dani",
        "extracto": "La identidad no es una etiqueta que encuentras un día y ya. Es algo que vas construyendo, capa por capa, decisión por decisión.",
        "cuerpo": (
            "Crecemos rodeados de expectativas: las de la familia, las de los amigos, "
            "las de internet. Y a veces es difícil separar lo que queremos de lo que "
            "se supone que deberíamos querer.\n\n"
            "Construir tu identidad no es encontrar una respuesta final. Es hacerte "
            "preguntas mejores. ¿Qué me hace sentir yo? ¿Qué cosas hago solo para "
            "encajar? ¿Qué me gustaría intentar si nadie me juzgara?\n\n"
            "No tienes que definirte hoy. Tienes permiso de cambiar, de contradecirte, "
            "de probar y equivocarte. Eso también es ser tú."
        ),
    },
    {
        "titulo": "Cómo hablarte cuando cometes un error",
        "tema": "Autoestima",
        "autor": "Anónimo",
        "extracto": "La voz con la que te hablas importa. Si no le hablarías así a un amigo, quizá tampoco deberías hablarte así a ti.",
        "cuerpo": (
            "Todos tenemos una voz interna. El problema es cuando esa voz se convierte "
            "en nuestro peor crítico.\n\n"
            "Un ejercicio simple: la próxima vez que te equivoques y aparezca ese "
            "'soy un desastre', imagina que un amigo te cuenta que le pasó lo mismo. "
            "¿Le dirías que es un desastre? Seguramente no. Le dirías que fue un error, "
            "que le puede pasar a cualquiera, que mañana lo intenta de nuevo.\n\n"
            "Date esa misma amabilidad. No es autoengaño, es dejar de patear a alguien "
            "que ya está en el suelo: tú."
        ),
    },
]

DUDAS = [
    {
        "nombre": "Anónimo",
        "pregunta": "¿Es normal sentirme cansado todo el tiempo aunque duerma bien?",
        "respuesta": (
            "El cansancio constante puede tener causas físicas y emocionales. Vale la "
            "pena revisarlo con un médico, pero también pregúntate cómo anda tu ánimo "
            "últimamente. A veces el agotamiento no es del cuerpo, es de la cabeza."
        ),
    },
    {
        "nombre": "Alex",
        "pregunta": "¿Cómo sé si lo que siento es tristeza normal o algo más serio?",
        "respuesta": None,
    },
]


def main():
    with app.app_context():
        db.init_db(app)
        # ¿Ya hay posts? Si sí, no duplicamos.
        existentes = db.query("SELECT COUNT(*) AS n FROM posts", one=True)["n"]
        if existentes:
            print(f"Ya hay {existentes} publicaciones. No se agregó nada.")
            return

        for p in POSTS:
            db.execute(
                """INSERT INTO posts (titulo, tema, autor, extracto, cuerpo)
                   VALUES (?, ?, ?, ?, ?)""",
                (p["titulo"], p["tema"], p["autor"], p["extracto"], p["cuerpo"]),
            )
        for d in DUDAS:
            db.execute(
                "INSERT INTO dudas (nombre, pregunta, respuesta) VALUES (?, ?, ?)",
                (d["nombre"], d["pregunta"], d["respuesta"]),
            )
        db.close_db()
        print("¡Listo! Se agregó contenido de ejemplo.")


if __name__ == "__main__":
    main()
