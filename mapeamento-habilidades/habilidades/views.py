# Arquivo: /mapeamento-habilidades/habilidades/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout as auth_logout
from django import forms
from django.urls import reverse
from django.contrib import messages
from django.http import HttpRequest
import requests
import json 

# Variável de configuração da API (URL Base)
API_BASE_URL = "http://localhost:8001/api/v1"

# =========================================================================
# === 1. DEFINIÇÕES DE FORMULÁRIO (Métricas de Avaliação) ===
# =========================================================================

# NOVO: Definição das opções de resposta (Escala de 1 a 3 para as Métricas)
RESPOSTA_CHOICES_METRICAS = [
    (3, 'Máximo (3)'),
    (2, 'Médio (2)'),
    (1, 'Mínimo (1)'),
    (0, 'Não se Aplica (0)'), # Mantido como fallback se a pergunta não for relevante
]

# Definição das opções de Métrica Textual (Mantida)
METRICA_TEXTUAL_CHOICES = [
    ('excelente', 'Excelente (5)'),
    ('razoavel', 'Razoável (3)'),
    ('nao cumpre', 'Não cumpre com o que foi proposto (0)'),
]

# Definição dos Widgets (Mantidos)
TEXTAREA_WIDGET_AVALIACAO = forms.Textarea(attrs={'class': 'form-input flex w-full min-w-0 flex-1 resize-y overflow-hidden rounded-lg focus:outline-0 focus:ring-2 focus:ring-primary/50 border border-border-light dark:border-border-dark bg-background-light dark:bg-background-dark focus:border-primary p-[15px] text-base font-normal leading-normal min-h-[100px]', 'rows': 4})
RADIO_WIDGET = forms.RadioSelect() 

