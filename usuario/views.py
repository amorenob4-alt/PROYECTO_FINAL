from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .forms import UsuarioForm
from django.contrib import messages


@login_required
def lista_usuarios(request):

    usuarios = User.objects.all()

    return render(
        request,
        "usuario/lista_usuarios.html",
        {
            "usuarios": usuarios
        }
    )


@login_required
def crear_usuario(request):

    if request.method == "POST":

        form = UsuarioForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("lista_usuarios")

    else:

        form = UsuarioForm()

    return render(
        request,
        "usuario/crear_usuario.html",
        {
            "form": form
        }
    )
def registro(request):

    if request.method == "POST":

        form = UsuarioForm(request.POST)

        if form.is_valid():
            usuario = form.save(commit=False)
            usuario.is_active = True
            usuario.save()

            messages.success(request, "Usuario registrado correctamente.")
            return redirect("login")

    else:

        form = UsuarioForm()

    return render(
        request,
        "usuario/registro.html",
        {
            "form": form
        }
    )
