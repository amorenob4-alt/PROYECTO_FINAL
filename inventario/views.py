from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from django.http import HttpResponse

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

from datetime import datetime
import json

from .models import Equipo
from .forms import EquipoForm
from prestamo.models import Prestamo

@login_required
def dashboard(request):
    # 1. Conteo de equipos por estado
    total_equipos = Equipo.objects.count()
    disponibles = Equipo.objects.filter(estado='Disponible').count()
    prestados = Equipo.objects.filter(estado='Prestado').count()
    mantenimiento = Equipo.objects.filter(estado='Mantenimiento').count()

    # 2. Conteo de préstamos activos de la otra app
    prestamos_activos = Prestamo.objects.filter(estado='Activo').count()

    # 3. Agrupación y conteo para alimentar el gráfico de Chart.js
    equipos_por_estado = Equipo.objects.values('estado').annotate(total=Count('id'))
    
    # Convertimos los datos a JSON string para que el JavaScript del HTML lo pueda leer
    equipos_json = json.dumps(list(equipos_por_estado))

    # 4. Enviamos todas las variables al HTML
    context = {
        'total_equipos': total_equipos,
        'disponibles': disponibles,
        'prestados': prestados,
        'mantenimiento': mantenimiento,
        'prestamos_activos': prestamos_activos,
        'equipos_json': equipos_json,
    }

    return render(request, 'dashboard.html', context)

@login_required
def lista_equipos(request):
    buscar = request.GET.get("buscar")

    equipos = Equipo.objects.all()

    if buscar:
        equipos = equipos.filter(
            Q(nombre__icontains=buscar) |
            Q(codigo__icontains=buscar) |
            Q(marca__icontains=buscar) |
            Q(modelo__icontains=buscar)
        )

    return render(request, "inventario/lista_equipos.html", {
        "equipos": equipos
    })

@login_required
def crear_equipo(request):
    if request.method == "POST":
        form = EquipoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("lista_equipos")
    else:
        form = EquipoForm()

    return render(request, "inventario/crear_equipo.html", {
        "form": form

})
@login_required
def editar_equipo(request, pk):
    equipo = get_object_or_404(Equipo, pk=pk)

    if request.method == "POST":
        form = EquipoForm(request.POST, instance=equipo)
        if form.is_valid():
            form.save()
            return redirect("lista_equipos")
    else:
        form = EquipoForm(instance=equipo)

    return render(request, "inventario/editar_equipo.html", {
        "form": form
    })
@login_required
def eliminar_equipo(request, pk):
    equipo = get_object_or_404(Equipo, pk=pk)

    if request.method == "POST":
        equipo.delete()
        return redirect("lista_equipos")

    return render(request, "inventario/eliminar_equipo.html", {
        "equipo": equipo
    })

@login_required
def reporte_equipos_pdf(request):

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte_equipos.pdf"'

    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    #  Título
    p.setFont("Helvetica-Bold", 16)
    p.drawString(180, 750, "SISTEMA DE PRÉSTAMOS DE LABORATORIO")

    #  Subtítulo
    p.setFont("Helvetica", 12)
    p.drawString(250, 730, "Reporte de Equipos")

    #  Fecha
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M")
    p.setFont("Helvetica", 10)
    p.drawString(420, 710, f"Fecha: {fecha}")

    #  Línea separadora
    p.line(50, 700, 550, 700)

    #  Encabezados tabla
    p.setFont("Helvetica-Bold", 10)
    p.drawString(50, 670, "Código")
    p.drawString(120, 670, "Nombre")
    p.drawString(250, 670, "Marca")
    p.drawString(350, 670, "Modelo")
    p.drawString(450, 670, "Estado")

    y = 650
    p.setFont("Helvetica", 9)

    equipos = Equipo.objects.all()

    for e in equipos:
        p.drawString(50, y, str(e.codigo))
        p.drawString(120, y, str(e.nombre))
        p.drawString(250, y, str(e.marca))
        p.drawString(350, y, str(e.modelo))
        p.drawString(450, y, str(e.estado))

        y -= 20

        #  nueva página si se llena
        if y < 50:
            p.showPage()
            y = 750

    p.save()
    return response