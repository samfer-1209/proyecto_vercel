from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from unittest.mock import patch
from .forms import ProjectForm, TaskForm, UserRegistrationForm


class FormValidationTest(TestCase):
    def test_project_form_valid(self):
        form = ProjectForm({
            "nombre": "Proyecto Alpha",
            "descripcion": "Descripción del proyecto.",
            "estado": "Pendiente",
        })
        self.assertTrue(form.is_valid())

    def test_task_form_fecha_limite_valida(self):
        form = TaskForm(
            {
                "titulo": "Tarea 1",
                "descripcion": "Descripción de tarea.",
                "prioridad": "Alta",
                "estado": "Pendiente",
                "fecha_limite": "2099-12-31",
                "proyecto_id": "1",
                "usuario_asignado_id": "1",
            },
            project_choices=[("1", "Proyecto")],
            user_choices=[("1", "Usuario")],
        )
        self.assertTrue(form.is_valid())

    def test_registration_form_requires_email(self):
        form = UserRegistrationForm(
            {
                "username": "usuario",
                "password1": "ComplexPass123",
                "password2": "ComplexPass123",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)


class RegistrationViewTest(TestCase):
    @patch("core.views._ensure_usuario")
    def test_register_creates_user_and_redirects(self, mock_sync):
        response = self.client.post(
            reverse("register"),
            {
                "username": "nuevo",
                "email": "nuevo@example.com",
                "first_name": "Nuevo",
                "last_name": "Usuario",
                "password1": "ComplexPass123",
                "password2": "ComplexPass123",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username="nuevo").exists())
        mock_sync.assert_called()
