# Arquivo: /mapeamento-habilidades/habilidades/urls.py
# (MANTIDO ORIGINALMENTE)

from django.urls import path
from . import views

# O namespace é OBRIGATÓRIO, pois o base.html usa 'habilidades:...'
app_name = 'habilidades'

urlpatterns = [
    # Rotas de Navegação
    path('', views.index, name='index'),
    path('cadastro/perfil/', views.cadastro_perfil_view, name='cadastro_perfil'),
    path('busca/', views.busca_habilidade_view, name='busca_habilidade'),
    path('projetos/', views.lista_projetos_view, name='lista_projetos'),
    
    # Rota para Criar Novo Projeto 
    path('projetos/novo/', views.criar_projeto_view, name='criar_projeto'), 
    path('projetos/<int:projeto_id>/', views.detalhes_projeto_view, name='detalhes_projeto'),
    path('projetos/<int:projeto_id>/participar/', views.participar_projeto_view, name='participar_projeto'),
    path('projetos/<int:projeto_id>/gerenciar/', views.gerenciar_projeto_view, name='gerenciar_projeto'),
    path('projetos/<int:projeto_id>/editar/', views.editar_projeto_view, name='editar_projeto'),
    
    path('comunidade/', views.comunidade_view, name='comunidade'),

    # Rotas de Autenticação
    path('login/', views.login_view, name='login'), 
    path('logout/', views.logout_view, name='logout'), 

    # Rotas de Perfil
    path('perfil/<int:usuario_id>/', views.perfil_usuario_view, name='perfil_usuario'),
    path('perfil/editar/', views.editar_perfil_view, name='editar_perfil'),
]