"""
Formularios de la app 'usuarios'.
 
RegistroForm      → registro de nuevo socio (User + PerfilUsuario)
PerfilForm        → edición de datos del perfil
"""
 
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import PerfilUsuario


class RegistroForm(UserCreationForm):
    """
    Extiende el UserCreationForm de Django agregando los campos
    que necesitamos: nombre, apellido, email y teléfono.
 
    UserCreationForm ya incluye username, password1 y password2
    con todas las validaciones de seguridad de Django.
    """
 
    first_name = forms.CharField(
        max_length=50,
        label='Nombre',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tu nombre'}),
    )
    last_name = forms.CharField(
        max_length=50,
        label='Apellido',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tu apellido'}),
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'tu@email.com'}),
    )
    telefono = forms.CharField(
        max_length=20,
        label='Teléfono / WhatsApp',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 11 2345-6789'}),
    )
 
    class Meta:
        model  = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'username': 'Nombre de usuario',
        }
        help_texts = {
            'username': 'Solo letras, números y los caracteres @/./+/-/_',
        }
 
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Agregar clase form-control a los campos de password generados por Django
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['class'] = 'form-control'
        self.fields['password1'].label = 'Contraseña'
        self.fields['password2'].label = 'Repetir contraseña'
 
    def clean_email(self):
        """Verificar que el email no esté ya registrado."""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Ya existe una cuenta con ese email.')
        return email
 
    def save(self, commit=True):
        """
        Guardamos el User y luego actualizamos el PerfilUsuario
        con el teléfono. El perfil ya fue creado automáticamente
        por la señal en models.py.
        """
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name  = self.cleaned_data['last_name']
        user.email      = self.cleaned_data['email']
 
        if commit:
            user.save()
            # Actualizar el perfil creado por la señal
            user.perfil.telefono = self.cleaned_data.get('telefono', '')
            user.perfil.save()
 
        return user
    
    
class PerfilForm(forms.ModelForm):
    """
    Formulario para que el socio edite sus datos de perfil.
    También permite cambiar nombre, apellido y email del User.
    """
 
    # Campos del User que mostramos en el mismo form
    first_name = forms.CharField(
        max_length=50,
        label='Nombre',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    last_name = forms.CharField(
        max_length=50,
        label='Apellido',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
    )
 
    class Meta:
        model  = PerfilUsuario
        fields = ['telefono', 'numero_socio']
        widgets = {
            'telefono'     : forms.TextInput(attrs={'class': 'form-control'}),
            'numero_socio' : forms.TextInput(attrs={'class': 'form-control'}),
        }
 
    def __init__(self, *args, **kwargs):
        # Recibimos el usuario para pre-cargar sus datos
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['first_name'].initial = self.user.first_name
            self.fields['last_name'].initial  = self.user.last_name
            self.fields['email'].initial      = self.user.email
 
    def save(self, commit=True):
        perfil = super().save(commit=False)
        if self.user:
            self.user.first_name = self.cleaned_data['first_name']
            self.user.last_name  = self.cleaned_data['last_name']
            self.user.email      = self.cleaned_data['email']
            if commit:
                self.user.save()
        if commit:
            perfil.save()
        return perfil