class AvaliacaoProjetoForm(forms.Form):
    """Formulário de avaliação detalhada com as 7 métricas + nota final."""
    
    # --- Métrica 1: Clareza e Entendimento (3 perguntas) ---
    clareza_objetivo = forms.ChoiceField(choices=RESPOSTA_CHOICES_METRICAS, widget=RADIO_WIDGET, label="O objetivo do projeto está claramente apresentado.")
    clareza_informacao = forms.ChoiceField(choices=RESPOSTA_CHOICES_METRICAS, widget=RADIO_WIDGET, label="As informações disponibilizadas são suficientes para entender a proposta.")
    clareza_beneficiarios = forms.ChoiceField(choices=RESPOSTA_CHOICES_METRICAS, widget=RADIO_WIDGET, label="O projeto explica de forma clara quem será beneficiado.")
    
    # --- Métrica 2: Relevância Social (3 perguntas) ---
    relevancia_problema = forms.ChoiceField(choices=RESPOSTA_CHOICES_METRICAS, widget=RADIO_WIDGET, label="O projeto aborda um problema real ou necessidade da comunidade.")
    relevancia_impacto = forms.ChoiceField(choices=RESPOSTA_CHOICES_METRICAS, widget=RADIO_WIDGET, label="O impacto esperado é relevante para a comunidade.")
    relevancia_beneficios = forms.ChoiceField(choices=RESPOSTA_CHOICES_METRICAS, widget=RADIO_WIDGET, label="O projeto gera benefícios sociais claros ou potenciais.")
    
    # --- Métrica 3: Viabilidade (3 perguntas) ---
    viabilidade_implementacao = forms.ChoiceField(choices=RESPOSTA_CHOICES_METRICAS, widget=RADIO_WIDGET, label="O projeto parece possível de ser implementado com os recursos informados.")
    viabilidade_cronograma = forms.ChoiceField(choices=RESPOSTA_CHOICES_METRICAS, widget=RADIO_WIDGET, label="O cronograma proposto é realista.")
    viabilidade_capacidade = forms.ChoiceField(choices=RESPOSTA_CHOICES_METRICAS, widget=RADIO_WIDGET, label="Os responsáveis parecem ter capacidade técnica para executar o projeto.")
    
    # --- Métrica 4: Transparência (3 perguntas) ---
    transparencia_verificavel = forms.ChoiceField(choices=RESPOSTA_CHOICES_METRICAS, widget=RADIO_WIDGET, label="O projeto apresenta informações transparentes e verificáveis.")
    transparencia_custos = forms.ChoiceField(choices=RESPOSTA_CHOICES_METRICAS, widget=RADIO_WIDGET, label="Os custos e recursos do projeto são mostrados de forma clara.")
    transparencia_prestacao = forms.ChoiceField(choices=RESPOSTA_CHOICES_METRICAS, widget=RADIO_WIDGET, label="O projeto demonstra intenção de prestação de contas.")
    
    # --- Métrica 5: Inovação (2 perguntas) ---
    inovacao_ideias = forms.ChoiceField(choices=RESPOSTA_CHOICES_METRICAS, widget=RADIO_WIDGET, label="O projeto apresenta ideias novas ou soluções criativas.")
    inovacao_melhorias = forms.ChoiceField(choices=RESPOSTA_CHOICES_METRICAS, widget=RADIO_WIDGET, label="A proposta traz melhorias significativas em relação ao que já existe.")
    
    # --- Métrica 6: Participação e Inclusão (3 perguntas) ---
    participacao_grupos = forms.ChoiceField(choices=RESPOSTA_CHOICES_METRICAS, widget=RADIO_WIDGET, label="O projeto favorece diferentes grupos da comunidade.")
    participacao_social = forms.ChoiceField(choices=RESPOSTA_CHOICES_METRICAS, widget=RADIO_WIDGET, label="A proposta foi construída considerando participação social.")
    participacao_colaboracao = forms.ChoiceField(choices=RESPOSTA_CHOICES_METRICAS, widget=RADIO_WIDGET, label="O projeto incentiva a colaboração entre membros.")
    
    # --- Métrica 7: Sustentabilidade (2 perguntas) ---
    sustentabilidade_duradouro = forms.ChoiceField(choices=RESPOSTA_CHOICES_METRICAS, widget=RADIO_WIDGET, label="O projeto tem potencial para gerar resultados duradouros.")
    sustentabilidade_recursos = forms.ChoiceField(choices=RESPOSTA_CHOICES_METRICAS, widget=RADIO_WIDGET, label="Os recursos necessários podem ser mantidos ao longo do tempo.")

    # --- Métrica 8: Avaliação Final e Feedback (Geral) ---
    # Nota Geral Mantida de 0 a 5
    nota_geral = forms.ChoiceField(
        choices=[(i, str(i)) for i in range(6)], 
        widget=RADIO_WIDGET,
        label="Sua nota geral para o projeto (0 a 5)"
    )
    metrica_textual = forms.ChoiceField(
        choices=METRICA_TEXTUAL_CHOICES,
        widget=RADIO_WIDGET,
        label="Métrica de Cumprimento da Proposta"
    )
    comentario = forms.CharField(
        widget=TEXTAREA_WIDGET_AVALIACAO,
        required=False,
        label="Comentários Adicionais (Feedback opcional)"
    )

class ProjectCreationForm(forms.Form):
    """
    Formulário para criação e edição de projetos. 
    Contém todos os campos necessários para a API de Projetos (CRUD).
    """
    titulo = forms.CharField(max_length=100, label="Título do Projeto")
    proposito = forms.CharField(widget=forms.Textarea, label="Descrição Completa")
    habilidades_requeridas = forms.CharField(max_length=255, label="Habilidades Requeridas", required=False)
    status = forms.ChoiceField(choices=[('AB', 'Aberto'), ('PR', 'Em Progresso')], label="Status Inicial")
    campus = forms.ChoiceField(
        choices=[
            ('DIA', 'Diamantina'), 
            ('JAN', 'Janaúba'), 
            ('UNA', 'Unaí'), 
            ('MUC', 'Mucuri')
        ],
        label="Campus (Localização)"
    )

# # # A classe UserProfileForm fake e FakeUserProfile foram removidas. # # #
# # # A classe FeedbackForm e a view submit_feedback_view foram removidas. # # #

