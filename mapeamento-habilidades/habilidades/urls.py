# /habilidades/urls.py
from django.urls import path
from . import views

# O namespace é OBRIGATÓRIO, pois o base.html usa 'habilidades:...'
app_name = 'habilidades'

urlpatterns = [
    # Rotas de Navegação (Mapeamento dos links do base.html)
    path('', views.index, name='index'),
    path('cadastro/perfil/', views.cadastro_perfil_view, name='cadastro_perfil'),
    path('busca/', views.busca_habilidade_view, name='busca_habilidade'),
    path('projetos/', views.lista_projetos_view, name='lista_projetos'),
    path('comunidade/', views.comunidade_view, name='comunidade'),

    # Rotas de Autenticação
    path('login/', views.login_view, name='login'), 
    path('logout/', views.logout_view, name='logout'), 

    # Rotas de Perfil
    path('perfil/editar/', views.editar_perfil_view, name='editar_perfil'),
    path('perfil/<int:usuario_id>/', views.perfil_usuario_view, name='perfil_usuario'),
]