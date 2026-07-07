from datetime import datetime
import json

from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from .forms import EquipoForm
from .models import Equipo
from prestamo.models import Prestamo

@login_required
def dashboard(request):

    total_equipos = Equipo.objects.count()
    disponibles = Equipo.objects.filter(estado="Disponible").count()
    prestados = Equipo.objects.filter(estado="Prestado").count()
    mantenimiento = Equipo.objects.filter(estado="Mantenimiento").count()

    prestamos_activos = Prestamo.objects.filter(
        estado="Activo"
    ).count()

    equipos_por_estado = (
        Equipo.objects
        .values("estado")
        .annotate(total=Count("id"))
    )

    context = {
        "total_equipos": total_equipos,
        "disponibles": disponibles,
        "prestados": prestados,
        "mantenimiento": mantenimiento,
        "prestamos_activos": prestamos_activos,
        "equipos_json": json.dumps(list(equipos_por_estado)),
    }

    return render(request, 'dashboard.html', context)
    
@login_required
def lista_equipos(request):

    buscar = request.GET.get("buscar", "")
    estado = request.GET.get("estado", "")

    equipos = Equipo.objects.all()

    if buscar:
        equipos = equipos.filter(
            Q(nombre__icontains=buscar)
            | Q(codigo__icontains=buscar)
            | Q(marca__icontains=buscar)
            | Q(modelo__icontains=buscar)
        )
        if estado:
            equipos = equipos.filter(estado=estado)

    estado_disponible = estado == "Disponible"
    estado_prestado = estado == "Prestado"
    estado_mantenimiento = estado == "Mantenimiento"

    context = {
    "equipos": equipos,
    "buscar": buscar,
    "estado_disponible": estado_disponible,
    "estado_prestado": estado_prestado,
    "estado_mantenimiento": estado_mantenimiento,

    "total_equipos": Equipo.objects.count(),
    "disponibles": Equipo.objects.filter(estado="Disponible").count(),
    "prestados": Equipo.objects.filter(estado="Prestado").count(),
    "en_mantenimiento": Equipo.objects.filter(estado="Mantenimiento").count(),
    }

    return render(request, "inventario/lista_equipos.html", context)

@login_required
def crear_equipo(request):

    if request.method == "POST":

        form = EquipoForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("lista_equipos")

    else:
        form = EquipoForm()

    return render(
        request,
        "inventario/crear_equipo.html",
        {"form": form},
    )


@login_required
def editar_equipo(request, pk):

    equipo = get_object_or_404(Equipo, pk=pk)

    if request.method == "POST":

        form = EquipoForm(
            request.POST,
            instance=equipo
        )

        if form.is_valid():
            form.save()
            return redirect("lista_equipos")

    else:

        form = EquipoForm(instance=equipo)

    return render(
        request,
        "inventario/editar_equipo.html",
        {"form": form},
    )


@login_required
def eliminar_equipo(request, pk):

    equipo = get_object_or_404(Equipo, pk=pk)

    if request.method == "POST":
        equipo.delete()
        return redirect("lista_equipos")

    return render(
        request,
        "inventario/eliminar_equipo.html",
        {"equipo": equipo},
    )


@login_required
def reporte_equipos_pdf(request):

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = (
        'attachment; filename="reporte_equipos.pdf"'
    )

    pdf = canvas.Canvas(response, pagesize=letter)

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(
        140,
        760,
        "SISTEMA DE INVENTARIO DE LABORATORIOS"
    )

    pdf.setFont("Helvetica", 12)
    pdf.drawString(
        220,
        740,
        "Reporte de Equipos"
    )

    fecha = datetime.now().strftime("%d/%m/%Y %H:%M")

    pdf.setFont("Helvetica", 10)
    pdf.drawString(
        390,
        720,
        f"Fecha: {fecha}"
    )

    pdf.line(50, 710, 550, 710)

    pdf.setFont("Helvetica-Bold", 10)

    pdf.drawString(50, 690, "Código")
    pdf.drawString(120, 690, "Nombre")
    pdf.drawString(250, 690, "Marca")
    pdf.drawString(350, 690, "Modelo")
    pdf.drawString(450, 690, "Estado")

    y = 670

    pdf.setFont("Helvetica", 9)

    for equipo in Equipo.objects.all():

        pdf.drawString(50, y, str(equipo.codigo))
        pdf.drawString(120, y, str(equipo.nombre))
        pdf.drawString(250, y, str(equipo.marca))
        pdf.drawString(350, y, str(equipo.modelo))
        pdf.drawString(450, y, str(equipo.estado))

        y -= 20

        if y <= 50:
            pdf.showPage()
            y = 760

    pdf.save()

    return response