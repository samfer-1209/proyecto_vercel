# TaskHub - Sistema de Gestión de Tareas Colaborativas

TaskHub es un sistema académico de gestión colaborativa de proyectos y tareas, desarrollado con Django 5, plantillas de Django, HTML5, CSS3, JavaScript Vanilla y Firebase Firestore.

## Arquitectura general

- Backend: Django 5 en patrón MVT (Model-View-Template).
- Frontend: Django Templates + CSS moderno + JavaScript Vanilla.
- Autenticación: Sistema de Django con login, logout, registro y recuperación de contraseña.
- Base de datos principal: Firebase Firestore para proyectos, tareas, usuarios extendidos y comentarios.
- Control de versiones: Git + GitHub.
- Despliegue: Vercel.

## Estructura de carpetas

```
trabajo_luna/
├── .gitignore
├── .env.example
├── README.md
├── manage.py
├── requirements.txt
├── runtime.txt
├── vercel.json
├── taskhub/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── firebase.py
└── core/
    ├── __init__.py
    ├── admin.py
    ├── apps.py
    ├── forms.py
    ├── models.py
    ├── tests.py
    ├── urls.py
    ├── views.py
    ├── templates/
    │   ├── core/
    │   └── registration/
    └── static/
        └── core/
            ├── css/styles.css
            └── js/main.js
```

## Funcionalidades principales

- Registro, inicio de sesión, cierre de sesión y recuperación de contraseña.
- Dashboard con métricas de proyectos y tareas.
- CRUD completo de proyectos y tareas.
- Comentarios por tarea.
- Perfil de usuario y edición de perfil.
- Filtros y búsquedas sobre proyectos y tareas.
- Roles: Administrador y Usuario.
- Persistencia de datos en Firebase Firestore.

## Diseño de la base de datos Firestore

### Colecciones

- `usuarios`
  - `uid`: id de Django
  - `email`
  - `nombre`
  - `apellido`
  - `rol`: `Administrador` o `Usuario`
  - `fecha_creacion`

- `proyectos`
  - `nombre`
  - `descripcion`
  - `fecha_creacion`
  - `propietario_id`
  - `estado`

- `tareas`
  - `titulo`
  - `descripcion`
  - `prioridad`
  - `estado`
  - `fecha_limite`
  - `proyecto_id`
  - `usuario_asignado_id`
  - `fecha_creacion`

- `comentarios`
  - `tarea_id`
  - `autor_id`
  - `texto`
  - `fecha_creacion`

### Relaciones

- Un `proyecto` pertenece a un propietario y puede contener múltiples `tareas`.
- Una `tarea` está vinculada a un `proyecto` y a un `usuario_asignado`.
- Un `comentario` se asocia con una `tarea`.

### Buenas prácticas

- Mantener los datos de autenticación en Django y usar Firestore para entidades del dominio.
- Normalizar referencias de documento usando IDs.
- Usar índices compuestos en Firestore para consultas con estado, prioridad y fecha límite.

## Requerimientos funcionales

1. Registro de nuevos usuarios.
2. Inicio y cierre de sesión.
3. Recuperación de contraseña.
4. Crear, listar, editar y eliminar proyectos.
5. Crear, listar, editar y eliminar tareas.
6. Agregar comentarios a tareas.
7. Filtrar y buscar proyectos y tareas.
8. Gestionar roles de administrador y usuario.
9. Ver estadísticas en el dashboard.
10. Editar perfil y revisar tareas asignadas.

## Requerimientos no funcionales

- Interfaz responsiva y profesional.
- Uso exclusivo de Django Templates y JavaScript Vanilla.
- Compatibilidad con Python 3.13.
- Despliegue en Vercel.
- Uso de Firebase Firestore.
- No usar frameworks SPA ni Django REST Framework.

## Historias de usuario

- Como usuario, quiero registrarme y acceder al sistema.
- Como usuario, quiero ver mis tareas asignadas.
- Como administrador, quiero gestionar usuarios y roles.
- Como usuario, quiero crear proyectos y tareas.
- Como gestor, quiero ver métricas de tareas completadas y pendientes.
- Como colaborador, quiero comentar tareas para coordinar el trabajo.

## Casos de uso principales

- Crear un proyecto.
- Crear una tarea dentro de un proyecto.
- Asignar una tarea a un usuario.
- Cambiar el estado de una tarea.
- Filtrar tareas por estado, prioridad y fecha.
- Visualizar detalles de un proyecto.
- Administrar roles de usuario.

## Instalación local

1. Clona el repositorio.
2. Crea un entorno virtual con Python 3.13.
3. Instala dependencias:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

4. Copia `.env.example` a `.env` y completa las variables.
5. Ejecuta migraciones de Django:

```bash
python manage.py migrate
```

6. Inicia la aplicación:

```bash
python manage.py runserver
```

7. Abre `http://127.0.0.1:8000/`.

## Variables de entorno necesarias

- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG`
- `DJANGO_ALLOWED_HOSTS`
- `FIREBASE_PROJECT_ID`
- `FIREBASE_API_KEY`
- `FIREBASE_SERVICE_ACCOUNT_JSON`

## Configuración de Firebase

1. Crea un proyecto en Firebase.
2. Habilita Firestore en modo de producción o pruebas.
3. Genera una clave de cuenta de servicio.
4. Copia el JSON de la clave en `FIREBASE_SERVICE_ACCOUNT_JSON` o guarda el archivo `firebase_service_account.json` en la raíz.
5. Asegúrate de tener `FIREBASE_PROJECT_ID` configurado.

## Despliegue en Vercel

1. Conecta el repositorio a GitHub en Vercel.
2. Configura las variables de entorno en Vercel idénticas a las de `.env`.
3. Asegura `runtime.txt` en la raíz con `python-3.13`.
4. Deja `vercel.json` para que Vercel utilice el build de Python.

## Metodología por fases

1. **Fase 1: Arquitectura y planificación** — Definición de requerimientos, colecciones Firestore y árbol de carpetas.
2. **Fase 2: Configuración del entorno** — Proyecto Django, dependencias, Firebase y settings.
3. **Fase 3: Autenticación** — Registro, login, logout y recuperación de contraseña.
4. **Fase 4: CRUD de proyectos** — Vistas, formularios, plantillas y validaciones.
5. **Fase 5: CRUD de tareas** — Tareas, asignación, estados y prioridad.
6. **Fase 6: Dashboard** — Métricas, gráficos simples y resumen de información.
7. **Fase 7: Roles y permisos** — Administrador y usuario, control de acceso.
8. **Fase 8: Filtros y búsquedas** — Búsqueda por nombre, estado, prioridad y fecha.
9. **Fase 9: Pruebas** — Tests unitarios de formularios y flujos básicos.
10. **Fase 10: Despliegue** — GitHub, Vercel y configuración de Firebase.

## Notas finales

Este proyecto está diseñado para ser una solución académica completa con una arquitectura Django MVT y Firestore como fuente de datos. Todas las vistas se renderizan en el servidor y la interfaz se construye con HTML, CSS y JavaScript básico.

## Seguridad y manejo de credenciales

- No comitees el archivo de cuenta de servicio de Firebase ni `.env` con claves privadas.
- Usa `firebase_service_account.json` en la raíz solo en entornos locales y añade el archivo a `.gitignore`.
- En CI y producción guarda las credenciales en el gestor de secretos de la plataforma (GitHub Actions secrets, Vercel env vars, Google Secret Manager, etc.).
- Para pruebas locales puedes usar variables de entorno con JSON compactado: `export FIREBASE_SERVICE_ACCOUNT_JSON=$(jq -c . path/to/key.json)`.