# =========================================================================
# === 2. FUNÇÕES AUXILIARES ===
# =========================================================================

def get_user_id_and_token(request):
    """
    Função auxiliar para obter o ID e (opcionalmente) o token do usuário logado na API.
    """
    user_id = request.session.get('user_id')
    user_token = request.session.get('api_token', None) 
    return user_id, user_token

# =========================================================================
# === 3. VIEWS PRINCIPAIS (Cleaned) ===
# =========================================================================

def index(request):
    """Página Inicial do SkillMap."""
    return render(request, 'habilidades/index.html') 

def busca_habilidade_view(request: HttpRequest):
    """Processa a busca de usuários e projetos na API."""
    termo_busca = request.GET.get('termo', '')
    campus_filtro = request.GET.getlist('campus') 
    resultados_usuarios = []
    resultados_projetos = []
    
    endpoint_busca = f"{API_BASE_URL}/" 
    params = {}
    if termo_busca:
        params['termo'] = termo_busca
    if campus_filtro:
        params['campus'] = campus_filtro 
    
    try:
        if termo_busca or campus_filtro:
            response = requests.get(endpoint_busca, params=params, timeout=10)
            if response.status_code == 200:
                dados = response.json()
                if isinstance(dados, dict):
                    resultados_usuarios = dados.get('usuarios', [])
                    resultados_projetos = dados.get('projetos', [])
            elif response.status_code == 404:
                 messages.info(request, "Nenhum resultado de busca encontrado.")
            else:
                messages.error(request, f"Erro na busca da API: Status {response.status_code}. Detalhe: {response.text}")
        
    except requests.exceptions.RequestException as e:
        messages.error(request, f'Não foi possível conectar ao Backend para realizar a busca: {e}')

    context = {
        'termo_busca': termo_busca,
        'campus_filtro': campus_filtro,
        'usuarios': resultados_usuarios,
        'projetos': resultados_projetos,
        'total_resultados': len(resultados_usuarios) + len(resultados_projetos),
        'total_usuarios': len(resultados_usuarios),
        'total_projetos': len(resultados_projetos),
    }
    return render(request, 'habilidades/busca_habilidade.html', context)

def lista_projetos_view(request: HttpRequest):
    """Lista todos os projetos disponíveis na API."""
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
    except requests.exceptions.RequestException as e:
        messages.error(request, f'Não foi possível conectar ao Backend: {e}')
    context = {
        'projetos': projetos,
        'user_id': user_id,
    }
    return render(request, 'habilidades/lista_projetos.html', context)

def comunidade_view(request):
    """View para a página de FÓRUM/Voz da Comunidade."""
    return render(request, 'habilidades/comunidade.html') 

def cadastro_perfil_view(request: HttpRequest):
    """View para REGISTRO de usuário (Chama a API /auth/register)."""
    # Lógica mantida: Sem mocks e funcionando com API
    context = {}
    if request.method == 'POST':
        # ... (lógica de obtenção de dados e chamada à API) ...
        username = request.POST.get('username', '')
        email = request.POST.get('email', '')
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')
        campus = request.POST.get('campus', '')
        curso = request.POST.get('curso', '')
        context['form_data'] = request.POST 
        if password != password2:
            messages.error(request, "As senhas não coincidem.")
            return render(request, 'habilidades/cadastrar_perfil.html', context)
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
            except requests.exceptions.JSONDecodeError:
                pass 
            if response.status_code == 201: 
                messages.success(request, "Usuário registrado com sucesso! Faça login para continuar.")
                return redirect(reverse('habilidades:login'))
            elif response.status_code == 422:
                messages.error(request, f"Erro de validação da API (422): Verifique se preencheu todos os campos. Detalhe: {error_detail}")
            elif response.status_code != 200:
                messages.error(request, f'Falha no registro: Status {response.status_code}. Detalhe: {error_detail}')
        except requests.exceptions.RequestException as e:
            messages.error(request, f'Erro de conexão ao Backend: {e}')
    return render(request, 'habilidades/cadastrar_perfil.html', context)


