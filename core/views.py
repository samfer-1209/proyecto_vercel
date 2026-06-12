from datetime import datetime
import logging
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone
from google.api_core.exceptions import PermissionDenied, ServiceUnavailable
from .forms import (
    CommentForm,
    ProfileForm,
    ProjectForm,
    TaskForm,
    UserRegistrationForm,
    UserRoleForm,
)
from .models import ProyectoDocumento, TareaDocumento
from taskhub.firebase import get_collection, get_document

logger = logging.getLogger(__name__)


def _doc_to_dict(doc):
    data = doc.to_dict() or {}
    data["id"] = doc.id
    return data


def _ensure_usuario(user):
    """
    Crea o actualiza un documento de usuario en Firestore.
    Si Firestore no está disponible (API deshabilitada, sin conexión),
    continúa sin lanzar excepción para evitar bloquear el registro.
    """
    payload = {
        "uid": str(user.id),
        "email": user.email,
        "nombre": user.first_name or user.username,
        "apellido": user.last_name or "",
        "rol": "Administrador" if user.is_staff else "Usuario",
        "fecha_creacion": datetime.utcnow(),
    }
    try:
        usuarios = get_collection("usuarios")
        doc_ref = usuarios.document(str(user.id))
        snapshot = doc_ref.get()
        if not snapshot.exists:
            doc_ref.set(payload)
        else:
            existing = snapshot.to_dict() or {}
            if existing.get("rol") != payload["rol"]:
                doc_ref.update({"rol": payload["rol"]})
    except PermissionDenied as e:
        logger.warning(
            f"Cloud Firestore API no habilitada o permisos insuficientes para usuario {user.id}. "
            f"Consulta SETUP_FIRESTORE.md para habilitar la API. Error: {e}"
        )
    except ServiceUnavailable as e:
        logger.warning(
            f"Cloud Firestore no disponible en este momento para usuario {user.id}. "
            f"Reintentar más tarde. Error: {e}"
        )
    except Exception as e:
        logger.error(f"Error al sincronizar usuario {user.id} con Firestore: {e}")
    return payload


def _collection_list(collection_name):
    return [
        _doc_to_dict(doc)
        for doc in get_collection(collection_name).stream()
    ]


def _get_proyecto(proyecto_id):
    proyecto_ref = get_document("proyectos", proyecto_id)
    snapshot = proyecto_ref.get()
    if not snapshot.exists:
        return None
    return _doc_to_dict(snapshot)


def _get_tarea(tarea_id):
    tarea_ref = get_document("tareas", tarea_id)
    snapshot = tarea_ref.get()
    if not snapshot.exists:
        return None
    return _doc_to_dict(snapshot)


def _get_comments_for_task(tarea_id):
    comentarios = get_collection("comentarios")
    docs = comentarios.where("tarea_id", "==", tarea_id).order_by("fecha_creacion", direction="DESCENDING").stream()
    return [_doc_to_dict(doc) for doc in docs]


def _filter_projects(projects, search=None, estado=None):
    result = projects
    if search:
        text = search.lower()
        result = [p for p in result if text in p.get("nombre", "").lower()]
    if estado:
        result = [p for p in result if p.get("estado") == estado]
    return result


def _filter_tasks(tasks, search=None, estado=None, prioridad=None, fecha=None):
    result = tasks
    if search:
        text = search.lower()
        result = [t for t in result if text in t.get("titulo", "").lower()]
    if estado:
        result = [t for t in result if t.get("estado") == estado]
    if prioridad:
        result = [t for t in result if t.get("prioridad") == prioridad]
    if fecha:
        result = [
            t for t in result
            if t.get("fecha_limite") and t.get("fecha_limite")[:10] == fecha
        ]
    return result


def _create_project_payload(user, data):
    return {
        "nombre": data["nombre"],
        "descripcion": data["descripcion"],
        "estado": data["estado"],
        "propietario_id": str(user.id),
        "fecha_creacion": datetime.utcnow(),
    }


