from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('equipos/', views.lista_equipos, name='lista_equipos'),
    path("equipos/nuevo/", views.crear_equipo, name="crear_equipo"),
    path("equipos/<int:pk>/editar/", views.editar_equipo, name="editar_equipo"),
    path("equipos/<int:pk>/eliminar/", views.eliminar_equipo, name="eliminar_equipo"),
    path("reporte/equipos/pdf/", views.reporte_equipos_pdf, name="reporte_equipos_pdf"),
]