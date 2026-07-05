
from django.contrib.auth.decorators import login_required
from django.shortcuts import render,redirect
from .models import Prestamo,Devolucion
from .forms import PrestamoForm
from .forms import DevolucionForm
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from datetime import datetime
from .models import Prestamo
from django.contrib.auth.decorators import login_required


@login_required
def lista_prestamos(request):
    prestamos = Prestamo.objects.select_related(
        "usuario",
        "equipo"
    ).all()

    return render(
        request,
        "prestamo/lista_prestamos.html",
        {"prestamos": prestamos}
    )

@login_required
def crear_prestamo(request):
    if request.method == "POST":
        form = PrestamoForm(request.POST)

        if form.is_valid():
            prestamo = form.save(commit=False)

            # Asignar el usuario que inició sesión
            prestamo.usuario = request.user

            # Verificar disponibilidad
            if prestamo.equipo.estado != "Disponible":
                form.add_error(
                    "equipo",
                    "Este equipo no está disponible."
                )
            else:
                prestamo.save()
                return redirect("lista_prestamos")

    else:
        form = PrestamoForm()

    return render(request, "prestamo/crear_prestamo.html", {
        "form": form
    })

@login_required
def crear_devolucion(request):
    if request.method == "POST":
        form = DevolucionForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("lista_prestamos")

    else:
        form = DevolucionForm()

    return render(request, "prestamo/crear_devolucion.html", {
        "form": form
    })

@login_required
def reporte_prestamos_pdf(request):

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte_prestamos.pdf"'

    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    #  Título
    p.drawCentredString(width / 2, 750, "REPORTE DE PRÉSTAMOS")

    #  Fecha
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M")
    p.setFont("Helvetica", 10)
    p.drawString(420, 730, f"Fecha: {fecha}")

    #  Línea
    p.line(50, 720, 550, 720)

    #  Encabezados
    p.setFont("Helvetica-Bold", 10)
    p.drawString(50, 690, "Usuario")
    p.drawString(150, 690, "Equipo")
    p.drawString(280, 690, "F. Préstamo")
    p.drawString(380, 690, "F. Devolución")
    p.drawString(480, 690, "Estado")

    y = 670
    p.setFont("Helvetica", 9)

    prestamos = Prestamo.objects.select_related("usuario", "equipo")

    for pr in prestamos:
        p.drawString(50, y, str(pr.usuario.username))
        p.drawString(150, y, str(pr.equipo.nombre))
        p.drawString(280, y, str(pr.fecha_prestamo.date()))
        p.drawString(380, y, str(pr.fecha_devolucion) if pr.fecha_devolucion else "-")
        p.drawString(480, y, str(pr.estado))

        y -= 20

        if y < 50:
            p.showPage()
            y = 750

    p.save()
    return response


@login_required
def dashboard(request):

    is_admin = request.user.groups.filter(name="Admin").exists()
    is_usuario = request.user.groups.filter(name="Usuario").exists()

    return render(request, "dashboard.html", {
        "is_admin": is_admin,
        "is_usuario": is_usuario,
    })