def _create_task_payload(data):
    fecha_limite = data.get("fecha_limite")
    return {
        "titulo": data["titulo"],
        "descripcion": data["descripcion"],
        "prioridad": data["prioridad"],
        "estado": data["estado"],
        "fecha_limite": fecha_limite.isoformat() if fecha_limite else None,
        "proyecto_id": data["proyecto_id"],
        "usuario_asignado_id": data["usuario_asignado_id"],
        "fecha_creacion": datetime.utcnow(),
    }


def _get_select_choices(documents, label_key="nombre"):
    return [(doc["id"], doc.get(label_key, "Sin nombre")) for doc in documents]


def _is_administrator(user):
    return user.is_staff


def _can_manage_project(user, proyecto):
    return user.is_staff or proyecto.get("propietario_id") == str(user.id)


def _can_manage_task(user, tarea):
    return user.is_staff or tarea.get("usuario_asignado_id") == str(user.id)


def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.is_active = True
            
            # Validación de seguridad: solo el primer admin puede ser administrador
            rol_seleccionado = form.cleaned_data.get("rol", "Usuario")
            admins_count = User.objects.filter(is_staff=True).count()
            
            if rol_seleccionado == "Administrador" and admins_count == 0:
                # El primer registro puede ser admin
                user.is_staff = True
                messages.success(request, "Registro exitoso. Te registraste como Administrador.")
            else:
                # Otros registros son usuarios normales
                user.is_staff = False
                if rol_seleccionado == "Administrador" and admins_count > 0:
                    messages.warning(request, "Ya existe un Administrador. Te registraste como Usuario.")
                else:
                    messages.success(request, "Registro exitoso. Bienvenido al sistema.")
            
            user.save()
            _ensure_usuario(user)
            login(request, user)
            return redirect("dashboard")
    else:
        form = UserRegistrationForm()
    return render(request, "registration/register.html", {"form": form})


@login_required
def dashboard(request):
    _ensure_usuario(request.user)
    proyectos = _collection_list("proyectos")
    tareas = _collection_list("tareas")
    usuarios = User.objects.all()
    
    # Datos generales
    user_tasks = [t for t in tareas if t.get("usuario_asignado_id") == str(request.user.id)]
    vencidas = [t for t in tareas if t.get("estado") != "Completada" and t.get("fecha_limite") and t.get("fecha_limite") < datetime.utcnow().isoformat()]
    
    # Estadísticas por estado
    proyectos_activos = len([p for p in proyectos if p.get("estado") == "Activo"])
    proyectos_completados = len([p for p in proyectos if p.get("estado") == "Completado"])
    tareas_en_progreso = len([t for t in tareas if t.get("estado") == "En progreso"])
    tareas_pendientes = len([t for t in tareas if t.get("estado") == "Pendiente"])
    tareas_completadas = len([t for t in tareas if t.get("estado") == "Completada"])
    
    # Datos de administrador
    is_admin = _is_administrator(request.user)
    usuarios_activos = User.objects.filter(is_active=True).count()
    admins_count = User.objects.filter(is_staff=True).count()
    
    context = {
        "is_admin": is_admin,
        "proyectos_total": len(proyectos),
        "tareas_total": len(tareas),
        "tareas_pendientes": tareas_pendientes,
        "tareas_en_progreso": tareas_en_progreso,
        "tareas_completadas": tareas_completadas,
        "tareas_vencidas": len(vencidas),
        "proyectos_activos": proyectos_activos,
        "proyectos_completados": proyectos_completados,
        "proyectos_recientes": sorted(proyectos, key=lambda p: p.get("fecha_creacion"), reverse=True)[:4],
        "tareas_propia": user_tasks[:5],
        "usuarios_activos": usuarios_activos,
        "admins_count": admins_count,
        "usuarios_recientes": usuarios.order_by("-date_joined")[:5],
    }
    return render(request, "core/dashboard.html", context)


@login_required
def project_list(request):
    search = request.GET.get("search", "")
    estado = request.GET.get("estado", "")
    proyectos = _collection_list("proyectos")
    proyectos = _filter_projects(proyectos, search=search, estado=estado)
    return render(request, "core/project_list.html", {"proyectos": proyectos, "search": search, "estado": estado})


