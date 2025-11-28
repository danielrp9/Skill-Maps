# Arquivo: /mapeamento-habilidades/habilidades/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout as auth_logout
from django import forms
from django.urls import reverse # Import necessário para redirecionamento correto
from django.contrib import messages
from django.http import HttpRequest
import requests
import json # Adicionado para melhor manipulação de JSON

# Variável de configuração da API (URL Base)
API_BASE_URL = "http://localhost:8001/api/v1"

# from .models import UserProfile # Descomente e ajuste quando tiver seu modelo

# --- Placeholder de Modelo e Formulário para Edição ---
# **AVISO:** Substitua isso pelos seus modelos e formulários reais.
class FakeUserProfile:
    """Modelo fake para simular o UserProfile (A SER REMOVIDO)"""
    def __init__(self, user):
        self.user = user
        self.avatar_url = "https://placehold.co/128x128/13ec5b/0d1b12?text=Foto"
        self.lattes_url = "http://lattes.cnpq.br/123456789"
        self.linkedin_url = "https://linkedin.com/in/exemplo"
        self.curso_ou_departamento = "Sistemas de Informação"
        self.campus = "JK"
        self.biografia = "Estudante apaixonado por resolver problemas complexos com tecnologia."

class UserProfileForm(forms.Form):
    """Formulário fake para demonstrar a view (A SER REMOVIDO)"""
    nome = forms.CharField(max_length=150)
    curso_departamento = forms.CharField(max_length=100, required=False)
    campus = forms.CharField(max_length=10)
    biografia = forms.CharField(max_length=300, widget=forms.Textarea, required=False)
    lattes_url = forms.URLField(required=False)
    linkedin_url = forms.URLField(required=False)

# Novo formulário placeholder para Criação de Projeto
# AJUSTADO para mapear Descrição Completa (do template) para Propósito (da API)
class ProjectCreationForm(forms.Form):
    titulo = forms.CharField(max_length=100, label="Título do Projeto")
    # O campo 'proposito' é usado para coletar a Descrição Completa do template
    proposito = forms.CharField(widget=forms.Textarea, label="Descrição Completa")
    # Estes campos estão no template, mas serão ignorados na chamada da API neste momento
    habilidades_requeridas = forms.CharField(max_length=255, label="Habilidades Requeridas", required=False)
    status = forms.ChoiceField(choices=[('AB', 'Aberto'), ('PR', 'Em Progresso')], label="Status Inicial")


# Função para simular a obtenção do perfil (A SER REMOVIDO)
def get_user_profile(user):
    # Simula a criação de um perfil fake para o usuário logado
    # Na implementação real, use: return user.userprofile
    if not hasattr(user, 'userprofile'):
        setattr(user, 'userprofile', FakeUserProfile(user))
    return user.userprofile

# --- Views Simples (Placeholders para Templates) ---

def index(request):
    """Página Inicial do SkillMap."""
    return render(request, 'habilidades/index.html') 

def busca_habilidade_view(request):
    """View para a página de BUSCA e FILTROS. Requer template: busca_habilidade.html"""
    return render(request, 'habilidades/busca_habilidade.html')

def lista_projetos_view(request):
    """View para a página de LISTA de projetos. Requer template: lista_projetos.html"""
    
    user_id = request.session.get('user_id') 
    projetos = []
    
    endpoint = f"{API_BASE_URL}/projetos/"
    
    try:
        response = requests.get(endpoint, timeout=10)

        if response.status_code == 200:
            projetos = response.json()
        elif response.status_code == 404:
            messages.info(request, "Nenhum projeto foi encontrado.")
        else:
            messages.error(request, f"Erro ao buscar projetos: Status {response.status_code}. Detalhe: {response.text}")

    except requests.exceptions.ConnectionError:
        messages.error(request, 'Não foi possível conectar ao Backend (Docker). Verifique se o serviço está ativo.')
    except Exception as e:
        messages.error(request, f'Ocorreu um erro inesperado: {e}')
        
    context = {
        'projetos': projetos,
        'user_id': user_id,
    }
    
    return render(request, 'habilidades/lista_projetos.html', context)

