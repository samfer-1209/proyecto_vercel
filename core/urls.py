from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("register/", views.register, name="register"),
    path("projects/", views.project_list, name="project_list"),
    path("projects/create/", views.project_create, name="project_create"),
    path("projects/<str:proyecto_id>/", views.project_detail, name="project_detail"),
    path("projects/<str:proyecto_id>/edit/", views.project_edit, name="project_edit"),
    path("projects/<str:proyecto_id>/delete/", views.project_delete, name="project_delete"),
    path("tasks/", views.task_list, name="task_list"),
    path("tasks/create/", views.task_create, name="task_create"),
    path("tasks/<str:tarea_id>/", views.task_detail, name="task_detail"),
    path("tasks/<str:tarea_id>/edit/", views.task_edit, name="task_edit"),
    path("tasks/<str:tarea_id>/delete/", views.task_delete, name="task_delete"),
    path("tasks/<str:tarea_id>/comment/", views.add_comment, name="add_comment"),
    path("profile/", views.profile, name="profile"),
    path("users/", views.user_list, name="user_list"),
    path("users/<str:user_id>/role/", views.edit_user_role, name="edit_user_role"),
]
