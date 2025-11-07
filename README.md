# 🗺️ SkillMap: Mapeamento de Habilidades para Colaboração Comunitária

Este projeto é um protótipo de plataforma desenvolvido na UFVJM para mapear e conectar voluntariamente as habilidades de discentes e membros da comunidade, promovendo a cooperação em projetos e demandas. Trabalho desenvolvido para a disciplina de TCAC

## 🎯 Objetivo
O **SkillMap** visa desenvolver um ponto de encontro digital que permita aos membros da comunidade acadêmica registrar suas competências e encontrar outras pessoas para fomentar o voluntariado e a colaboração em iniciativas.

## 💻 Configuração Rápida do Ambiente (Início da Colaboração)

Siga estas etapas para configurar e rodar o projeto localmente.

### 1. Clonar e Navegar
git clone <Repositório> 
cd mapeamento-habilidades

### 2. Criar o ambiente virtual
python -m venv venv

# Ativar o ambiente virtual:
# Windows (PowerShell):
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

### 3. Instalar todas as Dependências
# Com o ambiente ativado, instale todas as bibliotecas listadas no requirements.txt:
pip install -r requirements.txt

### 4. Configurar Banco de Dados
# O projeto utiliza um Modelo de Usuário Customizado. Execute as migrações:
python manage.py migrate

### 5. Criar Superuser
# Crie o superusuário para acesso ao painel de gestão:
python manage.py createsuperuser

### 6. Inicie o servidor de desenvolvimento do Django:
python manage.py runserver
