from django import forms
from .models import Prestamo
from inventario.models import Equipo
from .models import Devolucion,Prestamo

class PrestamoForm(forms.ModelForm):
    class Meta:
        model = Prestamo
        fields = ['equipo', 'fecha_devolucion']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['equipo'].queryset = Equipo.objects.filter(
            estado='Disponible'
        )
class DevolucionForm(forms.ModelForm):
    class Meta:
        model = Devolucion
        fields = ['prestamo', 'observaciones']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['prestamo'].queryset = Prestamo.objects.filter(
            estado="Activo"
        )