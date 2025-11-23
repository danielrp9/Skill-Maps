# /habilidades/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout

# --- Views Simples (Placeholders para Templates) ---

def index(request):
    """Página Inicial do SkillMap."""
    return render(request, 'habilidades/index.html') 

def cadastro_perfil_view(request):
    """View para servir o template de CADASTRO/REGISTRO inicial."""
    # CORREÇÃO: Chamando o nome do arquivo exatamente como ele está no disco.
    return render(request, 'habilidades/cadastrar_perfil.html') 

def busca_habilidade_view(request):
    """View para a página de BUSCA e FILTROS. Requer template: busca_habilidade.html"""
    return render(request, 'habilidades/busca_habilidade.html')

def lista_projetos_view(request):
    """View para a página de LISTA de projetos. Requer template: lista_projetos.html"""
    return render(request, 'habilidades/lista_projetos.html')

def comunidade_view(request):
    """View para a página de FÓRUM/Voz da Comunidade. Requer template: comunidade.html"""
    # NOTE: Este arquivo 'comunidade.html' pode estar faltando. Crie-o!
    return render(request, 'habilidades/comunidade.html') 

# --- Views de Autenticação ---

def login_view(request):
    """View placeholder para a página de login. Requer template: login.html"""
    return render(request, 'habilidades/login.html') 

def logout_view(request):
    """View que faz logout (implementação real será diferente)."""
    # Você deve implementar a lógica de token e sessão aqui. Por enquanto, apenas renderiza home.
    return render(request, 'habilidades/index.html') 

# --- Views de Perfil ---

@login_required
def editar_perfil_view(request):
    """View para EDIÇÃO de perfil. Requer template: editar_perfil.html"""
    # NOTE: Este arquivo 'editar_perfil.html' pode estar faltando. Crie-o!
    return render(request, 'habilidades/editar_perfil.html') 

def perfil_usuario_view(request, usuario_id):
    """View para visualização de perfil de outro usuário. Requer template: perfil_usuario.html"""
    return render(request, 'habilidades/perfil_usuario.html', {'usuario_id': usuario_id})