@login_required
def project_detail(request, proyecto_id):
    proyecto = _get_proyecto(proyecto_id)
    if not proyecto:
        messages.error(request, "Proyecto no encontrado.")
        return redirect("project_list")
    tareas = [t for t in _collection_list("tareas") if t.get("proyecto_id") == proyecto_id]
    return render(request, "core/project_detail.html", {"proyecto": proyecto, "tareas": tareas})


@login_required
def project_create(request):
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            payload = _create_project_payload(request.user, form.cleaned_data)
            get_collection("proyectos").add(payload)
            messages.success(request, "Proyecto creado correctamente.")
            return redirect("project_list")
    else:
        form = ProjectForm()
    return render(request, "core/project_form.html", {"form": form, "title": "Crear proyecto"})


@login_required
def project_edit(request, proyecto_id):
    proyecto = _get_proyecto(proyecto_id)
    if not proyecto or not _can_manage_project(request.user, proyecto):
        messages.error(request, "No tienes permisos para editar este proyecto.")
        return redirect("project_list")
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            get_document("proyectos", proyecto_id).update({
                "nombre": form.cleaned_data["nombre"],
                "descripcion": form.cleaned_data["descripcion"],
                "estado": form.cleaned_data["estado"],
            })
            messages.success(request, "Proyecto actualizado.")
            return redirect("project_detail", proyecto_id=proyecto_id)
    else:
        form = ProjectForm(initial={
            "nombre": proyecto.get("nombre"),
            "descripcion": proyecto.get("descripcion"),
            "estado": proyecto.get("estado"),
        })
    return render(request, "core/project_form.html", {"form": form, "title": "Editar proyecto"})


@login_required
def project_delete(request, proyecto_id):
    proyecto = _get_proyecto(proyecto_id)
    if proyecto and _can_manage_project(request.user, proyecto):
        get_document("proyectos", proyecto_id).delete()
        messages.success(request, "Proyecto eliminado.")
    else:
        messages.error(request, "No tienes permisos para eliminar este proyecto.")
    return redirect("project_list")


@login_required
def task_list(request):
    search = request.GET.get("search", "")
    estado = request.GET.get("estado", "")
    prioridad = request.GET.get("prioridad", "")
    fecha = request.GET.get("fecha", "")
    tareas = _collection_list("tareas")
    if not request.user.is_staff:
        tareas = [t for t in tareas if t.get("usuario_asignado_id") == str(request.user.id)]
    tareas = _filter_tasks(tareas, search=search, estado=estado, prioridad=prioridad, fecha=fecha)
    return render(request, "core/task_list.html", {
        "tareas": tareas,
        "search": search,
        "estado": estado,
        "prioridad": prioridad,
        "fecha": fecha,
    })


@login_required
def task_detail(request, tarea_id):
    tarea = _get_tarea(tarea_id)
    if not tarea:
        messages.error(request, "Tarea no encontrada.")
        return redirect("task_list")
    proyecto = _get_proyecto(tarea.get("proyecto_id"))
    usuario_asignado = None
    if tarea.get("usuario_asignado_id"):
        snapshot = get_document("usuarios", tarea["usuario_asignado_id"]).get()
        usuario_asignado = snapshot.to_dict() if snapshot.exists else None
    comments = _get_comments_for_task(tarea_id)
    form = CommentForm()
    return render(request, "core/task_detail.html", {
        "tarea": tarea,
        "proyecto": proyecto,
        "usuario_asignado": usuario_asignado,
        "comments": comments,
        "form": form,
    })


@login_required
def task_create(request):
    proyectos = _collection_list("proyectos")
    usuarios = _collection_list("usuarios")
    proyecto_choices = _get_select_choices(proyectos, "nombre")
    user_choices = _get_select_choices(usuarios, "nombre")
    if request.method == "POST":
        form = TaskForm(request.POST, project_choices=proyecto_choices, user_choices=user_choices)
        if form.is_valid():
            payload = _create_task_payload(form.cleaned_data)
            get_collection("tareas").add(payload)
            messages.success(request, "Tarea creada correctamente.")
            return redirect("task_list")
    else:
        form = TaskForm(project_choices=proyecto_choices, user_choices=user_choices)
    return render(request, "core/task_form.html", {"form": form, "title": "Crear tarea"})