def login_view(request: HttpRequest):
    """View que se conecta à API para checar a existência do usuário e salvar o ID na sessão."""
    # Lógica mantida: Sem mocks e funcionando com API
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
        except requests.exceptions.RequestException as e:
            messages.error(request, f'Não foi possível conectar ao Backend: {e}')
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

# # # O UserProfileForm foi removido, então vamos simplificar o acesso ao perfil. # # #
class UserEditForm(forms.Form):
    """Formulário temporário para edição de perfil (usado na view editar_perfil_view)."""
    # Apenas para simplificar a remoção do UserProfileForm
    nome = forms.CharField(max_length=150)
    curso = forms.CharField(max_length=100, required=False)
    campus = forms.CharField(max_length=10)
    biografia = forms.CharField(max_length=300, widget=forms.Textarea, required=False)
    lattes_url = forms.URLField(required=False)
    linkedin_url = forms.URLField(required=False)
    email = forms.EmailField(required=False)


def editar_perfil_view(request: HttpRequest):
    """Carrega formulário de edição e envia alterações via PATCH para a API."""
    user_id = request.session.get('user_id')
    
    if not user_id:
        messages.warning(request, 'Você precisa estar logado para editar seu perfil.')
        return redirect('habilidades:login')

    user_endpoint = f"{API_BASE_URL}/usuarios/{user_id}"
    
    try:
        user_response = requests.get(user_endpoint, timeout=10)
        
        if user_response.status_code != 200:
            messages.error(request, 'Erro ao carregar dados do perfil.')
            return redirect('habilidades:perfil_usuario', usuario_id=user_id)
            
        user_data = user_response.json()

        if request.method == 'POST':
            form = UserEditForm(request.POST) 
            if form.is_valid():
                
                payload = {
                    "username": form.cleaned_data.get('nome'), 
                    "email": form.cleaned_data.get('email', user_data.get('email')),
                    "curso": form.cleaned_data.get('curso'),
                    "campus": form.cleaned_data.get('campus'),
                    # ... (outros campos devem ser adicionados ao UserEditForm se necessários)
                    "biografia": form.cleaned_data.get('biografia'),
                    "lattes_url": form.cleaned_data.get('lattes_url'),
                    "linkedin_url": form.cleaned_data.get('linkedin_url'),
                }
                
                # Remove campos None/vazios para um PATCH mais limpo (se necessário)
                payload = {k: v for k, v in payload.items() if v is not None and v != ''}

                patch_response = requests.patch(user_endpoint, json=payload, timeout=10)
                
                if patch_response.status_code == 200:
                    messages.success(request, 'Perfil atualizado com sucesso!')
                    return redirect('habilidades:perfil_usuario', usuario_id=user_id)
                else:
                    messages.error(request, f"Falha ao atualizar perfil: Status {patch_response.status_code}. Detalhe: {patch_response.text}")
        
        else:
            initial_data = {
                'nome': user_data.get('username'), 
                'curso': user_data.get('curso'),
                'campus': user_data.get('campus'),
                'email': user_data.get('email'),
                'biografia': user_data.get('biografia'),
                'lattes_url': user_data.get('lattes_url', ''),
                'linkedin_url': user_data.get('linkedin_url', ''),
            }
            form = UserEditForm(initial=initial_data)

    except requests.exceptions.RequestException as e:
        messages.error(request, f'Erro de conexão: {e}')
        form = UserEditForm()
    
    context = {'form': form}
    return render(request, 'habilidades/editar_perfil.html', context)


