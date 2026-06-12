from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils import timezone

STATUS_CHOICES = [
    ("Pendiente", "Pendiente"),
    ("En progreso", "En progreso"),
    ("Completada", "Completada"),
]

PRIORITY_CHOICES = [
    ("Baja", "Baja"),
    ("Media", "Media"),
    ("Alta", "Alta"),
]

ROLE_CHOICES = [
    ("Usuario", "Usuario"),
    ("Administrador", "Administrador"),
]


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(label="Correo electrónico", required=True)
    first_name = forms.CharField(label="Nombre", max_length=150, required=True)
    last_name = forms.CharField(label="Apellido", max_length=150, required=True)
    rol = forms.ChoiceField(
        label="Rol",
        choices=ROLE_CHOICES,
        initial="Usuario",
        help_text="El primer registrado puede ser Administrador. Los demás serán Usuarios.",
        required=False,
    )

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "password1", "password2"]
    
    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
        return user


class ProfileForm(forms.ModelForm):
    email = forms.EmailField(label="Correo electrónico", required=True)
    first_name = forms.CharField(label="Nombre", required=True)
    last_name = forms.CharField(label="Apellido", required=True)

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]


class ProjectForm(forms.Form):
    nombre = forms.CharField(label="Nombre del proyecto", max_length=200)
    descripcion = forms.CharField(label="Descripción", widget=forms.Textarea(attrs={"rows": 4}))
    estado = forms.ChoiceField(label="Estado", choices=STATUS_CHOICES)


class TaskForm(forms.Form):
    titulo = forms.CharField(label="Título", max_length=200)
    descripcion = forms.CharField(label="Descripción", widget=forms.Textarea(attrs={"rows": 4}))
    prioridad = forms.ChoiceField(label="Prioridad", choices=PRIORITY_CHOICES)
    estado = forms.ChoiceField(label="Estado", choices=STATUS_CHOICES)
    fecha_limite = forms.DateField(label="Fecha límite", required=False, widget=forms.DateInput(attrs={"type": "date"}))
    proyecto_id = forms.ChoiceField(label="Proyecto")
    usuario_asignado_id = forms.ChoiceField(label="Usuario asignado")

    def __init__(self, *args, project_choices=None, user_choices=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["proyecto_id"].choices = project_choices or []
        self.fields["usuario_asignado_id"].choices = user_choices or []

    def clean_fecha_limite(self):
        fecha = self.cleaned_data.get("fecha_limite")
        if fecha and fecha < timezone.localdate():
            raise forms.ValidationError("La fecha límite no puede ser anterior a hoy.")
        return fecha


class CommentForm(forms.Form):
    texto = forms.CharField(
        label="Comentario",
        widget=forms.Textarea(attrs={"rows": 2, "placeholder": "Escribe tu comentario aquí..."}),
        max_length=500,
    )


class UserRoleForm(forms.Form):
    rol = forms.ChoiceField(label="Rol", choices=ROLE_CHOICES)
