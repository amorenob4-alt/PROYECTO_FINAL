from django.urls import path
from . import views

urlpatterns = [
    path( "",views.lista_prestamos,name="lista_prestamos"),
    path( "nuevo/",views.crear_prestamo,name="crear_prestamo"),
    path("reporte/pdf/", views.reporte_prestamos_pdf, name="reporte_prestamos_pdf"),
    
    
]