def criar_projeto_view(request: HttpRequest):
    """View para criação de um novo projeto, utilizando o user_id da sessão."""
    user_id = request.session.get('user_id')
    
    if not user_id:
        messages.warning(request, 'Você precisa estar logado (via API) para criar um projeto.')
        return redirect('habilidades:login')
        
    if request.method == 'POST':
        form = ProjectCreationForm(request.POST)
        if form.is_valid():
            titulo = form.cleaned_data['titulo']
            proposito = form.cleaned_data['proposito'] 
            campus = form.cleaned_data['campus'] 
            habilidades_requeridas = form.cleaned_data['habilidades_requeridas'] 

            endpoint = f"{API_BASE_URL}/projetos/"
            payload = {"titulo": titulo, "proposito": proposito, "owner_id": user_id, "campus": campus, "habilidades_requeridas": habilidades_requeridas}
            
            try:
                response = requests.post(endpoint, json=payload, timeout=10)

                if response.status_code == 201 or response.status_code == 200: 
                    messages.success(request, "Projeto criado com sucesso na API!")
                    return redirect(reverse('habilidades:lista_projetos'))
                
                else:
                    messages.error(request, f'Falha ao criar projeto na API: Status {response.status_code}. Detalhe: {response.text}')

            except requests.exceptions.RequestException as e:
                messages.error(request, f'Erro de conexão: {e}')
            
    else:
        form = ProjectCreationForm()

    context = {
        'form': form
    }
    return render(request, 'habilidades/criar_projeto.html', context)


