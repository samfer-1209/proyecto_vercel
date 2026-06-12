from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class UsuarioDocumento:
    id: str
    email: str
    nombre: str
    apellido: str
    rol: str
    fecha_creacion: datetime


@dataclass
class ProyectoDocumento:
    id: str
    nombre: str
    descripcion: str
    fecha_creacion: datetime
    propietario_id: str
    estado: str


@dataclass
class TareaDocumento:
    id: str
    titulo: str
    descripcion: str
    prioridad: str
    estado: str
    fecha_limite: Optional[datetime]
    fecha_creacion: datetime
    proyecto_id: str
    usuario_asignado_id: str


@dataclass
class ComentarioDocumento:
    id: str
    tarea_id: str
    autor_id: str
    texto: str
    fecha_creacion: datetime