def comunidade_view(request):
    """View para a página de FÓRUM/Voz da Comunidade. Requer template: comunidade.html"""
    return render(request, 'habilidades/comunidade.html') 

# --- Views de Autenticação ---

def cadastro_perfil_view(request: HttpRequest):
    """
    View para REGISTRO de usuário. Envia dados completos para o endpoint /auth/register da API.
    """
    context = {} 
    
    if request.method == 'POST':
        # 1. Obter dados do formulário
        username = request.POST.get('username', '')
        email = request.POST.get('email', '')
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')
        
        # CAMPOS ACADÊMICOS OBRIGATÓRIOS
        campus = request.POST.get('campus', '')
        curso = request.POST.get('curso', '')
        
        context['form_data'] = request.POST 
        
        if password != password2:
            messages.error(request, "As senhas não coincidem.")
            return render(request, 'habilidades/cadastrar_perfil.html', context)

        # 2. Comunicação com a API: Enviando todos os campos necessários
        endpoint = f"{API_BASE_URL}/auth/register"
        payload = {"username": username, "email": email, "password": password, "campus": campus, "curso": curso}
        headers = {'Content-Type': 'application/json'}

        try:
            response = requests.post(endpoint, json=payload, headers=headers, timeout=10)
            
            error_detail = response.text 
            try:
                error_data = response.json()
                if isinstance(error_data, dict) and 'detail' in error_data:
                    error_detail = error_data.get('detail', error_detail)
                elif isinstance(error_data, list):
                    error_detail = json.dumps(error_data)
            except requests.exceptions.JSONDecodeError:
                pass 

            if response.status_code == 201: 
                messages.success(request, "Usuário registrado com sucesso! Faça login para continuar.")
                return redirect(reverse('habilidades:login'))
            
            elif response.status_code == 422:
                messages.error(request, f"Erro de validação da API (422): Verifique se preencheu todos os campos. Detalhe: {error_detail}")

            elif response.status_code != 200:
                messages.error(request, f'Falha no registro: Status {response.status_code}. Detalhe: {error_detail}')

        except requests.exceptions.ConnectionError:
            messages.error(request, 'Não foi possível conectar ao Backend. Verifique se o Docker está rodando na porta 8001.')
        except requests.exceptions.Timeout:
            messages.error(request, 'Tempo limite esgotado (Timeout). O Backend pode estar lento. Tente novamente.')
        except Exception as e:
            messages.error(request, f'Ocorreu um erro: {e}')
            
    return render(request, 'habilidades/cadastrar_perfil.html', context)


