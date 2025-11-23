# habilidades/forms.py
from django import forms
from .models import Usuario, Habilidade

# Para usar o Custom User Model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.utils.translation import gettext_lazy as _

class UsuarioCreationForm(UserCreationForm):
    """
    Formulário para criar um novo usuário (registro),
    incluindo campos customizados.
    """
    class Meta(UserCreationForm.Meta):
        model = Usuario
        fields = UserCreationForm.Meta.fields + ('curso', 'campus') # Adiciona campos customizados

class PerfilUsuarioForm(forms.ModelForm):
    """
    Formulário para o usuário editar seus dados no perfil (após o registro).
    Usado para preencher as Seções 1, 2, e 4 do seu layout.
    """
    # Exemplo de campo customizado que não está no seu modelo Usuario, mas no seu design:
    # sobre_mim = forms.CharField(label=_("Sobre mim (Biografia)"), widget=forms.Textarea, required=False)

    class Meta:
        model = Usuario
        # Inclua todos os campos que o usuário deve poder editar no perfil
        fields = ('first_name', 'last_name', 'curso', 'campus')

        labels = {
            'first_name': _("Nome Completo"),
            'last_name': _("Sobrenome"), # Se você usar first_name/last_name para Nome/Sobrenome
            'curso': _("Curso"),
            'campus': _("Campus"),
        }

class HabilidadesForm(forms.ModelForm):
    """
    Formulário para o usuário selecionar suas habilidades (Seção 3).
    """
    # O campo ManyToMany é mais complexo e requer JS (como Select2) no front.
    habilidades = forms.ModelMultipleChoiceField(
        queryset=Habilidade.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-select'}),
        required=False,
        label=_("Habilidades e Competências")
    )

    class Meta:
        model = Usuario # O formulário se vincula ao Usuario para salvar as habilidades
        fields = ('habilidades',) # Apenas o campo de habilidades

class UsuarioCreationForm(UserCreationForm):
    """
    Formulário para criar um novo usuário (Registro) no SkillMap.
    Adiciona os campos customizados (curso e campus) do modelo Usuario.
    """
    class Meta(UserCreationForm.Meta):
        model = Usuario
        # Adiciona os campos customizados
        fields = UserCreationForm.Meta.fields + ('curso', 'campus') 
        
    # Adicionar classes Tailwind ao campo de entrada (Input)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if field in ['username', 'email', 'password', 'password2', 'curso']:
                 self.fields[field].widget.attrs.update({
                    'class': 'form-input flex w-full min-w-0 flex-1 rounded-lg border border-border-light dark:border-border-dark bg-input-bg-light dark:bg-input-bg-dark h-12 px-4 text-base font-normal',
                    'placeholder': self.fields[field].label
                 })
            elif field == 'campus':
                 self.fields[field].widget.attrs.update({
                    'class': 'form-select flex w-full min-w-0 flex-1 rounded-lg border border-border-light dark:border-border-dark bg-input-bg-light dark:bg-input-bg-dark h-12 px-4 text-base font-normal',
                 })