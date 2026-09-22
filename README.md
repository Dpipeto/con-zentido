# Con Zentido 💜

Un blog con sentido sobre **salud mental**, **construcción de la identidad** y todos
los temas que quieras ir agregando con el tiempo. Hecho con **Flask** y SQLite (sin
bases de datos externas ni configuraciones complicadas).

## ¿Qué incluye?

- **Publicaciones** por tema, con página de lectura y filtros. **Solo el
  administrador (tú) puede publicar**; el resto de personas participa comentando.
- **Me gusta** en cada publicación (con contador; se recuerda por sesión).
- **Comentarios anónimos** debajo de cada publicación, abiertos para todo el mundo.
- **Buzón de dudas**: cualquiera puede dejar una pregunta (anónima si quiere) y
  el administrador puede responderlas.
- **Barra lateral "del día"**: canción del día, tema a debatir y un mensaje
  motivacional / fun fact.
- **Login de administrador** que protege publicar, el panel y las respuestas a dudas.
- **Panel** sencillo para actualizar el contenido del día.

## ¿Quién puede hacer qué?

| Acción                        | Visitante | Administrador (tú) |
|-------------------------------|:---------:|:------------------:|
| Leer publicaciones            |     ✅    |         ✅         |
| Dar "me gusta"                |     ✅    |         ✅         |
| Comentar (anónimo)            |     ✅    |         ✅         |
| Enviar una duda               |     ✅    |         ✅         |
| **Publicar una entrada**      |     ❌    |         ✅         |
| **Responder dudas**           |     ❌    |         ✅         |
| **Editar el contenido del día** |  ❌    |         ✅         |

Para hacer las acciones de administrador, entra en `/login` con tu contraseña.

Todo esto sale de tu maqueta: el logo arriba, las dudas a la izquierda, las
publicaciones al centro, y a la derecha la canción, el tema del día y los mensajes.

## Cómo ejecutarlo

Necesitas **Python 3.10 o superior**.

```bash
# 1. (Opcional pero recomendado) crea un entorno virtual
python -m venv venv
source venv/bin/activate        # en Windows:  venv\Scripts\activate

# 2. Instala Flask
pip install -r requirements.txt

# 3. (Opcional) agrega contenido de ejemplo para no arrancar en blanco
python seed.py

# 4. Arranca el servidor
python app.py
```

Luego abre **http://127.0.0.1:5000** en tu navegador.

> La primera vez se crea solo el archivo `con_zentido.db` con las tablas. Si quieres
> empezar de cero, borra ese archivo y vuelve a ejecutar.

## Estructura del proyecto

```
con-zentido/
├── app.py            # rutas y lógica de la aplicación
├── db.py             # ayudante para la base de datos (SQLite)
├── schema.sql        # tablas de la base de datos
├── seed.py           # contenido de ejemplo
├── requirements.txt
├── render.yaml       # configuración para desplegar en Render (con disco persistente)
├── Procfile          # comando de arranque para producción
├── .gitignore
├── templates/        # plantillas HTML (Jinja2)
│   ├── base.html         # estructura común (cabecera, pie)
│   ├── index.html        # portada de 3 columnas
│   ├── post.html         # publicación + comentarios
│   ├── nuevo_post.html   # formulario para publicar
│   ├── dudas.html        # buzón de dudas
│   ├── login.html        # entrar como administrador
│   ├── panel.html        # editar contenido del día
│   ├── _rail.html        # barra lateral reutilizable
│   └── 404.html
└── static/css/style.css  # todos los estilos
```

## Entrar como administrador

Responder dudas y editar el contenido del día está protegido con una contraseña.

- La contraseña por defecto es **`consentido`**. Cámbiala con una variable de entorno:

  ```bash
  # Linux / macOS
  export CON_ZENTIDO_ADMIN="tu-clave-secreta"
  export CON_ZENTIDO_SECRET="otra-clave-para-las-sesiones"
  python app.py

  # Windows (PowerShell)
  $env:CON_ZENTIDO_ADMIN="tu-clave-secreta"
  python app.py
  ```

- Para entrar, ve a **`/login`** (o al enlace que aparece al intentar responder
  una duda) y escribe la contraseña. Verás los enlaces **Panel** y **Salir** en el menú.
- El resto del sitio (leer, comentar, dar me gusta, enviar dudas) **sigue abierto**
  para todas las personas, sin necesidad de iniciar sesión.

## Rutas principales