@login_required
def task_edit(request, tarea_id):
    tarea = _get_tarea(tarea_id)
    if not tarea or not _can_manage_task(request.user, tarea):
        messages.error(request, "No tienes permisos para editar esta tarea.")
        return redirect("task_list")
    proyectos = _collection_list("proyectos")
    usuarios = _collection_list("usuarios")
    proyecto_choices = _get_select_choices(proyectos, "nombre")
    user_choices = _get_select_choices(usuarios, "nombre")
    if request.method == "POST":
        form = TaskForm(request.POST, project_choices=proyecto_choices, user_choices=user_choices)
        if form.is_valid():
            payload = _create_task_payload(form.cleaned_data)
            get_document("tareas", tarea_id).update(payload)
            messages.success(request, "Tarea actualizada.")
            return redirect("task_detail", tarea_id=tarea_id)
    else:
        fecha_limite_value = tarea.get("fecha_limite")
        if isinstance(fecha_limite_value, str) and len(fecha_limite_value) >= 10:
            fecha_limite_value = fecha_limite_value[:10]
        form = TaskForm(
            initial={
                "titulo": tarea.get("titulo"),
                "descripcion": tarea.get("descripcion"),
                "prioridad": tarea.get("prioridad"),
                "estado": tarea.get("estado"),
                "fecha_limite": fecha_limite_value,
                "proyecto_id": tarea.get("proyecto_id"),
                "usuario_asignado_id": tarea.get("usuario_asignado_id"),
            },
            project_choices=proyecto_choices,
            user_choices=user_choices,
        )
    return render(request, "core/task_form.html", {"form": form, "title": "Editar tarea"})


@login_required
def task_delete(request, tarea_id):
    tarea = _get_tarea(tarea_id)
    if tarea and _can_manage_task(request.user, tarea):
        get_document("tareas", tarea_id).delete()
        messages.success(request, "Tarea eliminada.")
    else:
        messages.error(request, "No tienes permisos para eliminar esta tarea.")
    return redirect("task_list")


@login_required
def add_comment(request, tarea_id):
    tarea = _get_tarea(tarea_id)
    if not tarea:
        return redirect("task_list")
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            get_collection("comentarios").add({
                "texto": form.cleaned_data["texto"],
                "tarea_id": tarea_id,
                "autor_id": str(request.user.id),
                "fecha_creacion": datetime.utcnow(),
            })
            messages.success(request, "Comentario agregado.")
    return redirect("task_detail", tarea_id=tarea_id)


@login_required
def profile(request):
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            _ensure_usuario(request.user)
            messages.success(request, "Perfil actualizado.")
            return redirect("profile")
    else:
        form = ProfileForm(instance=request.user)
    tareas = [
        t for t in _collection_list("tareas") if t.get("usuario_asignado_id") == str(request.user.id)
    ]
    return render(request, "core/profile.html", {"form": form, "tareas": tareas})


@login_required
def user_list(request):
    if not _is_administrator(request.user):
        return redirect("dashboard")
    usuarios = _collection_list("usuarios")
    return render(request, "core/user_list.html", {"usuarios": usuarios})


@login_required
def edit_user_role(request, user_id):
    if not _is_administrator(request.user):
        return redirect("dashboard")
    try:
        usuario = User.objects.get(id=int(user_id))
    except (User.DoesNotExist, ValueError):
        messages.error(request, "Usuario no encontrado.")
        return redirect("user_list")
    if request.method == "POST":
        form = UserRoleForm(request.POST)
        if form.is_valid():
            role = form.cleaned_data["rol"]
            usuario.is_staff = role == "Administrador"
            usuario.save()
            _ensure_usuario(usuario)
            messages.success(request, "Rol de usuario actualizado.")
            return redirect("user_list")
    else:
        form = UserRoleForm(initial={"rol": "Administrador" if usuario.is_staff else "Usuario"})
    return render(request, "core/user_role_form.html", {"form": form, "usuario": usuario})
