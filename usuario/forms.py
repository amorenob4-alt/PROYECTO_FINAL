from django import forms
from django.contrib.auth.models import User


class UsuarioForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for campo in self.fields.values():
            campo.widget.attrs['class'] = 'form-control'
            
    password = forms.CharField(
        widget=forms.PasswordInput(),
        label="Contraseña"
    )

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "password",
            
        ]

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.set_password(self.cleaned_data["password"])

        if commit:
            usuario.save()

        return usuario