| Ruta                | Para qué sirve                          |
|---------------------|-----------------------------------------|
| `/`                 | Portada con publicaciones y barra lateral |
| `/post/<id>`        | Leer una publicación y sus comentarios  |
| `/post/<id>/megusta`| Dar o quitar me gusta                   |
| `/publicar`         | Escribir una nueva publicación (protegido) |
| `/dudas`            | Enviar y ver dudas                      |
| `/login` · `/logout`| Entrar / salir como administrador       |
| `/panel`            | Cambiar canción, tema y mensaje del día (protegido) |

## Cómo agregar temas nuevos

Abre `app.py` y edita la lista `TEMAS` al inicio. Los temas nuevos aparecerán
automáticamente en los filtros y en el formulario de publicar.

## Publicar en Render (sin perder datos)

Este proyecto ya viene listo para Render con **disco persistente**, de modo que tu
base de datos SQLite y todas las publicaciones **se conservan** entre despliegues,
reinicios y suspensiones.

> ⚠️ **Importante sobre el plan.** En el plan **gratuito** de Render, el sistema de
> archivos es efímero: la base de datos se borra cada vez que el servicio se
> reinicia, se redespliega o se suspende por inactividad. Para que los datos
> persistan hace falta un **disco persistente**, que **solo está disponible en
> planes de pago** (Starter, ~7 USD/mes). Por eso el `render.yaml` usa el plan
> `starter`. Más abajo tienes una alternativa gratis.

### Pasos

1. Sube este proyecto a un repositorio de **GitHub** (o GitLab/Bitbucket).
2. En Render, crea un **Blueprint** nuevo y conéctalo a tu repositorio. Render
   detectará el archivo `render.yaml` y configurará solo:
   - el servicio web (con `gunicorn`),
   - el **disco persistente** de 1 GB montado en `/var/data`,
   - la variable `DATABASE_PATH` apuntando a `/var/data/con_zentido.db`,
   - una clave secreta de sesión generada automáticamente.
3. Cuando te lo pida, escribe el valor de **`CON_ZENTIDO_ADMIN`** (tu contraseña de
   administrador). No queda guardada en el repositorio.
4. Dale a **Apply / Deploy** y espera a que termine. ¡Listo!

Tu sitio arrancará vacío (sin publicaciones). Entra en `/login` con tu contraseña y
empieza a publicar. Todo lo que crees se guardará en el disco y no se borrará.

### Configuración manual (si no usas el Blueprint)

Si prefieres crear el servicio "a mano" en el panel de Render:

- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2`
- **Disk:** añade un disco (Settings → Disks) montado en `/var/data`.
- **Environment Variables:**
  - `DATABASE_PATH` = `/var/data/con_zentido.db`
  - `CON_ZENTIDO_ADMIN` = *(tu contraseña)*
  - `CON_ZENTIDO_SECRET` = *(una cadena larga y aleatoria)*
  - `PYTHON_VERSION` = `3.12.3`

### ¿Y si quiero empezar gratis?

El plan gratuito no tiene disco persistente, así que para no perder datos sin pagar
tendrías que cambiar de SQLite a una base de datos externa. Dos opciones populares:

- **Render Postgres**: Render ofrece una base de datos PostgreSQL administrada (con
  una capa gratuita limitada). Requiere adaptar el código para usar Postgres.
- **Turso** (SQLite en la nube): compatible con SQLite, con capa gratuita generosa.
  El SQL apenas cambia.

Si quieres, puedo prepararte una versión que use una de estas para que funcione
gratis. Dímelo y te la armo.

## Antes de publicarlo en internet (importante)

Este proyecto está pensado para aprender y usarse localmente o en Render. Ten en
cuenta:

1. **Cambia las contraseñas por defecto** con las variables `CON_ZENTIDO_ADMIN` y
   `CON_ZENTIDO_SECRET` (ver la sección "Entrar como administrador").
2. En producción se usa `gunicorn` (ya configurado en `render.yaml`); no uses el
   servidor de desarrollo de Flask.
3. Si esperas mucho tráfico, considera un login más robusto (usuarios, contraseñas
   cifradas) o una base de datos como PostgreSQL en lugar de SQLite.

## Una nota importante 💜

Este blog habla de salud mental, pero **no reemplaza la ayuda profesional**. Si tú o
alguien que conoces la está pasando mal, busquen apoyo de un profesional o de una
línea de ayuda de su país.
