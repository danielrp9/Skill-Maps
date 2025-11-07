# habilidades/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

# --------------------
# 1. MODELO DE USUÁRIO (QUEM)
# --------------------

# Definição das opções de Campus (Requisito Onde/Where)
CAMPUS_CHOICES = [
    ('DIA', 'Diamantina'),
    ('JAN', 'Janaúba'),
    ('UNA', 'Unaí'),
    ('MUC', 'Mucuri'),
]

class Usuario(AbstractUser):
    """
    Modelo de Usuário Customizado (SkillMap).
    Inclui informações necessárias para o mapeamento. (Requisito Quem)
    """
    curso = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        verbose_name="Curso (Ex: Ciência da Computação)"
    )
    
    campus = models.CharField(
        max_length=3, 
        choices=CAMPUS_CHOICES, 
        default='DIA',
        verbose_name="Campus de Atuação (Requisito Onde)"
    )
    
    # Relação ManyToMany com Habilidade (definida abaixo)
    # Será criada automaticamente pelo Django após a migração da Habilidade
    # suas_habilidades = models.ManyToManyField('Habilidade', blank=True, related_name='possuidores')

    class Meta:
        verbose_name = "Usuário (Quem)" 
        verbose_name_plural = "Usuários (Quem)"
        
    def __str__(self):
        return self.username

# --------------------
# 2. MODELO DE HABILIDADE (O QUE)
# --------------------

class Habilidade(models.Model):
    """
    Representa uma habilidade, conhecimento ou competência. (Requisito O Quê)
    """
    nome = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nome da Habilidade/Competência"
    )
    
    descricao = models.TextField(
        blank=True,
        verbose_name="Breve descrição da habilidade"
    )

    # Relação com os usuários que possuem esta habilidade
    usuarios = models.ManyToManyField(
        Usuario, 
        blank=True, 
        related_name='habilidades_cadastradas',
        verbose_name="Usuários que possuem esta habilidade"
    )

    class Meta:
        verbose_name = "Habilidade"
        verbose_name_plural = "Habilidades (O Quê)"
        
    def __str__(self):
        return self.nome

# --------------------
# 3. MODELO DE PROJETO/DEMANDA (O QUE, QUANDO, POR QUE)
# --------------------

class Projeto(models.Model):
    """
    Representa uma demanda ou projeto de colaboração comunitária.
    (Atende a Prestação de Serviços e Coleta de Opinião Pública)
    """
    # Requisito POR QUE (Motivação)
    titulo = models.CharField(max_length=200, verbose_name="Título da Demanda/Projeto")
    proposito = models.TextField(verbose_name="Descrição e Propósito da Colaboração (Requisito Por Quê)")
    
    # Requisito QUEM (Proponente)
    proponente = models.ForeignKey(
        Usuario, 
        on_delete=models.CASCADE,
        related_name='projetos_propostos',
        verbose_name="Proponente da Demanda (Requisito Quem)"
    )
    
    # Requisito QUANDO
    data_criacao = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="Data de Criação (Requisito Quando)"
    )
    
    # Relação com as habilidades necessárias
    habilidades_requeridas = models.ManyToManyField(
        Habilidade, 
        blank=True,
        related_name='projetos_requerem',
        verbose_name="Habilidades necessárias"
    )
    
    # Para Coleta de Opinião Pública (Status de Resposta)
    STATUS_CHOICES = [
        ('ABERTO', 'Aberto para Colaboração'),
        ('CONCLUIDO', 'Concluído/Atendido'),
        ('OPINIAO', 'Em Fase de Coleta de Opinião'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ABERTO')

    class Meta:
        verbose_name = "Projeto/Demanda"
        verbose_name_plural = "Projetos/Demandas (O Quê)"
        ordering = ['-data_criacao'] # Ordena pelo mais recente (Requisito Quando)
        
    def __str__(self):
        return self.titulo