def login_view(request: HttpRequest):
    """
    View que se conecta à API para checar a existência do usuário e salvar o ID na sessão.
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        
        if not username:
            messages.error(request, 'O campo Usuário é obrigatório.')
            return render(request, 'habilidades/login.html')
        
        endpoint = f"{API_BASE_URL}/auth/check-user"
        payload = {"username": username}
        
        try:
            response = requests.post(endpoint, json=payload)
            
            if response.status_code == 200:
                user_data = response.json()
                user_id = user_data.get('id')
                
                request.session['user_id'] = user_id
                request.session['username'] = user_data.get('username') 
                
                messages.success(request, f'Bem-vindo(a), {username}! Você está logado via API ID: {user_id}.')
                return redirect(reverse('habilidades:index')) 
            
            elif response.status_code == 404:
                messages.error(request, 'Usuário não encontrado. Verifique o nome de usuário na API.')
            
            else:
                messages.error(request, f'Erro inesperado na API de Login: Status {response.status_code}')

        except requests.exceptions.ConnectionError:
            messages.error(request, 'Não foi possível conectar ao Backend. Verifique se o Docker está rodando na porta 8001.')
        except Exception as e:
            messages.error(request, f'Ocorreu um erro: {e}')

    return render(request, 'habilidades/login.html') 

def logout_view(request):
    """View que faz logout, limpando a sessão."""
    if 'user_id' in request.session:
        del request.session['user_id']
    if 'username' in request.session:
        del request.session['username']
    
    auth_logout(request)
    
    messages.info(request, "Logout realizado com sucesso.")
    return redirect(reverse('habilidades:index'))

# --- Views de Perfil ---

def editar_perfil_view(request: HttpRequest):
    """
    Carrega o formulário de edição com dados existentes do usuário logado (GET)
    e envia as alterações via PATCH para a API (POST).
    """
    user_id = request.session.get('user_id')
    
    if not user_id:
        messages.warning(request, 'Você precisa estar logado para editar seu perfil.')
        return redirect('habilidades:login')

    user_endpoint = f"{API_BASE_URL}/usuarios/{user_id}"
    
    try:
        # 1. Obter dados atuais do usuário (GET)
        user_response = requests.get(user_endpoint, timeout=10)
        
        if user_response.status_code != 200:
            messages.error(request, 'Erro ao carregar dados do perfil.')
            return redirect('habilidades:perfil_usuario', usuario_id=user_id)
            
        user_data = user_response.json()

        if request.method == 'POST':
            # Note: O nome é hardcoded no template, use request.POST.get('nome')
            form = UserProfileForm(request.POST) 
            if form.is_valid():
                
                # 2. Enviar dados atualizados para a API (PATCH)
                # Assumimos que o backend ProjectUpdate schema agora aceita todos esses campos
                payload = {
                    "username": user_data.get('username'), 
                    "email": form.cleaned_data['email'],
                    "curso": form.cleaned_data['curso'],
                    "campus": form.cleaned_data['campus'],
                    "whatsapp": form.cleaned_data['whatsapp'], 
                    "discord": form.cleaned_data['discord'],
                    "telegram": form.cleaned_data['telegram'],
                    "biografia": form.cleaned_data['biografia'],
                    "lattes_url": form.cleaned_data['lattes_url'],
                    "linkedin_url": form.cleaned_data['linkedin_url'],
                }
                
                patch_response = requests.patch(user_endpoint, json=payload, timeout=10)
                
                if patch_response.status_code == 200:
                    messages.success(request, 'Perfil atualizado com sucesso!')
                    return redirect('habilidades:perfil_usuario', usuario_id=user_id)
                else:
                    messages.error(request, f"Falha ao atualizar perfil: Status {patch_response.status_code}. Detalhe: {patch_response.text}")
        
        else:
            # GET: Preencher o formulário com dados existentes
            initial_data = {
                # Nome é um campo fake no backend, mas preenchemos com username/nome
                'nome': user_data.get('username'), 
                'curso': user_data.get('curso'),
                'campus': user_data.get('campus'),
                'email': user_data.get('email'),
                'biografia': user_data.get('biografia'),
                'whatsapp': user_data.get('whatsapp', ''),
                'discord': user_data.get('discord', ''),
                'telegram': user_data.get('telegram', ''),
                'lattes_url': user_data.get('lattes_url', ''),
                'linkedin_url': user_data.get('linkedin_url', ''),
                
            }
            form = UserProfileForm(initial=initial_data)

    except requests.exceptions.RequestException as e:
        messages.error(request, f'Erro de conexão: {e}')
        form = UserProfileForm()
    
    context = {'form': form}
    return render(request, 'habilidades/editar_perfil.html', context)



def criar_projeto_view(request: HttpRequest):
    """
    View para criação de um novo projeto, utilizando o user_id da sessão.
    Mapeia o campo 'proposito' do form (que é a Descrição Completa no template) para 'proposito' da API.
    """
    # Checagem de login usando a sessão da API
    user_id = request.session.get('user_id')
    
    if not user_id:
        messages.warning(request, 'Você precisa estar logado (via API) para criar um projeto.')
        return redirect('habilidades:login') # Redireciona para o login
        
    if request.method == 'POST':
        form = ProjectCreationForm(request.POST)
        if form.is_valid():
            # 1. Obter dados limpos e preparar o payload
            titulo = form.cleaned_data['titulo']
            # O campo 'proposito' do formulário contém a descrição completa do usuário, que é o 'proposito' para a API
            proposito = form.cleaned_data['proposito'] 

            endpoint = f"{API_BASE_URL}/projetos/"
            payload = {"titulo": titulo, "proposito": proposito, "owner_id": user_id}
            
            try:
                response = requests.post(endpoint, json=payload, timeout=10) # Adicionando timeout

                if response.status_code == 201 or response.status_code == 200: 
                    messages.success(request, "Projeto criado com sucesso na API!")
                    return redirect(reverse('habilidades:lista_projetos'))
                
                else:
                    messages.error(request, f'Falha ao criar projeto na API. Status: {response.status_code}. Detalhe: {response.text}')

            except requests.exceptions.ConnectionError:
                messages.error(request, 'Não foi possível conectar ao Backend (FastAPI).')
            except requests.exceptions.Timeout:
                messages.error(request, 'Tempo limite esgotado. O Backend pode estar lento.')
            except Exception as e:
                messages.error(request, f'Ocorreu um erro ao enviar para a API: {e}')
            
    else:
        form = ProjectCreationForm()

    context = {
        'form': form
    }
    return render(request, 'habilidades/criar_projeto.html', context)

def editar_projeto_view(request: HttpRequest, projeto_id):
    """
    Carrega o formulário de edição com dados existentes e trata o envio (PATCH).
    """
    user_id = request.session.get('user_id')
    
    if not user_id:
        messages.warning(request, 'Você precisa estar logado para editar projetos.')
        return redirect('habilidades:login')

    # 1. Obter dados do projeto existente (GET)
    project_endpoint = f"{API_BASE_URL}/projetos/{projeto_id}" # ASSUMINDO QUE EXISTE UMA ROTA GET POR ID
    
    try:
        response = requests.get(project_endpoint, timeout=10)
        
        if response.status_code == 200:
            projeto_data = response.json()
        elif response.status_code == 404:
            messages.error(request, 'Projeto não encontrado.')
            return redirect('habilidades:lista_projetos')
        else:
            messages.error(request, f'Erro ao carregar projeto: Status {response.status_code}')
            return redirect('habilidades:lista_projetos')

    except requests.exceptions.RequestException as e:
        messages.error(request, f'Erro de conexão ao buscar projeto: {e}')
        return redirect('habilidades:lista_projetos')

    # Checagem de Owner (Apenas o criador pode editar)
    if projeto_data.get('owner_id') != int(user_id):
        messages.error(request, 'Você não tem permissão para editar este projeto.')
        return redirect('habilidades:detalhes_projeto', projeto_id=projeto_id)

    if request.method == 'POST':
        form = ProjectCreationForm(request.POST)
        if form.is_valid():
            # 2. Enviar dados atualizados para a API (PATCH)
            endpoint_patch = f"{API_BASE_URL}/projetos/{projeto_id}"
            
            # Payload para atualização (PATCH)
            payload = {
                "titulo": form.cleaned_data['titulo'],
                "proposito": form.cleaned_data['proposito'],
                "status": form.cleaned_data['status'],
                "campus": form.cleaned_data['campus'], # NOVO
                # Habilidades serão tratadas em outra etapa
            }
            
            try:
                patch_response = requests.patch(endpoint_patch, json=payload, timeout=10)
                
                if patch_response.status_code == 200:
                    messages.success(request, 'Projeto atualizado com sucesso!')
                    return redirect('habilidades:detalhes_projeto', projeto_id=projeto_id)
                else:
                    messages.error(request, f'Falha ao atualizar projeto na API: Status {patch_response.status_code}.')

            except requests.exceptions.RequestException as e:
                messages.error(request, f'Erro de conexão ao atualizar: {e}')
    
    else:
        # GET: Preencher o formulário com dados existentes
        initial_data = {
            'titulo': projeto_data.get('titulo'),
            'proposito': projeto_data.get('proposito'),
            'status': projeto_data.get('status'),
            'campus': projeto_data.get('campus'), # NOVO
            # 'habilidades_requeridas': ...
        }
        form = ProjectCreationForm(initial=initial_data)

    context = {
        'form': form,
        'editing': True, # Flag para mudar o título no template
        'projeto_id': projeto_id,
        'projeto_data': projeto_data, # Passa dados originais para o template (se necessário)
    }
    return render(request, 'habilidades/criar_projeto.html', context)

def perfil_usuario_view(request: HttpRequest, usuario_id):
    """
    Busca os detalhes do usuário na API e lista seus projetos criados.
    """
    usuario = None
    projetos_criados = []

    # 1. Buscar Detalhes do Usuário (GET /usuarios/{user_id})
    user_endpoint = f"{API_BASE_URL}/usuarios/{usuario_id}"
    
    # 2. Buscar Projetos Criados pelo Usuário (GET /projetos/usuario/{user_id})
    projects_endpoint = f"{API_BASE_URL}/projetos/usuario/{usuario_id}"

    try:
        # Requisita os dados do Usuário
        user_response = requests.get(user_endpoint, timeout=10)
        if user_response.status_code == 200:
            usuario = user_response.json()
        
        # Requisita os projetos criados
        projects_response = requests.get(projects_endpoint, timeout=10)
        if projects_response.status_code == 200:
            projetos_criados = projects_response.json()

        elif user_response.status_code == 404:
            messages.error(request, f"Usuário ID {usuario_id} não encontrado na API.")
            
    except requests.exceptions.ConnectionError:
        messages.error(request, 'Não foi possível conectar ao Backend (Docker).')
    except Exception as e:
        messages.error(request, f'Ocorreu um erro: {e}')
        
    
    # Se o usuário não foi encontrado, evite erros de template
    if not usuario:
        return render(request, 'habilidades/perfil_usuario.html', {'messages': messages})


    context = {
        'usuario': usuario,
        'projetos_criados': projetos_criados,
        # Você pode adicionar aqui uma flag 'is_current_user' se desejar
    }
    return render(request, 'habilidades/perfil_usuario.html', context)
    
def lista_projetos_view(request: HttpRequest):
    """
    Lista todos os projetos disponíveis na API. 
    Acessível por qualquer usuário, logado ou não.
    """
    # A ID do usuário é recuperada, mas é usada APENAS para lógica de template (ex: mostrar 'Ver Detalhes' ou 'Editar')
    # e NÃO para filtrar o resultado da API.
    user_id = request.session.get('user_id') 
    projetos = []
    
    endpoint = f"{API_BASE_URL}/projetos/"
    
    try:
        response = requests.get(endpoint, timeout=10)

        if response.status_code == 200:
            projetos = response.json()
        elif response.status_code == 404:
            # Não encontrou projetos
            messages.info(request, "Nenhum projeto foi encontrado.")
        else:
            messages.error(request, f"Erro ao buscar projetos: Status {response.status_code}. Detalhe: {response.text}")

    except requests.exceptions.ConnectionError:
        messages.error(request, 'Não foi possível conectar ao Backend (Docker). Verifique se o serviço está ativo.')
    except Exception as e:
        messages.error(request, f'Ocorreu um erro inesperado: {e}')
        
    context = {
        'projetos': projetos,
        'user_id': user_id,
    }
    
    return render(request, 'habilidades/lista_projetos.html', context)


def detalhes_projeto_view(request: HttpRequest, projeto_id):
    """
    Busca os detalhes de um projeto, seu owner e seus colaboradores na API (com GET /colaboradores).
    Inclui checagem robusta de tipo para participação.
    """
    user_id = request.session.get('user_id')
    # GARANTINDO QUE user_id É UM INTEIRO (se existir) para comparação com o JSON
    if user_id is not None:
        try:
            user_id = int(user_id)
        except ValueError:
            user_id = None
    
    projeto = None
    owner = None
    colaboradores = []
    usuario_e_colaborador = False
    
    try:
        # 1. Busca detalhes do Projeto (usando a listagem como workaround)
        listagem_endpoint = f"{API_BASE_URL}/projetos/"
        listagem_response = requests.get(listagem_endpoint, timeout=10)
        
        if listagem_response.status_code == 200:
            projetos_lista = listagem_response.json()
            for p in projetos_lista:
                if p.get('id') == projeto_id:
                    projeto = p
                    break
            
            if projeto:
                # 2. Busca detalhes do Owner
                owner_id = projeto.get('owner_id')
                if owner_id:
                    owner_endpoint = f"{API_BASE_URL}/usuarios/{owner_id}"
                    owner_response = requests.get(owner_endpoint, timeout=10)
                    if owner_response.status_code == 200:
                        owner = owner_response.json()
                
                # 3. BUSCA DE COLABORADORES (ENDPOINT CORRETO)
                colaboradores_endpoint = f"{API_BASE_URL}/projetos/{projeto_id}/colaboradores"
                colaboradores_response = requests.get(colaboradores_endpoint, timeout=10)
                
                if colaboradores_response.status_code == 200:
                    colaboradores = colaboradores_response.json()
                    
                    # CHECAGEM ROBUSTA DE PARTICIPAÇÃO
                    if user_id is not None:
                        for colaborador in colaboradores:
                            colaborador_id = colaborador.get('id')
                            
                            if colaborador_id == user_id: 
                                usuario_e_colaborador = True
                                break
                
                # 4. VERIFICAÇÃO SE O OWNER É O USUÁRIO LOGADO
                is_owner = owner_id == user_id if user_id is not None and owner_id is not None else False
                
            else:
                messages.error(request, f"Projeto ID {projeto_id} não encontrado na lista retornada pela API.")

        else:
            messages.error(request, f"Erro ao carregar lista de projetos (Status {listagem_response.status_code}).")

    except requests.exceptions.ConnectionError:
        messages.error(request, 'Não foi possível conectar ao Backend (Docker) para buscar o projeto.')
    except Exception as e:
        messages.error(request, f'Ocorreu um erro inesperado: {e}')
        
   
    # Define o estado final para o template
    participa_do_projeto = usuario_e_colaborador or is_owner
        
    context = {
        'projeto': projeto,
        'owner': owner,
        'colaboradores': colaboradores,
        'usuario_e_colaborador': usuario_e_colaborador, 
        'is_owner': is_owner,
        'projeto_id': projeto_id,
        'participa_do_projeto': participa_do_projeto,
        'feedbacks': [{'autor': 'Ricardo', 'texto': 'Iniciativa fantástica!'}],
    }
    
    return render(request, 'habilidades/detalhes_projeto.html', context)

def participar_projeto_view(request: HttpRequest, projeto_id):
    user_id = request.session.get('user_id')
    
    if not user_id:
        messages.error(request, 'Você precisa estar logado para manifestar interesse.')
        return redirect('habilidades:login')
        
    if request.method == 'POST':
        acao = request.POST.get('acao', 'participar') 
        
        headers = {'Content-Type': 'application/json'}
        # Converte user_id para int, garantindo que o payload e a URL estejam corretos
        user_id_int = int(user_id) 
        
        try:
            if acao == 'participar':
                # --- LÓGICA DE ENTRADA (POST) ---
                endpoint = f"{API_BASE_URL}/projetos/{projeto_id}/colaborar"
                payload = {"user_id": user_id_int, "mensagem": "Solicitação de participação."}

                response = requests.post(endpoint, json=payload, headers=headers, timeout=10)
                
                if response.status_code == 200 or response.status_code == 201:
                    messages.success(request, 'Sua participação foi registrada com sucesso no projeto!')
                elif response.status_code == 409:
                    messages.warning(request, 'Você já está cadastrado como colaborador neste projeto.')
                else:
                    messages.error(request, f'Falha ao registrar interesse: Status {response.status_code}. Detalhe: {response.text}')
            
            elif acao == 'sair':
                # --- LÓGICA DE SAÍDA (DELETE) ---
                endpoint = f"{API_BASE_URL}/projetos/{projeto_id}/colaborar/{user_id_int}"
                
                # REQUISIÇÃO DELETE REAL PARA REMOVER O ESTADO DO MOCK NO BACKEND
                response = requests.delete(endpoint, headers=headers, timeout=10)

                if response.status_code == 200:
                    messages.success(request, 'Você saiu do projeto com sucesso! A colaboração foi removida.')
                elif response.status_code == 404:
                    messages.warning(request, 'Não foi possível encontrar sua colaboração para remover.')
                else:
                    messages.error(request, f'Falha ao sair do projeto: Status {response.status_code}. Detalhe: {response.text}')
            
        except Exception as e:
            messages.error(request, f'Ocorreu um erro: {e}')
            
    return redirect(reverse('habilidades:detalhes_projeto', kwargs={'projeto_id': projeto_id}))

def busca_habilidade_view(request: HttpRequest):
    """
    Processa a busca de usuários e projetos na API com base em termos e filtros (campus).
    """
    termo_busca = request.GET.get('termo', '')
    campus_filtro = request.GET.getlist('campus') # Usamos getlist pois pode haver múltiplos checkboxes

    resultados_usuarios = []
    resultados_projetos = []
    
    # 1. Montagem do Endpoint de Busca (Assumindo que a rota GET /api/v1/ é a rota de busca)
    # ATENÇÃO: Se esta URL não funcionar, ela precisa ser ajustada para a rota real de busca na API.
    endpoint_busca = f"{API_BASE_URL}/" 
    
    params = {}
    if termo_busca:
        params['termo'] = termo_busca
    if campus_filtro:
        # A API pode esperar uma lista ou uma string separada por vírgula. Vamos enviar como lista (múltiplos 'campus=X')
        params['campus'] = campus_filtro 
    
    try:
        # Requisita a API de Busca (esperamos usuários e projetos)
        if termo_busca or campus_filtro:
            response = requests.get(endpoint_busca, params=params, timeout=10)
            
            if response.status_code == 200:
                # Vamos assumir que a API de busca retorna um JSON que contém duas listas: users e projects.
                # Se a API retornar apenas uma lista combinada, o parsing precisará de ajuste.
                dados = response.json()
                
                # Supondo que a API retorna dados_combinados. Vamos simular a separação:
                # (AJUSTE NECESSÁRIO: Substitua esta simulação pelo parsing real da sua API)
                if isinstance(dados, list):
                    # Se a API retornar uma lista simples, assumimos que são usuários (ou projetos)
                    resultados_usuarios = [item for item in dados if 'email' in item] # Heurística simples
                    resultados_projetos = [item for item in dados if 'proposito' in item] # Heurística simples
                
                # Caso a API retorne um dicionário com chaves específicas:
                elif isinstance(dados, dict):
                    resultados_usuarios = dados.get('usuarios', [])
                    resultados_projetos = dados.get('projetos', [])
            
            elif response.status_code == 404:
                 messages.info(request, "Nenhum resultado de busca encontrado.")
            else:
                messages.error(request, f"Erro na busca da API: Status {response.status_code}. Detalhe: {response.text}")
        
    except requests.exceptions.ConnectionError:
        messages.error(request, 'Não foi possível conectar ao Backend para realizar a busca.')
    except Exception as e:
        messages.error(request, f'Ocorreu um erro inesperado durante a busca: {e}')


    context = {
        'termo_busca': termo_busca,
        'campus_filtro': campus_filtro,
        'usuarios': resultados_usuarios,
        'projetos': resultados_projetos, # NOVO: Passando projetos para o template
        'total_resultados': len(resultados_usuarios) + len(resultados_projetos),
        'total_usuarios': len(resultados_usuarios),
        'total_projetos': len(resultados_projetos),
    }
    
    return render(request, 'habilidades/busca_habilidade.html', context)

class ProjectCreationForm(forms.Form):
    titulo = forms.CharField(max_length=100, label="Título do Projeto")
    proposito = forms.CharField(widget=forms.Textarea, label="Descrição Completa")
    habilidades_requeridas = forms.CharField(max_length=255, label="Habilidades Requeridas", required=False)
    status = forms.ChoiceField(choices=[('AB', 'Aberto'), ('PR', 'Em Progresso')], label="Status Inicial")
    # NOVO CAMPO: Campus (Geolocalização)
    campus = forms.ChoiceField(
        choices=[
            ('DIA', 'Diamantina'), 
            ('JAN', 'Janaúba'), 
            ('UNA', 'Unaí'), 
            ('MUC', 'Mucuri')
        ],
        label="Campus (Localização)"
    )

def gerenciar_projeto_view(request: HttpRequest, projeto_id):
    """
    Trata as ações de gerenciamento do owner (como DELETAR) usando PATCH (Soft Delete).
    """
    user_id = request.session.get('user_id')
    acao_gerenciamento = request.POST.get('acao_gerenciamento')
    
    if not user_id:
        messages.error(request, 'Você precisa estar logado para gerenciar projetos.')
        return redirect('habilidades:login')

    # Ação de DELETAR (usando PATCH para exclusão lógica)
    if request.method == 'POST' and acao_gerenciamento == 'deletar':
        
        patch_endpoint = f"{API_BASE_URL}/projetos/{projeto_id}"
        headers = {'Content-Type': 'application/json'}
        
        # Payload para exclusão lógica (Altera o status do projeto)
        payload = {"status": "DELETADO"}

        try:
            # Envia a requisição PATCH para o Backend (rota funcional)
            response = requests.patch(patch_endpoint, json=payload, headers=headers, timeout=10)
            
            if response.status_code == 200:
                messages.success(request, f"Projeto ID {projeto_id} marcado como DELETADO.")
                # Redireciona para a listagem principal
                return redirect('habilidades:lista_projetos')
            
            elif response.status_code == 404:
                messages.warning(request, "O projeto não foi encontrado para exclusão.")
            
            else:
                messages.error(request, f"Falha na exclusão lógica. Status: {response.status_code}. Detalhe: {response.text}")
                
        except requests.exceptions.RequestException as e:
            messages.error(request, f"Erro de conexão ao tentar deletar o projeto: {e}")
            
    # Se a ação falhou ou não foi reconhecida, retorna para a página de detalhes
    return redirect('habilidades:detalhes_projeto', projeto_id=projeto_id)

def perfil_usuario_view(request: HttpRequest, usuario_id):
    """
    Busca os detalhes do usuário na API e lista seus projetos criados.
    """
    user_id_logado = request.session.get('user_id')
    
    # 1. Checagem para saber se o perfil visualizado é o do usuário logado
    is_current_user = False
    if user_id_logado is not None:
        try:
            # Garante que ambos são inteiros para comparação
            is_current_user = int(user_id_logado) == usuario_id
        except ValueError:
            pass
            
    usuario = None
    projetos_criados = []

    # 2. Buscar Detalhes do Usuário (GET /usuarios/{user_id})
    user_endpoint = f"{API_BASE_URL}/usuarios/{usuario_id}"
    projects_endpoint = f"{API_BASE_URL}/projetos/usuario/{usuario_id}"

    try:
        user_response = requests.get(user_endpoint, timeout=10)
        if user_response.status_code == 200:
            usuario = user_response.json()
        
        projects_response = requests.get(projects_endpoint, timeout=10)
        if projects_response.status_code == 200:
            projetos_criados = projects_response.json()

        elif user_response.status_code == 404:
            messages.error(request, f"Usuário ID {usuario_id} não encontrado na API.")
            
    except requests.exceptions.ConnectionError:
        messages.error(request, 'Não foi possível conectar ao Backend (Docker).')
    except Exception as e:
        messages.error(request, f'Ocorreu um erro: {e}')
        
    
    if not usuario:
        return render(request, 'habilidades/perfil_usuario.html', {'messages': messages})


    context = {
        'usuario': usuario,
        'projetos_criados': projetos_criados,
        'is_current_user': is_current_user, # NOVO: Flag para o botão de edição
    }
    return render(request, 'habilidades/perfil_usuario.html', context)