def editar_projeto_view(request: HttpRequest, projeto_id):
    """Carrega o formulário de edição com dados existentes e trata o envio (PATCH)."""
    # Lógica mantida: Sem mocks e funcionando com API
    user_id = request.session.get('user_id')
    
    if not user_id:
        messages.warning(request, 'Você precisa estar logado para editar projetos.')
        return redirect('habilidades:login')

    project_endpoint = f"{API_BASE_URL}/projetos/{projeto_id}"
    
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

    if projeto_data.get('owner_id') != int(user_id):
        messages.error(request, 'Você não tem permissão para editar este projeto.')
        return redirect('habilidades:detalhes_projeto', projeto_id=projeto_id)

    if request.method == 'POST':
        form = ProjectCreationForm(request.POST)
        if form.is_valid():
            endpoint_patch = f"{API_BASE_URL}/projetos/{projeto_id}"
            
            payload = {
                "titulo": form.cleaned_data['titulo'],
                "proposito": form.cleaned_data['proposito'],
                "status": form.cleaned_data['status'],
                "campus": form.cleaned_data['campus'],
                "habilidades_requeridas": form.cleaned_data['habilidades_requeridas'],
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
        initial_data = {
            'titulo': projeto_data.get('titulo'),
            'proposito': projeto_data.get('proposito'),
            'status': projeto_data.get('status'),
            'campus': projeto_data.get('campus'),
            'habilidades_requeridas': projeto_data.get('habilidades_requeridas'),
        }
        form = ProjectCreationForm(initial=initial_data)

    context = {
        'form': form,
        'editing': True,
        'projeto_id': projeto_id,
        'projeto_data': projeto_data,
    }
    return render(request, 'habilidades/criar_projeto.html', context)


def perfil_usuario_view(request: HttpRequest, usuario_id):
    """Busca os detalhes do usuário na API e lista seus projetos criados."""
    # Lógica mantida: Sem mocks e funcionando com API
    user_id_logado = request.session.get('user_id')
    is_current_user = False
    if user_id_logado is not None:
        try:
            is_current_user = int(user_id_logado) == usuario_id
        except ValueError:
            pass
    usuario = None
    projetos_criados = []

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
            
    except requests.exceptions.RequestException as e:
        messages.error(request, f'Erro de conexão: {e}')
    
    if not usuario:
        return render(request, 'habilidades/perfil_usuario.html', {})

    context = {
        'usuario': usuario,
        'projetos_criados': projetos_criados,
        'is_current_user': is_current_user,
    }
    return render(request, 'habilidades/perfil_usuario.html', context)

def detalhes_projeto_view(request: HttpRequest, projeto_id):
    """
    Busca os detalhes de um projeto, seu owner, colaboradores E as estatísticas de avaliação.
    **100% de dependência da API.**
    """
    user_id = request.session.get('user_id')
    if user_id is not None:
        try:
            user_id = int(user_id)
        except ValueError:
            user_id = None
    
    projeto = None
    owner = None 
    colaboradores = []
    avaliacoes_stats = None
    usuario_e_colaborador = False
    is_owner = False
    
    try:
        # ENDPOINTS
        project_endpoint = f"{API_BASE_URL}/projetos/{projeto_id}"
        colaboradores_endpoint = f"{API_BASE_URL}/projetos/{projeto_id}/colaboradores"
        avaliacoes_endpoint = f"{API_BASE_URL}/projetos/{projeto_id}/avaliacoes"
        feedbacks_endpoint = f"{API_BASE_URL}/projetos/{projeto_id}/feedbacks" # Assumindo um endpoint para comentários/feedbacks

        # 1. Busca detalhes do Projeto
        projeto_response = requests.get(project_endpoint, timeout=10)
        if projeto_response.status_code == 200:
            projeto = projeto_response.json()
        elif projeto_response.status_code == 404:
            messages.error(request, f"Projeto ID {projeto_id} não encontrado na API.")
            return redirect('habilidades:lista_projetos')
        else:
            messages.error(request, f"Erro ao carregar projeto: Status {projeto_response.status_code}.")
            return redirect('habilidades:lista_projetos')

        # 2. Busca detalhes do Owner
        owner_id = projeto.get('owner_id')
        if owner_id:
            owner_endpoint = f"{API_BASE_URL}/usuarios/{owner_id}"
            try:
                owner_response = requests.get(owner_endpoint, timeout=10)
                if owner_response.status_code == 200:
                    owner = owner_response.json()
            except requests.exceptions.RequestException:
                pass # Ignora erro de owner se o projeto foi encontrado

        # 3. Busca de Colaboradores
        colaboradores_response = requests.get(colaboradores_endpoint, timeout=10)
        if colaboradores_response.status_code == 200:
            colaboradores = colaboradores_response.json()
            if user_id is not None:
                for colaborador in colaboradores:
                    if colaborador.get('id') == user_id: 
                        usuario_e_colaborador = True
                        break
        
        # 4. Busca de Estatísticas de Avaliação
        avaliacoes_response = requests.get(avaliacoes_endpoint, timeout=10)
        if avaliacoes_response.status_code == 200:
            avaliacoes_stats = avaliacoes_response.json()
            
        # 5. Busca de Feedbacks/Comentários
        feedbacks = []
        try:
            feedbacks_response = requests.get(feedbacks_endpoint, timeout=10)
            if feedbacks_response.status_code == 200:
                feedbacks = feedbacks_response.json()
        except requests.exceptions.RequestException:
            pass # Ignora se o endpoint de feedbacks não existir ou falhar

        # 6. Verificação de Permissão
        is_owner = owner_id == user_id if user_id is not None and owner_id is not None else False
        participa_do_projeto = usuario_e_colaborador or is_owner

    except requests.exceptions.RequestException as e:
        messages.error(request, f'Erro de conexão ao Backend para buscar o projeto: {e}')
        return redirect('habilidades:lista_projetos') 
        
    context = {
        'projeto': projeto,
        'owner': owner, 
        'colaboradores': colaboradores,
        'avaliacoes_stats': avaliacoes_stats,
        'feedbacks': feedbacks, # Novo campo para o template
        'usuario_e_colaborador': usuario_e_colaborador, 
        'is_owner': is_owner,
        'projeto_id': projeto_id,
        'participa_do_projeto': participa_do_projeto,
        # O link de avaliar usa a chave 'projeto_id' (que é o que está correto agora)
        'link_avaliar': reverse('habilidades:avaliar_projeto', kwargs={'projeto_id': projeto_id}) if participa_do_projeto else None,
    }
    
    return render(request, 'habilidades/detalhes_projeto.html', context)


def participar_projeto_view(request: HttpRequest, projeto_id):
    """Trata as ações de participar/sair de um projeto."""
    # Lógica mantida: Sem mocks e funcionando com API
    user_id = request.session.get('user_id')
    
    if not user_id:
        messages.error(request, 'Você precisa estar logado para manifestar interesse.')
        return redirect('habilidades:login')
        
    if request.method == 'POST':
        acao = request.POST.get('acao', 'participar') 
        headers = {'Content-Type': 'application/json'}
        user_id_int = int(user_id) 
        
        try:
            if acao == 'participar':
                endpoint = f"{API_BASE_URL}/projetos/{projeto_id}/colaborar"
                payload = {"user_id": user_id_int, "mensagem": "Solicitação de participação."}
                response = requests.post(endpoint, json=payload, headers=headers, timeout=10)
                
                if response.status_code in [200, 201]:
                    messages.success(request, 'Sua participação foi registrada com sucesso no projeto!')
                elif response.status_code == 409:
                    messages.warning(request, 'Você já está cadastrado como colaborador neste projeto.')
                else:
                    messages.error(request, f'Falha ao registrar interesse: Status {response.status_code}. Detalhe: {response.text}')
            
            elif acao == 'sair':
                endpoint = f"{API_BASE_URL}/projetos/{projeto_id}/colaborar/{user_id_int}"
                response = requests.delete(endpoint, headers=headers, timeout=10)

                if response.status_code == 200:
                    messages.success(request, 'Você saiu do projeto com sucesso! A colaboração foi removida.')
                elif response.status_code == 404:
                    messages.warning(request, 'Não foi possível encontrar sua colaboração para remover.')
                else:
                    messages.error(request, f'Falha ao sair do projeto: Status {response.status_code}. Detalhe: {response.text}')
            
        except requests.exceptions.RequestException as e:
            messages.error(request, f'Ocorreu um erro de conexão: {e}')
            
    return redirect(reverse('habilidades:detalhes_projeto', kwargs={'projeto_id': projeto_id}))


def gerenciar_projeto_view(request: HttpRequest, projeto_id):
    """Trata as ações de gerenciamento do owner (como DELETAR)."""
    # Lógica mantida: Sem mocks e funcionando com API
    user_id = request.session.get('user_id')
    acao_gerenciamento = request.POST.get('acao_gerenciamento')
    
    if not user_id:
        messages.error(request, 'Você precisa estar logado para gerenciar projetos.')
        return redirect('habilidades:login')

    if request.method == 'POST' and acao_gerenciamento == 'deletar':
        patch_endpoint = f"{API_BASE_URL}/projetos/{projeto_id}"
        headers = {'Content-Type': 'application/json'}
        payload = {"status": "DELETADO"}

        try:
            response = requests.patch(patch_endpoint, json=payload, headers=headers, timeout=10)
            
            if response.status_code == 200:
                messages.success(request, f"Projeto ID {projeto_id} marcado como DELETADO.")
                return redirect('habilidades:lista_projetos')
            
            elif response.status_code == 404:
                messages.warning(request, "O projeto não foi encontrado para exclusão.")
            
            else:
                messages.error(request, f"Falha na exclusão lógica. Status: {response.status_code}. Detalhe: {response.text}")
                
        except requests.exceptions.RequestException as e:
            messages.error(request, f"Erro de conexão ao tentar deletar o projeto: {e}")
            
    return redirect('habilidades:detalhes_projeto', projeto_id=projeto_id)

# =========================================================================
# === 4. VIEW DE AVALIAÇÃO (Corrigida e Implementada) ===
# =========================================================================

def avaliar_projeto_view(request: HttpRequest, projeto_id):
    """
    Carrega o formulário de avaliação, verifica a permissão e envia a avaliação para o endpoint RESTful.
    """
    user_id, user_token = get_user_id_and_token(request)
    
    if not user_id:
        messages.error(request, 'Você precisa estar logado para avaliar projetos.')
        return redirect('habilidades:login')

    headers = {'Content-Type': 'application/json'}

    # 1. Tentar obter detalhes do projeto (Para renderizar o título)
    project_endpoint = f"{API_BASE_URL}/projetos/{projeto_id}"
    project_title = 'Projeto Desconhecido'
    try:
        project_response = requests.get(project_endpoint, timeout=10)
        project_response.raise_for_status()
        project_data = project_response.json()
        project_title = project_data.get('titulo', project_title)
    except requests.exceptions.RequestException as e:
        messages.error(request, f"Erro ao carregar projeto ou conectar à API: {e}")
        return redirect('habilidades:lista_projetos') 

    # Variáveis de controle (simulação, a lógica real deve vir da API no futuro)
    context = {
        # *** CORRIGIDO: Usando 'projeto_id' para consistência (resolve o NoReverseMatch) ***
        'projeto_id': projeto_id,
        'project_title': project_title,
        'form': AvaliacaoProjetoForm(),
        'already_evaluated': False,
        'can_evaluate': True, 
    }

    if request.method == 'POST':
        form = AvaliacaoProjetoForm(request.POST)
        if form.is_valid():
            # 2. Construção do Payload com TODOS os 20+ campos
            payload = {
                "user_id": int(user_id), 
                "projeto_id": projeto_id,
                # Métrica 1
                "clareza_objetivo": int(form.cleaned_data['clareza_objetivo']),
                "clareza_informacao": int(form.cleaned_data['clareza_informacao']),
                "clareza_beneficiarios": int(form.cleaned_data['clareza_beneficiarios']),
                # Métrica 2
                "relevancia_problema": int(form.cleaned_data['relevancia_problema']),
                "relevancia_impacto": int(form.cleaned_data['relevancia_impacto']),
                "relevancia_beneficios": int(form.cleaned_data['relevancia_beneficios']),
                # Métrica 3
                "viabilidade_implementacao": int(form.cleaned_data['viabilidade_implementacao']),
                "viabilidade_cronograma": int(form.cleaned_data['viabilidade_cronograma']),
                "viabilidade_capacidade": int(form.cleaned_data['viabilidade_capacidade']),
                # Métrica 4
                "transparencia_verificavel": int(form.cleaned_data['transparencia_verificavel']),
                "transparencia_custos": int(form.cleaned_data['transparencia_custos']),
                "transparencia_prestacao": int(form.cleaned_data['transparencia_prestacao']),
                # Métrica 5
                "inovacao_ideias": int(form.cleaned_data['inovacao_ideias']),
                "inovacao_melhorias": int(form.cleaned_data['inovacao_melhorias']),
                # Métrica 6
                "participacao_grupos": int(form.cleaned_data['participacao_grupos']),
                "participacao_social": int(form.cleaned_data['participacao_social']),
                "participacao_colaboracao": int(form.cleaned_data['participacao_colaboracao']),
                # Métrica 7
                "sustentabilidade_duradouro": int(form.cleaned_data['sustentabilidade_duradouro']),
                "sustentabilidade_recursos": int(form.cleaned_data['sustentabilidade_recursos']),
                # Métrica 8 (Final)
                "nota_geral": int(form.cleaned_data['nota_geral']),
                "metrica_textual": form.cleaned_data['metrica_textual'].lower(),
                "comentario": form.cleaned_data.get('comentario')
            }

            # 3. Enviar a avaliação para o endpoint RESTful
            try:
                url_endpoint = f"{API_BASE_URL}/projetos/{projeto_id}/avaliar"
                response = requests.post(url_endpoint, headers=headers, json=payload, timeout=10)
                
                if response.status_code == 201:
                    messages.success(request, "Sua avaliação foi enviada com sucesso!")
                    return redirect('habilidades:detalhes_projeto', projeto_id=projeto_id)

                error_detail = response.json().get('detail', response.text)
                
                if response.status_code == 403: 
                    messages.error(request, f"Acesso negado. Apenas membros e o proprietário podem avaliar. Detalhe: {error_detail}")
                    context['can_evaluate'] = False
                elif response.status_code == 409: 
                    messages.warning(request, f"Você já avaliou este projeto. {error_detail}")
                    context['already_evaluated'] = True
                else:
                    messages.error(request, f"Erro ao enviar avaliação: Status {response.status_code}. Detalhe: {error_detail}")

            except requests.exceptions.RequestException as e:
                messages.error(request, f"Erro de conexão com a API ao tentar enviar a avaliação: {e}")
        
        context['form'] = form 
        
    return render(request, 'habilidades/avaliar_projeto.html', context)