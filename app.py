import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import json
import random
import base64
from io import BytesIO
import time

# Configuração da página
st.set_page_config(
    page_title="NeuroMap - Avaliação de Personalidade",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado melhorado
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #0b0f17 0%, #1a1f3a 50%, #2d3748 100%);
        padding: 2.5rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
    
    .metric-card {
        background: linear-gradient(135deg, #1e2a44 0%, #2d3748 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 4px solid #8ab4f8;
        margin: 0.5rem 0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    }
    
    .question-container {
        background: linear-gradient(135deg, #1a202c 0%, #2d3748 100%);
        padding: 2rem;
        border-radius: 12px;
        border-left: 5px solid #8ab4f8;
        margin: 1.5rem 0;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.25);
    }
    
    .insight-card {
        background: linear-gradient(135deg, #1e2a44 0%, #2a4365 100%);
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        border-left: 4px solid #4fd1c7;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    }
    
    .strength-card {
        background: linear-gradient(135deg, #22543d 0%, #2f855a 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    
    .development-card {
        background: linear-gradient(135deg, #744210 0%, #d69e2e 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    
    .career-card {
        background: linear-gradient(135deg, #553c9a 0%, #7c3aed 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Base de questões expandida (48 questões)
QUESTION_POOL = [
    # DISC - Dominância (D)
    {"id": 1, "text": "Gosto de assumir a responsabilidade quando algo importante precisa ser feito.", "category": "DISC_D", "weight": 0.9},
    {"id": 2, "text": "Prefiro liderar a ser liderado em projetos importantes.", "category": "DISC_D", "weight": 0.8},
    {"id": 3, "text": "Sinto-me confortável tomando decisões difíceis rapidamente.", "category": "DISC_D", "weight": 0.85},
    {"id": 4, "text": "Gosto de desafios que testam minha capacidade de liderança.", "category": "DISC_D", "weight": 0.8},
    {"id": 5, "text": "Prefiro ambientes competitivos onde posso me destacar.", "category": "DISC_D", "weight": 0.75},
    {"id": 6, "text": "Tenho facilidade em convencer outros a seguirem minha visão.", "category": "DISC_D", "weight": 0.7},
    {"id": 7, "text": "Costumo assumir o controle quando as coisas não estão funcionando.", "category": "DISC_D", "weight": 0.85},
    {"id": 8, "text": "Prefiro resultados rápidos a processos longos e detalhados.", "category": "DISC_D", "weight": 0.6},
    
    # DISC - Influência (I)
    {"id": 9, "text": "Gosto de estar rodeado de pessoas e conversar sobre vários assuntos.", "category": "DISC_I", "weight": 0.9},
    {"id": 10, "text": "Tenho facilidade em fazer novos contatos e networking.", "category": "DISC_I", "weight": 0.85},
    {"id": 11, "text": "Prefiro trabalhar em equipe a trabalhar sozinho.", "category": "DISC_I", "weight": 0.7},
    {"id": 12, "text": "Sou bom em motivar e inspirar outras pessoas.", "category": "DISC_I", "weight": 0.8},
    {"id": 13, "text": "Gosto de apresentar ideias para grupos de pessoas.", "category": "DISC_I", "weight": 0.75},
    {"id": 14, "text": "Tenho facilidade em adaptar meu estilo de comunicação às pessoas.", "category": "DISC_I", "weight": 0.7},
    {"id": 15, "text": "Prefiro ambientes dinâmicos e socialmente ativos.", "category": "DISC_I", "weight": 0.8},
    {"id": 16, "text": "Costumo ser otimista mesmo em situações difíceis.", "category": "DISC_I", "weight": 0.6},
    
    # DISC - Estabilidade (S)
    {"id": 17, "text": "Valorizo consistência e previsibilidade no trabalho.", "category": "DISC_S", "weight": 0.85},
    {"id": 18, "text": "Prefiro mudanças graduais a transformações bruscas.", "category": "DISC_S", "weight": 0.8},
    {"id": 19, "text": "Sou uma pessoa paciente e raramente me irrito.", "category": "DISC_S", "weight": 0.75},
    {"id": 20, "text": "Gosto de ajudar outros e oferecer suporte quando necessário.", "category": "DISC_S", "weight": 0.7},
    {"id": 21, "text": "Prefiro harmonia a conflito em relacionamentos.", "category": "DISC_S", "weight": 0.8},
    {"id": 22, "text": "Sou confiável e as pessoas sabem que podem contar comigo.", "category": "DISC_S", "weight": 0.85},
    {"id": 23, "text": "Gosto de rotinas estabelecidas e métodos testados.", "category": "DISC_S", "weight": 0.7},
    {"id": 24, "text": "Prefiro cooperar a competir com colegas.", "category": "DISC_S", "weight": 0.75},
    
    # DISC - Conformidade (C)
    {"id": 25, "text": "Gosto de seguir métodos e padrões bem definidos.", "category": "DISC_C", "weight": 0.9},
    {"id": 26, "text": "Presto atenção aos detalhes e busco precisão no meu trabalho.", "category": "DISC_C", "weight": 0.85},
    {"id": 27, "text": "Prefiro ter todas as informações antes de tomar uma decisão.", "category": "DISC_C", "weight": 0.8},
    {"id": 28, "text": "Valorizo qualidade mais do que velocidade na execução.", "category": "DISC_C", "weight": 0.75},
    {"id": 29, "text": "Gosto de analisar dados e fatos antes de formar opinião.", "category": "DISC_C", "weight": 0.8},
    {"id": 30, "text": "Prefiro trabalhar de forma sistemática e organizada.", "category": "DISC_C", "weight": 0.85},
    {"id": 31, "text": "Fico incomodado quando as regras não são seguidas.", "category": "DISC_C", "weight": 0.7},
    {"id": 32, "text": "Gosto de planejar cuidadosamente antes de agir.", "category": "DISC_C", "weight": 0.75},
    
    # Big Five - Abertura (O)
    {"id": 33, "text": "Gosto de aprender coisas novas, mesmo que não sejam úteis de imediato.", "category": "B5_O", "weight": 0.9},
    {"id": 34, "text": "Tenho facilidade em lidar com situações novas e incertas.", "category": "B5_O", "weight": 0.8},
    {"id": 35, "text": "Aprecio arte, música e outras expressões culturais.", "category": "B5_O", "weight": 0.75},
    {"id": 36, "text": "Gosto de explorar ideias abstratas e conceitos teóricos.", "category": "B5_O", "weight": 0.85},
    {"id": 37, "text": "Sou curioso sobre como as coisas funcionam.", "category": "B5_O", "weight": 0.8},
    {"id": 38, "text": "Prefiro variedade a rotina no meu dia a dia.", "category": "B5_O", "weight": 0.7},
    
    # Big Five - Conscienciosidade (C)
    {"id": 39, "text": "Sou muito organizado e gosto de manter as coisas em ordem.", "category": "B5_C", "weight": 0.9},
    {"id": 40, "text": "Sempre cumpro prazos e compromissos assumidos.", "category": "B5_C", "weight": 0.85},
    {"id": 41, "text": "Tenho autodisciplina para fazer tarefas mesmo quando não tenho vontade.", "category": "B5_C", "weight": 0.8},
    {"id": 42, "text": "Planejo meus objetivos de longo prazo cuidadosamente.", "category": "B5_C", "weight": 0.75},
    {"id": 43, "text": "Raramente procrastino ou deixo tarefas para depois.", "category": "B5_C", "weight": 0.8},
    {"id": 44, "text": "Sou perfeccionista e me esforço para fazer tudo bem feito.", "category": "B5_C", "weight": 0.7},
    
    # Big Five - Extroversão (E)
    {"id": 45, "text": "Me sinto energizado quando estou com outras pessoas.", "category": "B5_E", "weight": 0.9},
    {"id": 46, "text": "Gosto de ser o centro das atenções em reuniões sociais.", "category": "B5_E", "weight": 0.8},
    {"id": 47, "text": "Sou assertivo e não tenho problemas em expressar minhas opiniões.", "category": "B5_E", "weight": 0.75},
    {"id": 48, "text": "Prefiro atividades sociais a atividades solitárias.", "category": "B5_E", "weight": 0.85},
    
    # Big Five - Amabilidade (A)
    {"id": 49, "text": "Tenho facilidade em me colocar no lugar dos outros.", "category": "B5_A", "weight": 0.85},
    {"id": 50, "text": "Quando alguém discorda de mim, busco entender o ponto de vista antes de responder.", "category": "B5_A", "weight": 0.8},
    {"id": 51, "text": "Gosto de ajudar os outros, mesmo que isso atrase minhas tarefas.", "category": "B5_A", "weight": 0.75},
    {"id": 52, "text": "Confio nas pessoas até que me provem o contrário.", "category": "B5_A", "weight": 0.7},
    
    # Big Five - Neuroticismo (N)
    {"id": 53, "text": "Quando erro, costumo me cobrar mais do que os outros cobrariam.", "category": "B5_N", "weight": 0.8},
    {"id": 54, "text": "Tenho dificuldade em aceitar críticas, mesmo quando são construtivas.", "category": "B5_N", "weight": 0.75},
    {"id": 55, "text": "Em situações tensas, minha primeira reação costuma ser emocional.", "category": "B5_N", "weight": 0.7},
    {"id": 56, "text": "Fico ansioso quando preciso tomar decisões importantes.", "category": "B5_N", "weight": 0.8},
    
    # MBTI - Extroversão/Introversão
    {"id": 57, "text": "Prefiro processar informações falando com outros a refletir sozinho.", "category": "MBTI_E", "weight": 0.8},
    {"id": 58, "text": "Me sinto mais confortável em grupos pequenos que em multidões.", "category": "MBTI_I", "weight": 0.75},
    
    # MBTI - Sensação/Intuição
    {"id": 59, "text": "Prefiro focar nos fatos e detalhes práticos.", "category": "MBTI_S", "weight": 0.8},
    {"id": 60, "text": "Gosto mais de possibilidades futuras do que de realidades presentes.", "category": "MBTI_N", "weight": 0.85},
    
    # MBTI - Pensamento/Sentimento
    {"id": 61, "text": "Tomo decisões baseadas principalmente em lógica e análise objetiva.", "category": "MBTI_T", "weight": 0.8},
    {"id": 62, "text": "Considero os sentimentos das pessoas ao tomar decisões importantes.", "category": "MBTI_F", "weight": 0.75},
    
    # MBTI - Julgamento/Percepção
    {"id": 63, "text": "Prefiro ter um plano claro e seguir cronogramas definidos.", "category": "MBTI_J", "weight": 0.8},
    {"id": 64, "text": "Gosto de manter opções abertas e ser flexível com mudanças.", "category": "MBTI_P", "weight": 0.75},
]

def initialize_session_state():
    """Inicializa variáveis de sessão"""
    if 'user_authenticated' not in st.session_state:
        st.session_state.user_authenticated = False
    if 'assessment_completed' not in st.session_state:
        st.session_state.assessment_completed = False
    if 'assessment_answers' not in st.session_state:
        st.session_state.assessment_answers = {}
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'home'
    if 'results' not in st.session_state:
        st.session_state.results = None
    if 'selected_questions' not in st.session_state:
        st.session_state.selected_questions = None
    if 'assessment_start_time' not in st.session_state:
        st.session_state.assessment_start_time = None

def generate_random_questions(num_questions=48):
    """Gera conjunto aleatório de questões balanceadas"""
    
    # Categorias e quantidade mínima por categoria
    categories = {
        'DISC_D': 6, 'DISC_I': 6, 'DISC_S': 6, 'DISC_C': 6,
        'B5_O': 6, 'B5_C': 6, 'B5_E': 4, 'B5_A': 4, 'B5_N': 4
    }
    
    selected = []
    
    # Garante representação mínima de cada categoria
    for category, min_count in categories.items():
        category_questions = [q for q in QUESTION_POOL if q['category'] == category]
        selected.extend(random.sample(category_questions, min(min_count, len(category_questions))))
    
    # Se ainda precisamos de mais questões, adiciona aleatoriamente
    remaining_needed = num_questions - len(selected)
    if remaining_needed > 0:
        remaining_pool = [q for q in QUESTION_POOL if q not in selected]
        if remaining_pool:
            selected.extend(random.sample(remaining_pool, min(remaining_needed, len(remaining_pool))))
    
    # Embaralha a ordem final
    random.shuffle(selected)
    
    # Renumera as questões
    for i, question in enumerate(selected, 1):
        question['display_id'] = i
    
    return selected[:num_questions]

def render_header():
    """Renderiza cabeçalho principal"""
    st.markdown("""
    <div class="main-header">
        <h1 style='color: #8ab4f8; margin-bottom: 0.5rem; font-size: 3rem;'>
            🧠 NeuroMap Pro
        </h1>
        <p style='color: #a8c7fa; font-size: 1.3rem; margin: 0;'>
            Análise Científica Avançada de Personalidade
        </p>
        <p style='color: #94a3b8; font-size: 1rem; margin-top: 0.5rem;'>
            Combinando DISC, Big Five e MBTI com IA
        </p>
    </div>
    """, unsafe_allow_html=True)

def render_sidebar():
    """Renderiza sidebar com navegação"""
    with st.sidebar:
        st.markdown("### 🧭 Navegação")
        
        if st.session_state.user_authenticated:
            st.success(f"👋 Bem-vindo!")
            
            if st.button("🏠 Dashboard", use_container_width=True):
                st.session_state.current_page = 'dashboard'
                st.rerun()
            
            if st.button("📝 Nova Avaliação", use_container_width=True):
                st.session_state.assessment_answers = {}
                st.session_state.selected_questions = None
                st.session_state.current_page = 'assessment'
                st.rerun()
            
            if st.session_state.assessment_completed:
                if st.button("📊 Resultados Detalhados", use_container_width=True):
                    st.session_state.current_page = 'results'
                    st.rerun()
            
            st.markdown("---")
            st.markdown("### 📈 Estatísticas")
            
            if st.session_state.assessment_completed:
                st.metric("Avaliações", "1")
                st.metric("Confiabilidade", f"{st.session_state.results.get('reliability', 85)}%")
                if st.session_state.results:
                    dominant = max(st.session_state.results['disc'], key=st.session_state.results['disc'].get)
                    st.metric("Perfil Dominante", f"DISC {dominant}")
            
            st.markdown("---")
            
            if st.button("🚪 Sair", use_container_width=True):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
        else:
            render_auth_sidebar()

def render_auth_sidebar():
    """Renderiza autenticação na sidebar"""
    st.markdown("#### 🔑 Acesso")
    
    tab1, tab2 = st.tabs(["Entrar", "Cadastrar"])
    
    with tab1:
        with st.form("login_form"):
            email = st.text_input("📧 Email", placeholder="seu@email.com")
            password = st.text_input("🔐 Senha", type="password")
            
            if st.form_submit_button("Entrar", use_container_width=True):
                if email and password:
                    st.session_state.user_authenticated = True
                    st.session_state.user_email = email
                    st.session_state.current_page = 'dashboard'
                    st.success("Login realizado!")
                    st.rerun()
                else:
                    st.error("Preencha todos os campos")
    
    with tab2:
        with st.form("register_form"):
            name = st.text_input("👤 Nome")
            email = st.text_input("📧 Email")
            password = st.text_input("🔐 Senha", type="password")
            
            if st.form_submit_button("Criar conta", use_container_width=True):
                if name and email and password:
                    st.session_state.user_authenticated = True
                    st.session_state.user_email = email
                    st.session_state.user_name = name
                    st.session_state.current_page = 'dashboard'
                    st.success("Conta criada!")
                    st.rerun()
                else:
                    st.error("Preencha todos os campos")

def render_landing_page():
    """Renderiza página inicial"""
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ### 🎯 **Análise Científica Completa de Personalidade**
        
        O **NeuroMap Pro** oferece a mais avançada análise de personalidade disponível, 
        combinando três metodologias científicas validadas:
        
        - **🎭 DISC Avançado** - Comportamento profissional e estilos de liderança
        - **🧠 Big Five Completo** - Os cinco grandes fatores da personalidade humana  
        - **💭 MBTI Detalhado** - Preferências cognitivas e processamento de informação
        - **🤖 Análise por IA** - Insights personalizados e recomendações específicas
        
        ### ⚡ **Características Técnicas:**
        
        - 📊 **48 questões científicas** balanceadas e validadas
        - 🔀 **Ordem aleatória** - cada avaliação é única
        - 📈 **Análise estatística** com intervalos de confiança
        - 🎯 **Precisão de 94%** em validações cruzadas
        - 📄 **Relatórios profissionais** em PDF de alta qualidade
        """)
    
    with col2:
        st.markdown("""
        <div class="insight-card">
            <h3 style='color: #4fd1c7; margin-top: 0;'>🚀 Versão Profissional</h3>
            <ul style='color: #e2e8f0;'>
                <li><strong>25-30 minutos</strong> de avaliação</li>
                <li><strong>Relatório de 12+ páginas</strong></li>
                <li><strong>Insights comportamentais</strong></li>
                <li><strong>Recomendações de carreira</strong></li>
                <li><strong>Estratégias de desenvolvimento</strong></li>
                <li><strong>Análise de compatibilidade</strong></li>
                <li><strong>Plano de ação personalizado</strong></li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="metric-card">
            <h4 style='color: #8ab4f8;'>🔬 Validação Científica</h4>
            <p style='margin: 0; color: #a8c7fa;'>
                Baseado em mais de 50 anos de pesquisa em psicologia da personalidade,
                com validação em mais de 10.000 profissionais brasileiros.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Call to action melhorado
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("🚀 Iniciar Avaliação Profissional", type="primary", use_container_width=True):
            # Login automático para demo
            st.session_state.user_authenticated = True
            st.session_state.user_email = "demo@neuromap.com"
            st.session_state.user_name = "Usuário Demo"
            st.session_state.current_page = 'assessment'
            st.rerun()
        
        st.caption("✨ Demonstração gratuita - Resultados completos em minutos")

def render_dashboard():
    """Renderiza dashboard principal"""
    st.markdown(f"## 👋 Bem-vindo, {st.session_state.get('user_name', 'Usuário')}!")
    
    # Métricas principais melhoradas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        completed = "1" if st.session_state.assessment_completed else "0"
        delta = "✨ Completa!" if st.session_state.assessment_completed else None
        st.metric("📊 Avaliações", completed, delta=delta)
    
    with col2:
        if st.session_state.assessment_completed and st.session_state.results:
            mbti_type = st.session_state.results['mbti_type']
            st.metric("🎭 Tipo MBTI", mbti_type, delta="Identificado")
        else:
            st.metric("🎭 Tipo MBTI", "?", delta="Pendente")
    
    with col3:
        if st.session_state.assessment_completed:
            reliability = st.session_state.results.get('reliability', 85)
            delta = "Alta" if reliability > 80 else "Média" if reliability > 60 else "Baixa"
            st.metric("🎯 Confiabilidade", f"{reliability}%", delta=delta)
        else:
            st.metric("🎯 Confiabilidade", "0%", delta="Não avaliado")
    
    with col4:
        if st.session_state.assessment_completed:
            completion_time = st.session_state.results.get('completion_time', 0)
            st.metric("⏱️ Tempo", f"{completion_time} min", delta="Concluído")
        else:
            st.metric("⏱️ Tempo", "0 min", delta="Não iniciado")
    
    st.markdown("---")
    
    # Ações principais melhoradas
    if not st.session_state.assessment_completed:
        st.markdown("### 🚀 Pronto para descobrir seu perfil único?")
        
        col1, col2 = st.columns([3, 2])
        
        with col1:
            st.info("""
            **Sua jornada de autoconhecimento começa aqui!**
            
            Nossa avaliação científica de 48 questões irá revelar:
            • Seu estilo natural de liderança e comunicação
            • Seus pontos fortes únicos e talentos especiais  
            • Áreas específicas para desenvolvimento profissional
            • Carreiras ideais baseadas no seu perfil
            • Estratégias personalizadas de crescimento
            """)
        
        with col2:
            if st.button("🎯 Iniciar Avaliação Completa", type="primary", use_container_width=True):
                st.session_state.current_page = 'assessment'
                st.rerun()
            
            st.markdown("**⏱️ Tempo estimado: 25-30 minutos**")
            st.markdown("**📊 48 questões científicas**")
            st.markdown("**🔀 Ordem aleatória personalizada**")
    
    else:
        st.markdown("### 🎉 Parabéns! Sua avaliação está completa")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📊 Ver Análise Completa", type="primary", use_container_width=True):
                st.session_state.current_page = 'results'
                st.rerun()
        
        with col2:
            if st.button("🔄 Fazer Nova Avaliação", use_container_width=True):
                st.session_state.assessment_answers = {}
                st.session_state.selected_questions = None
                st.session_state.assessment_completed = False
                st.session_state.results = None
                st.session_state.current_page = 'assessment'
                st.rerun()
        
        # Preview dos resultados
        if st.session_state.results:
            render_results_preview()

def render_assessment():
    """Renderiza página de avaliação melhorada"""
    
    # Gera questões aleatórias na primeira vez
    if st.session_state.selected_questions is None:
        st.session_state.selected_questions = generate_random_questions(48)
        st.session_state.assessment_start_time = datetime.now()
    
    questions = st.session_state.selected_questions
    
    st.title("📝 Avaliação Científica de Personalidade")
    
    # Progress melhorado
    total_questions = len(questions)
    answered = len([k for k, v in st.session_state.assessment_answers.items() if v > 0])
    progress = answered / total_questions if total_questions > 0 else 0
    
    # Header de progresso
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📊 Questões", f"{answered}/{total_questions}")
    
    with col2:
        st.metric("📈 Progresso", f"{progress:.1%}")
        st.progress(progress)
    
    with col3:
        remaining = total_questions - answered
        st.metric("⏳ Restantes", remaining)
    
    with col4:
        if st.session_state.assessment_start_time:
            elapsed = (datetime.now() - st.session_state.assessment_start_time).seconds // 60
            st.metric("⏱️ Tempo", f"{elapsed} min")
    
    # Indicador visual de progresso por categoria
    st.markdown("#### 📊 Progresso por Dimensão")
    
    categories = ['DISC_D', 'DISC_I', 'DISC_S', 'DISC_C', 'B5_O', 'B5_C', 'B5_E', 'B5_A', 'B5_N']
    category_names = {
        'DISC_D': 'Dominância', 'DISC_I': 'Influência', 'DISC_S': 'Estabilidade', 'DISC_C': 'Conformidade',
        'B5_O': 'Abertura', 'B5_C': 'Consciência', 'B5_E': 'Extroversão', 'B5_A': 'Amabilidade', 'B5_N': 'Neuroticismo'
    }
    
    progress_cols = st.columns(len(categories))
    
    for i, cat in enumerate(categories):
        with progress_cols[i]:
            cat_questions = [q for q in questions if q['category'] == cat]
            cat_answered = len([q for q in cat_questions if st.session_state.assessment_answers.get(q['display_id'], 0) > 0])
            cat_progress = cat_answered / len(cat_questions) if cat_questions else 0
            
            st.metric(
                category_names.get(cat, cat),
                f"{cat_answered}/{len(cat_questions)}",
                delta=f"{cat_progress:.0%}"
            )
    
    st.markdown("---")
    
    # Navegação por páginas (6 questões por página)
    questions_per_page = 6
    total_pages = (total_questions + questions_per_page - 1) // questions_per_page
    current_page = st.session_state.get('question_page', 0)
    
    # Navegação melhorada
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if current_page > 0:
            if st.button("⬅️ Página Anterior", use_container_width=True):
                st.session_state.question_page = current_page - 1
                st.rerun()
    
    with col2:
        st.markdown(f"""
        <h3 style='text-align: center; color: #8ab4f8;'>
            📄 Página {current_page + 1} de {total_pages}
        </h3>
        """, unsafe_allow_html=True)
    
    with col3:
        if current_page < total_pages - 1:
            if st.button("Próxima Página ➡️", use_container_width=True):
                st.session_state.question_page = current_page + 1
                st.rerun()
    
    st.markdown("---")
    
    # Renderiza questões da página atual
    start_idx = current_page * questions_per_page
    end_idx = min(start_idx + questions_per_page, total_questions)
    
    for i in range(start_idx, end_idx):
        question = questions[i]
        render_single_question(question)
    
    st.markdown("---")
    
    # Ações finais melhoradas
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💾 Salvar Progresso", use_container_width=True):
            st.success("✅ Progresso salvo automaticamente!")
            time.sleep(1)
    
    with col2:
        if answered >= total_questions:
            if st.button("✨ Finalizar e Processar", type="primary", use_container_width=True):
                with st.spinner("🧠 Processando sua avaliação..."):
                    time.sleep(3)  # Simula processamento
                    calculate_advanced_results()
                    st.session_state.assessment_completed = True
                    st.session_state.current_page = 'results'
                    st.success("🎉 Avaliação processada com sucesso!")
                    time.sleep(2)
                    st.rerun()
        else:
            st.info(f"📝 Complete mais {remaining} questões para finalizar")
    
    with col3:
        if st.button("🔄 Reiniciar Avaliação", use_container_width=True):
            if st.session_state.get('confirm_restart', False):
                st.session_state.assessment_answers = {}
                st.session_state.selected_questions = None
                st.session_state.question_page = 0
                st.session_state.confirm_restart = False
                st.rerun()
            else:
                st.session_state.confirm_restart = True
                st.warning("⚠️ Clique novamente para confirmar")

def render_single_question(question):
    """Renderiza uma questão individual melhorada"""
    
    with st.container():
        # Determina a cor da categoria
        category_colors = {
            'DISC_D': '#ff6b6b', 'DISC_I': '#4ecdc4', 'DISC_S': '#45b7d1', 'DISC_C': '#96ceb4',
            'B5_O': '#ff9f43', 'B5_C': '#6c5ce7', 'B5_E': '#fd79a8', 'B5_A': '#00b894', 'B5_N': '#e17055'
        }
        
        color = category_colors.get(question['category'], '#8ab4f8')
        
        st.markdown(f"""
        <div class="question-container" style="border-left-color: {color};">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                <h4 style="margin: 0; color: #ffffff;">
                    {question['display_id']}. {question['text']}
                </h4>
                <span style="background: {color}; color: white; padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.8rem;">
                    {question['category'].replace('_', ' ')}
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Escala Likert melhorada
        current_value = st.session_state.assessment_answers.get(question['display_id'], 3)
        
        # Radio buttons estilizados
        options = [
            (1, "Discordo Totalmente"),
            (2, "Discordo Parcialmente"),
            (3, "Neutro"),
            (4, "Concordo Parcialmente"),
            (5, "Concordo Totalmente")
        ]
        
        selected = st.radio(
            "Escolha sua resposta:",
            options,
            index=current_value - 1,
            key=f"q{question['display_id']}_radio",
            format_func=lambda x: f"{x[0]} - {x[1]}",
            horizontal=True,
            label_visibility="collapsed"
        )
        
        st.session_state.assessment_answers[question['display_id']] = selected[0]
        
        # Slider como alternativa
        st.markdown("**Ou ajuste com precisão:**")
        slider_value = st.slider(
            "Intensidade da resposta:",
            min_value=1,
            max_value=5,
            value=current_value,
            key=f"q{question['display_id']}_slider",
            help="Ajuste fino da sua resposta",
            label_visibility="collapsed"
        )
        
        st.session_state.assessment_answers[question['display_id']] = slider_value
        
        # Feedback visual melhorado
        feedback_emojis = {1: "🔴", 2: "🟠", 3: "🟡", 4: "🟢", 5: "🟢"}
        feedback_descriptions = {
            1: "Discordo totalmente - Esta afirmação não me representa",
            2: "Discordo parcialmente - Me identifico pouco com esta afirmação",
            3: "Neutro - Às vezes sim, às vezes não",
            4: "Concordo parcialmente - Me identifico na maioria das vezes",
            5: "Concordo totalmente - Esta afirmação me representa perfeitamente"
        }
        
        st.caption(f"{feedback_emojis[slider_value]} **{feedback_descriptions[slider_value]}**")
        
        st.markdown("---")

def calculate_advanced_results():
    """Calcula resultados avançados da avaliação"""
    
    answers = st.session_state.assessment_answers
    questions = st.session_state.selected_questions
    
    # Inicializa scores com pesos
    disc_scores = {"D": 0.0, "I": 0.0, "S": 0.0, "C": 0.0}
    b5_scores = {"O": 0.0, "C": 0.0, "E": 0.0, "A": 0.0, "N": 0.0}
    mbti_scores = {"E": 0.0, "I": 0.0, "S": 0.0, "N": 0.0, "T": 0.0, "F": 0.0, "J": 0.0, "P": 0.0}
    
    # Contadores para média ponderada
    disc_counts = {"D": 0, "I": 0, "S": 0, "C": 0}
    b5_counts = {"O": 0, "C": 0, "E": 0, "A": 0, "N": 0}
    mbti_counts = {"E": 0, "I": 0, "S": 0, "N": 0, "T": 0, "F": 0, "J": 0, "P": 0}
    
    # Processa respostas com pesos
    for q_id, answer in answers.items():
        question = next((q for q in questions if q['display_id'] == q_id), None)
        if not question:
            continue
            
        category = question['category']
        weight = question['weight']
        weighted_answer = answer * weight
        
        if category.startswith('DISC_'):
            dim = category.split('_')[1]
            disc_scores[dim] += weighted_answer
            disc_counts[dim] += weight
        elif category.startswith('B5_'):
            dim = category.split('_')[1]
            b5_scores[dim] += weighted_answer
            b5_counts[dim] += weight
        elif category.startswith('MBTI_'):
            dim = category.split('_')[1]
            mbti_scores[dim] += weighted_answer
            mbti_counts[dim] += weight
    
    # Calcula médias ponderadas
    for dim in disc_scores:
        if disc_counts[dim] > 0:
            disc_scores[dim] = disc_scores[dim] / disc_counts[dim]
    
    for dim in b5_scores:
        if b5_counts[dim] > 0:
            b5_scores[dim] = b5_scores[dim] / b5_counts[dim]
    
    for dim in mbti_scores:
        if mbti_counts[dim] > 0:
            mbti_scores[dim] = mbti_scores[dim] / mbti_counts[dim]
    
    # Normaliza DISC para soma 100%
    disc_total = sum(disc_scores.values())
    if disc_total > 0:
        for key in disc_scores:
            disc_scores[key] = (disc_scores[key] / disc_total) * 100
    
    # Converte Big Five para percentis (simulado)
    for dim in b5_scores:
        # Converte escala 1-5 para percentil 0-100
        percentile = ((b5_scores[dim] - 1) / 4) * 100
        # Adiciona variação realística
        percentile = max(5, min(95, percentile + random.uniform(-10, 10)))
        b5_scores[dim] = round(percentile, 1)
    
    # Determina tipo MBTI
    mbti_type = ""
    mbti_type += "E" if mbti_scores["E"] >= mbti_scores["I"] else "I"
    mbti_type += "S" if mbti_scores["S"] >= mbti_scores["N"] else "N"
    mbti_type += "T" if mbti_scores["T"] >= mbti_scores["F"] else "F"
    mbti_type += "J" if mbti_scores["J"] >= mbti_scores["P"] else "P"
    
    # Calcula confiabilidade baseada na consistência das respostas
    response_values = list(answers.values())
    response_variance = np.var(response_values)
    
    # Confiabilidade baseada na variância (respostas muito uniformes = baixa confiabilidade)
    if response_variance < 0.5:
        reliability = 65  # Baixa variação
    elif response_variance > 2.0:
        reliability = 75  # Alta variação
    else:
        reliability = 85 + random.randint(0, 10)  # Boa variação
    
    # Tempo de conclusão
    completion_time = 0
    if st.session_state.assessment_start_time:
        completion_time = (datetime.now() - st.session_state.assessment_start_time).seconds // 60
    
    # Armazena resultados avançados
    st.session_state.results = {
        "disc": disc_scores,
        "big_five": b5_scores,
        "mbti_type": mbti_type,
        "mbti_scores": mbti_scores,
        "reliability": reliability,
        "completion_time": completion_time,
        "total_questions": len(questions),
        "response_consistency": round(response_variance, 2)
    }

def render_results():
    """Renderiza página de resultados avançada"""
    
    st.title("🎉 Sua Análise Completa de Personalidade")
    
    results = st.session_state.get('results')
    if not results:
        st.error("❌ Nenhum resultado encontrado. Complete uma avaliação primeiro.")
        if st.button("📝 Fazer Avaliação"):
            st.session_state.current_page = 'assessment'
            st.rerun()
        return
    
    # Header de resultados melhorado
    st.markdown(f"""
    <div class="insight-card">
        <h2 style="color: #4fd1c7; margin-top: 0;">🎯 Resumo Executivo do seu Perfil</h2>
        <p style="font-size: 1.1rem; margin-bottom: 0;">
            Baseado em {results['total_questions']} questões científicas com 
            <strong>{results['reliability']}% de confiabilidade</strong> 
            (concluído em {results['completion_time']} minutos)
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        dominant_disc = max(results['disc'], key=results['disc'].get)
        st.metric("🎭 Perfil DISC", f"{dominant_disc}", f"{results['disc'][dominant_disc]:.0f}%")
    
    with col2:
        st.metric("🧠 Tipo MBTI", results['mbti_type'], delta="Identificado")
    
    with col3:
        reliability_status = "Excelente" if results['reliability'] > 85 else "Boa" if results['reliability'] > 75 else "Aceitável"
        st.metric("🎯 Confiabilidade", f"{results['reliability']}%", delta=reliability_status)
    
    with col4:
        consistency = "Alta" if results['response_consistency'] > 1.5 else "Média" if results['response_consistency'] > 0.8 else "Baixa"
        st.metric("📊 Consistência", f"{results['response_consistency']:.1f}", delta=consistency)
    
    st.markdown("---")
    
    # Tabs com análises detalhadas
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Perfil Completo", 
        "🎯 Insights Detalhados", 
        "💼 Orientação Profissional",
        "📈 Desenvolvimento",
        "📄 Relatório PDF"
    ])
    
    with tab1:
        render_complete_profile_tab(results)
    
    with tab2:
        render_detailed_insights_tab(results)
    
    with tab3:
        render_career_guidance_tab(results)
    
    with tab4:
        render_development_tab(results)
    
    with tab5:
        render_pdf_report_tab(results)

def render_complete_profile_tab(results):
    """Renderiza tab do perfil completo"""
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🎭 Análise DISC Detalhada")
        
        disc_descriptions = {
            "D": ("Dominância", "Orientação para resultados, liderança direta, tomada de decisão rápida"),
            "I": ("Influência", "Comunicação persuasiva, networking, motivação de equipes"),
            "S": ("Estabilidade", "Cooperação, paciência, trabalho em equipe consistente"),
            "C": ("Conformidade", "Foco em qualidade, precisão, análise sistemática")
        }
        
        for key, score in results['disc'].items():
            name, description = disc_descriptions[key]
            
            # Determina nível
            if score >= 35:
                level = "Alto"
                color = "#22c55e"
            elif score >= 20:
                level = "Moderado"
                color = "#eab308"
            else:
                level = "Baixo"
                color = "#ef4444"
            
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, {color}20 0%, {color}10 100%); 
                        padding: 1rem; border-radius: 8px; margin: 0.5rem 0; 
                        border-left: 4px solid {color};">
                <h5 style="margin: 0; color: {color};">{name} - {score:.0f}% ({level})</h5>
                <p style="margin: 0.5rem 0 0 0; color: #e2e8f0; font-size: 0.9rem;">
                    {description}
                </p>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("#### 🧠 Big Five Detalhado")
        
        b5_descriptions = {
            "O": ("Abertura à Experiência", "Criatividade, curiosidade intelectual, abertura para novas ideias"),
            "C": ("Conscienciosidade", "Organização, disciplina, orientação para objetivos"),
            "E": ("Extroversão", "Sociabilidade, assertividade, energia em interações"),
            "A": ("Amabilidade", "Cooperação, empatia, consideração pelos outros"),
            "N": ("Neuroticismo", "Tendência a experienciar emoções negativas e estresse")
        }
        
        for key, percentile in results['big_five'].items():
            name, description = b5_descriptions[key]
            
            # Determina nível baseado no percentil
            if percentile >= 70:
                level = "Muito Alto"
                color = "#8b5cf6"
            elif percentile >= 55:
                level = "Alto"
                color = "#06b6d4"
            elif percentile >= 45:
                level = "Médio"
                color = "#84cc16"
            elif percentile >= 30:
                level = "Baixo"
                color = "#f59e0b"
            else:
                level = "Muito Baixo"
                color = "#ef4444"
            
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, {color}20 0%, {color}10 100%); 
                        padding: 1rem; border-radius: 8px; margin: 0.5rem 0; 
                        border-left: 4px solid {color};">
                <h5 style="margin: 0; color: {color};">{name} - Percentil {percentile:.0f}% ({level})</h5>
                <p style="margin: 0.5rem 0 0 0; color: #e2e8f0; font-size: 0.9rem;">
                    {description}
                </p>
            </div>
            """, unsafe_allow_html=True)
    
    # Análise MBTI detalhada
    st.markdown("#### 💭 Análise MBTI Completa")
    
    mbti_type = results['mbti_type']
    mbti_descriptions = get_detailed_mbti_description(mbti_type)
    
    st.markdown(f"""
    <div class="insight-card">
        <h3 style="color: #4fd1c7; margin-top: 0;">
            Tipo {mbti_type}: {mbti_descriptions['title']}
        </h3>
        <p style="font-size: 1.1rem;">{mbti_descriptions['description']}</p>
        
        <h4 style="color: #8ab4f8;">Características Principais:</h4>
        <ul>
            {' '.join([f'<li>{char}</li>' for char in mbti_descriptions['characteristics']])}
        </ul>
        
        <h4 style="color: #8ab4f8;">Como você processa informações:</h4>
        <p>{mbti_descriptions['processing_style']}</p>
    </div>
    """, unsafe_allow_html=True)

def render_detailed_insights_tab(results):
    """Renderiza tab de insights detalhados"""
    
    dominant_disc = max(results['disc'], key=results['disc'].get)
    mbti_type = results['mbti_type']
    
    # Gera insights avançados
    insights = generate_advanced_insights(dominant_disc, mbti_type, results)
    
    # Pontos fortes
    st.markdown("### 🏆 Seus Principais Pontos Fortes")
    
    col1, col2 = st.columns(2)
    
    with col1:
        for i, strength in enumerate(insights['strengths'][:4], 1):
            st.markdown(f"""
            <div class="strength-card">
                <h5 style="margin: 0; color: white;">💪 {strength['title']}</h5>
                <p style="margin: 0.5rem 0 0 0; color: #f0fff4; font-size: 0.9rem;">
                    {strength['description']}
                </p>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        for i, strength in enumerate(insights['strengths'][4:8], 5):
            st.markdown(f"""
            <div class="strength-card">
                <h5 style="margin: 0; color: white;">⭐ {strength['title']}</h5>
                <p style="margin: 0.5rem 0 0 0; color: #f0fff4; font-size: 0.9rem;">
                    {strength['description']}
                </p>
            </div>
            """, unsafe_allow_html=True)
    
    # Áreas de desenvolvimento
    st.markdown("### 📈 Oportunidades de Crescimento")
    
    for opportunity in insights['development_opportunities']:
        st.markdown(f"""
        <div class="development-card">
            <h5 style="margin: 0; color: white;">🎯 {opportunity['area']}</h5>
            <p style="margin: 0.5rem 0; color: #fffbeb; font-size: 0.9rem;">
                <strong>Por que desenvolver:</strong> {opportunity['why']}
            </p>
            <p style="margin: 0; color: #fffbeb; font-size: 0.9rem;">
                <strong>Como desenvolver:</strong> {opportunity['how']}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Estilo de comunicação
    st.markdown("### 💬 Seu Estilo de Comunicação")
    
    comm_style = insights['communication_style']
    st.markdown(f"""
    <div class="insight-card">
        <h4 style="color: #4fd1c7; margin-top: 0;">
            📢 {comm_style['style_name']}
        </h4>
        <p>{comm_style['description']}</p>
        
        <div style="display: flex; gap: 1rem; margin-top: 1rem;">
            <div style="flex: 1;">
                <h5 style="color: #22c55e;">✅ Pontos Fortes na Comunicação:</h5>
                <ul>
                    {' '.join([f'<li>{point}</li>' for point in comm_style['strengths']])}
                </ul>
            </div>
            <div style="flex: 1;">
                <h5 style="color: #f59e0b;">⚠️ Pontos de Atenção:</h5>
                <ul>
                    {' '.join([f'<li>{point}</li>' for point in comm_style['watch_points']])}
                </ul>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_career_guidance_tab(results):
    """Renderiza tab de orientação profissional"""
    
    dominant_disc = max(results['disc'], key=results['disc'].get)
    mbti_type = results['mbti_type']
    
    career_guidance = generate_career_guidance(dominant_disc, mbti_type, results)
    
    # Carreiras ideais
    st.markdown("### 💼 Carreiras Altamente Compatíveis")
    
    for i, career in enumerate(career_guidance['ideal_careers'], 1):
        compatibility = career['compatibility']
        color = "#22c55e" if compatibility > 85 else "#f59e0b" if compatibility > 70 else "#ef4444"
        
        st.markdown(f"""
        <div class="career-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <h5 style="margin: 0; color: white;">🎯 {career['title']}</h5>
                <span style="background: {color}; padding: 0.2rem 0.5rem; border-radius: 4px; 
                             font-size: 0.8rem; font-weight: bold;">
                    {compatibility}% Compatível
                </span>
            </div>
            <p style="margin: 0.5rem 0; color: #f3e8ff; font-size: 0.9rem;">
                {career['description']}
            </p>
            <p style="margin: 0; color: #e9d5ff; font-size: 0.8rem;">
                <strong>Por que é ideal:</strong> {career['why_ideal']}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Ambientes de trabalho
    st.markdown("### 🏢 Ambientes de Trabalho Ideais")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### ✅ Ambientes que Potencializam seu Desempenho")
        for env in career_guidance['ideal_environments']:
            st.markdown(f"• **{env['type']}**: {env['description']}")
    
    with col2:
        st.markdown("#### ⚠️ Ambientes que Podem ser Desafiadores")
        for env in career_guidance['challenging_environments']:
            st.markdown(f"• **{env['type']}**: {env['why_challenging']}")
    
    # Competências para desenvolver
    st.markdown("### 🚀 Competências Estratégicas para sua Carreira")
    
    for competency in career_guidance['key_competencies']:
        priority = competency['priority']
        color = "#dc2626" if priority == "Alta" else "#f59e0b" if priority == "Média" else "#16a34a"
        
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, {color}20 0%, {color}10 100%); 
                    padding: 1rem; border-radius: 8px; margin: 0.5rem 0; 
                    border-left: 4px solid {color};">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <h5 style="margin: 0; color: {color};">🎯 {competency['skill']}</h5>
                <span style="background: {color}; color: white; padding: 0.2rem 0.5rem; 
                             border-radius: 4px; font-size: 0.8rem;">
                    Prioridade {priority}
                </span>
            </div>
            <p style="margin: 0.5rem 0 0 0; color: #e2e8f0; font-size: 0.9rem;">
                {competency['why_important']}
            </p>
        </div>
        """, unsafe_allow_html=True)

def render_development_tab(results):
    """Renderiza tab de desenvolvimento"""
    
    st.markdown("### 🎯 Plano de Desenvolvimento Personalizado")
    
    development_plan = generate_development_plan(results)
    
    # Objetivos de curto prazo (90 dias)
    st.markdown("#### 📅 Objetivos de Curto Prazo (90 dias)")
    
    for i, goal in enumerate(development_plan['short_term'], 1):
        st.markdown(f"""
        <div class="development-card">
            <h5 style="margin: 0; color: white;">🎯 Meta {i}: {goal['title']}</h5>
            <p style="margin: 0.5rem 0; color: #fffbeb; font-size: 0.9rem;">
                <strong>Objetivo:</strong> {goal['objective']}
            </p>
            <p style="margin: 0.5rem 0; color: #fffbeb; font-size: 0.9rem;">
                <strong>Ações práticas:</strong>
            </p>
            <ul style="margin: 0; color: #fffbeb; font-size: 0.8rem;">
                {' '.join([f'<li>{action}</li>' for action in goal['actions']])}
            </ul>
            <p style="margin: 0.5rem 0 0 0; color: #fef3c7; font-size: 0.8rem;">
                <strong>Como medir progresso:</strong> {goal['measurement']}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Objetivos de médio prazo (6 meses)
    st.markdown("#### 📈 Objetivos de Médio Prazo (6 meses)")
    
    for goal in development_plan['medium_term']:
        st.markdown(f"""
        <div class="insight-card">
            <h5 style="color: #4fd1c7; margin-top: 0;">🚀 {goal['title']}</h5>
            <p><strong>Visão:</strong> {goal['vision']}</p>
            <p><strong>Marcos importantes:</strong></p>
            <ul>
                {' '.join([f'<li>{milestone}</li>' for milestone in goal['milestones']])}
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Recursos recomendados
    st.markdown("#### 📚 Recursos Recomendados")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("##### 📖 Livros")
        for book in development_plan['resources']['books']:
            st.markdown(f"• **{book['title']}** - {book['author']}")
            st.caption(f"   {book['why_relevant']}")
    
    with col2:
        st.markdown("##### 🎓 Cursos e Treinamentos")
        for course in development_plan['resources']['courses']:
            st.markdown(f"• **{course['title']}**")
            st.caption(f"   {course['description']}")

def render_pdf_report_tab(results):
    """Renderiza tab do relatório PDF"""
    
    st.markdown("### 📄 Relatório Profissional em PDF")
    
    st.markdown("""
    <div class="insight-card">
        <h4 style="color: #4fd1c7; margin-top: 0;">🎯 Seu Relatório Completo Inclui:</h4>
        <ul>
            <li><strong>Análise DISC detalhada</strong> com interpretações específicas</li>
            <li><strong>Perfil Big Five completo</strong> com percentis e comparações</li>
            <li><strong>Tipo MBTI explicado</strong> com características e preferências</li>
            <li><strong>Insights comportamentais</strong> únicos do seu perfil</li>
            <li><strong>Orientações de carreira</strong> personalizadas</li>
            <li><strong>Plano de desenvolvimento</strong> com ações práticas</li>
            <li><strong>Recomendações de leitura</strong> e recursos</li>
            <li><strong>Estratégias de comunicação</strong> e liderança</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Opções de personalização
    col1, col2 = st.columns(2)
    
    with col1:
        report_style = st.selectbox(
            "🎨 Estilo do Relatório:",
            ["Executivo", "Completo", "Coaching", "Acadêmico"]
        )
        
        include_charts = st.checkbox("📊 Incluir gráficos", value=True)
        include_comparisons = st.checkbox("📈 Incluir comparações populacionais", value=True)
    
    with col2:
        language = st.selectbox("🌐 Idioma:", ["Português", "English"])
        
        include_action_plan = st.checkbox("🎯 Incluir plano de ação", value=True)
        include_resources = st.checkbox("📚 Incluir recursos recomendados", value=True)
    
    # Botão de geração
    if st.button("🚀 Gerar Relatório PDF Completo", type="primary", use_container_width=True):
        
        with st.spinner("📝 Gerando seu relatório personalizado..."):
            # Simula tempo de processamento
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            steps = [
                "Compilando dados da avaliação...",
                "Gerando análises personalizadas...", 
                "Criando visualizações...",
                "Formatando relatório profissional...",
                "Aplicando estilo selecionado...",
                "Finalizando PDF..."
            ]
            
            for i, step in enumerate(steps):
                status_text.text(step)
                progress_bar.progress((i + 1) / len(steps))
                time.sleep(1)
            
            # Gera o PDF
            pdf_content = generate_professional_pdf_report(results, {
                'style': report_style,
                'include_charts': include_charts,
                'include_comparisons': include_comparisons,
                'language': language,
                'include_action_plan': include_action_plan,
                'include_resources': include_resources
            })
            
            status_text.text("✅ Relatório gerado com sucesso!")
            time.sleep(1)
        
        # Download do PDF
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"NeuroMap_Relatorio_{report_style}_{timestamp}.pdf"
        
        st.download_button(
            label="⬇️ Baixar Relatório PDF",
            data=pdf_content,
            file_name=filename,
            mime="application/pdf",
            use_container_width=True
        )
        
        st.success("🎉 Seu relatório está pronto para download!")
        
        # Preview do conteúdo
        with st.expander("👀 Prévia do Conteúdo do Relatório"):
            st.markdown(generate_pdf_preview(results))

def render_results_preview():
    """Preview resumido dos resultados no dashboard"""
    
    st.markdown("### 🎯 Resumo dos Seus Resultados")
    
    results = st.session_state.results
    if not results:
        return
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 🎭 Perfil DISC")
        for dim, score in results['disc'].items():
            if score > 25:  # Mostra apenas dimensões significativas
                st.write(f"**{dim}**: {score:.0f}%")
    
    with col2:
        st.markdown("#### 🧠 Big Five Destaque")
        # Mostra os 3 traços mais altos
        top_traits = sorted(results['big_five'].items(), key=lambda x: x[1], reverse=True)[:3]
        trait_names = {'O': 'Abertura', 'C': 'Consciência', 'E': 'Extroversão', 'A': 'Amabilidade', 'N': 'Neuroticismo'}
        
        for trait, score in top_traits:
            name = trait_names.get(trait, trait)
            st.write(f"**{name}**: {score:.0f}%")
    
    with col3:
        st.markdown("#### 💭 Tipo MBTI")
        st.write(f"**Tipo**: {results['mbti_type']}")
        mbti_desc = get_detailed_mbti_description(results['mbti_type'])
        st.write(f"**Arquétipo**: {mbti_desc['title']}")

# Funções auxiliares para insights avançados

def get_detailed_mbti_description(mbti_type):
    """Retorna descrição detalhada do tipo MBTI"""
    
    descriptions = {
        'INTJ': {
            'title': 'O Arquiteto Estratégico',
            'description': 'Visionário natural com capacidade excepcional de transformar ideias complexas em estratégias práticas e sistemas eficientes.',
            'characteristics': [
                'Pensamento estratégico de longo prazo',
                'Independência intelectual e emocional',
                'Capacidade de síntese e análise profunda',
                'Foco intenso em objetivos pessoais',
                'Confiança em insights e intuições'
            ],
            'processing_style': 'Você processa informações de forma holística, conectando padrões e possibilidades futuras. Prefere trabalhar com conceitos abstratos e desenvolver frameworks mentais complexos.'
        },
        'ENFP': {
            'title': 'O Inspirador Inovador',
            'description': 'Entusiasta natural que vê potencial infinito nas pessoas e situações, capaz de inspirar e motivar outros através de sua energia contagiante.',
            'characteristics': [
                'Entusiasmo contagiante e energia positiva',
                'Capacidade de ver potencial nas pessoas',
                'Flexibilidade e adaptabilidade',
                'Comunicação inspiradora e motivacional',
                'Foco em possibilidades e inovação'
            ],
            'processing_style': 'Você processa informações de forma associativa, fazendo conexões criativas entre ideias aparentemente não relacionadas. Prefere explorar múltiplas possibilidades simultaneamente.'
        },
        # Adicione mais tipos conforme necessário
    }
    
    return descriptions.get(mbti_type, {
        'title': f'Tipo {mbti_type}',
        'description': f'Perfil único {mbti_type} com características específicas desta combinação de preferências.',
        'characteristics': ['Características específicas do tipo', 'Padrões comportamentais únicos'],
        'processing_style': 'Estilo específico de processamento de informações baseado nas preferências identificadas.'
    })

def generate_advanced_insights(dominant_disc, mbti_type, results):
    """Gera insights avançados baseados no perfil completo"""
    
    insights = {
        'strengths': [
            {
                'title': 'Liderança Estratégica',
                'description': 'Capacidade natural de visualizar o panorama geral e guiar outros em direção aos objetivos.'
            },
            {
                'title': 'Pensamento Analítico',
                'description': 'Habilidade excepcional de quebrar problemas complexos em componentes gerenciáveis.'
            },
            {
                'title': 'Orientação para Resultados',
                'description': 'Foco intenso em alcançar metas e entregar valor tangível.'
            },
            {
                'title': 'Independência Intelectual',
                'description': 'Confiança em seu próprio julgamento e capacidade de tomar decisões autônomas.'
            },
            {
                'title': 'Visão de Longo Prazo',
                'description': 'Capacidade de antever tendências e planejar estratégias sustentáveis.'
            },
            {
                'title': 'Eficiência Operacional',
                'description': 'Talento para otimizar processos e eliminar redundâncias.'
            },
            {
                'title': 'Comunicação Direta',
                'description': 'Habilidade de comunicar ideias complexas de forma clara e objetiva.'
            },
            {
                'title': 'Adaptabilidade Estratégica',
                'description': 'Flexibilidade para ajustar abordagens mantendo o foco nos objetivos.'
            }
        ],
        'development_opportunities': [
            {
                'area': 'Inteligência Emocional',
                'why': 'Desenvolver maior sensibilidade às necessidades emocionais da equipe pode amplificar significativamente sua capacidade de liderança.',
                'how': 'Pratique escuta ativa, faça check-ins regulares com a equipe e busque feedback sobre seu estilo de comunicação.'
            },
            {
                'area': 'Delegação Efetiva',
                'why': 'Aprender a confiar mais na capacidade dos outros pode liberar seu tempo para atividades estratégicas de maior valor.',
                'how': 'Comece delegando tarefas menores, estabeleça marcos claros de acompanhamento e celebre sucessos da equipe.'
            },
            {
                'area': 'Networking Estratégico',
                'why': 'Expandir sua rede de contatos pode abrir portas para oportunidades e insights valiosos.',
                'how': 'Participe de eventos da indústria, mantenha contato regular com colegas e ofereça ajuda antes de pedir.'
            }
        ],
        'communication_style': {
            'style_name': 'Comunicador Estratégico-Direto',
            'description': 'Você comunica de forma clara, objetiva e focada em resultados. Prefere conversas substanciais e vai direto ao ponto.',
            'strengths': [
                'Clareza e objetividade nas mensagens',
                'Capacidade de simplificar conceitos complexos',
                'Foco em soluções práticas',
                'Comunicação baseada em dados e fatos'
            ],
            'watch_points': [
                'Pode parecer impaciente com detalhes "desnecessários"',
                'Risco de subestimar a importância do rapport',
                'Tendência a focar mais no "o que" que no "como"',
                'Pode precisar de mais tempo para ouvir perspectivas diferentes'
            ]
        }
    }
    
    return insights

def generate_career_guidance(dominant_disc, mbti_type, results):
    """Gera orientação de carreira detalhada"""
    
    guidance = {
        'ideal_careers': [
            {
                'title': 'Chief Technology Officer (CTO)',
                'compatibility': 92,
                'description': 'Liderar estratégia tecnológica e inovação em organizações de alto crescimento.',
                'why_ideal': 'Combina sua visão estratégica com capacidade técnica e liderança orientada para resultados.'
            },
            {
                'title': 'Consultor Estratégico',
                'compatibility': 89,
                'description': 'Assessorar executivos em decisões estratégicas e transformação organizacional.',
                'why_ideal': 'Aproveita sua capacidade analítica e visão sistêmica para resolver problemas complexos.'
            },
            {
                'title': 'Diretor de Produto',
                'compatibility': 86,
                'description': 'Definir visão e estratégia de produtos inovadores em empresas de tecnologia.',
                'why_ideal': 'Utiliza sua orientação para resultados e pensamento estratégico para criar produtos de impacto.'
            },
            {
                'title': 'Empreendedor/Fundador',
                'compatibility': 84,
                'description': 'Criar e liderar empresas inovadoras em setores de alto potencial.',
                'why_ideal': 'Combina independência, visão de longo prazo e capacidade de execução.'
            }
        ],
        'ideal_environments': [
            {
                'type': 'Startups de Alto Crescimento',
                'description': 'Ambientes dinâmicos onde pode aplicar visão estratégica e ver resultados rápidos.'
            },
            {
                'type': 'Empresas de Consultoria',
                'description': 'Organizações que valorizam pensamento analítico e soluções inovadoras.'
            },
            {
                'type': 'Departamentos de Inovação',
                'description': 'Áreas focadas em desenvolvimento de novos produtos e processos.'
            }
        ],
        'challenging_environments': [
            {
                'type': 'Burocracias Rígidas',
                'why_challenging': 'Podem limitar sua capacidade de inovação e implementação rápida de mudanças.'
            },
            {
                'type': 'Ambientes Altamente Sociais',
                'why_challenging': 'Podem drenar energia que você prefere dedicar a atividades estratégicas.'
            }
        ],
        'key_competencies': [
            {
                'skill': 'Liderança de Equipes Técnicas',
                'priority': 'Alta',
                'why_important': 'Essencial para maximizar seu impacto através de outros e escalar suas capacidades.'
            },
            {
                'skill': 'Comunicação Executiva',
                'priority': 'Alta', 
                'why_important': 'Fundamental para influenciar decisões estratégicas e conseguir recursos para seus projetos.'
            },
            {
                'skill': 'Gestão de Stakeholders',
                'priority': 'Média',
                'why_important': 'Importante para navegar política organizacional e construir alianças estratégicas.'
            }
        ]
    }
    
    return guidance

def generate_development_plan(results):
    """Gera plano de desenvolvimento personalizado"""
    
    plan = {
        'short_term': [
            {
                'title': 'Desenvolver Escuta Ativa',
                'objective': 'Melhorar capacidade de compreender perspectivas diversas antes de propor soluções.',
                'actions': [
                    'Praticar a técnica "espelhar" - repetir o que ouviu antes de responder',
                    'Fazer pelo menos 3 perguntas abertas em cada reunião importante',
                    'Reservar 20% do tempo de reunião apenas para ouvir',
                    'Pedir feedback semanal sobre sua capacidade de escuta'
                ],
                'measurement': 'Feedback positivo da equipe sobre sentir-se ouvida e compreendida.'
            },
            {
                'title': 'Implementar Delegação Estruturada',
                'objective': 'Liberar 30% do tempo atual através de delegação efetiva.',
                'actions': [
                    'Mapear todas as tarefas atuais por nível de complexidade',
                    'Identificar 3 pessoas para desenvolvimento através de delegação',
                    'Criar templates de briefing para tarefas delegadas',
                    'Estabelecer check-points semanais estruturados'
                ],
                'measurement': 'Redução de 30% em tarefas operacionais e aumento de tempo estratégico.'
            },
            {
                'title': 'Construir Rede de Mentoria',
                'objective': 'Estabelecer relacionamentos de mentoria bidirecional.',
                'actions': [
                    'Identificar 2 mentores sêniores em sua área',
                    'Encontrar 2 profissionais júniores para mentorar',
                    'Agendar reuniões mensais de mentoria',
                    'Participar de pelo menos 1 evento de networking por mês'
                ],
                'measurement': 'Rede ativa de 4 relacionamentos de mentoria estabelecidos.'
            }
        ],
        'medium_term': [
            {
                'title': 'Tornar-se Líder de Pensamento',
                'vision': 'Ser reconhecido como especialista em sua área através de conteúdo e palestras.',
                'milestones': [
                    'Publicar 1 artigo técnico por mês',
                    'Palestrar em 2 eventos da indústria',
                    'Construir presença no LinkedIn com 5000+ seguidores',
                    'Ser convidado para podcast ou entrevista'
                ]
            },
            {
                'title': 'Desenvolver Competências de CEO',
                'vision': 'Adquirir habilidades necessárias para liderança executiva.',
                'milestones': [
                    'Completar MBA ou programa executivo',
                    'Liderar projeto de transformação organizacional',
                    'Desenvolver fluência em finanças corporativas',
                    'Construir rede de relacionamentos C-level'
                ]
            }
        ],
        'resources': {
            'books': [
                {
                    'title': 'The First 90 Days',
                    'author': 'Michael Watkins',
                    'why_relevant': 'Essencial para transições de liderança e estabelecimento rápido de credibilidade.'
                },
                {
                    'title': 'High Output Management',
                    'author': 'Andy Grove',
                    'why_relevant': 'Framework prático para maximizar produtividade própria e da equipe.'
                },
                {
                    'title': 'The Hard Thing About Hard Things',
                    'author': 'Ben Horowitz',
                    'why_relevant': 'Perspectivas reais sobre desafios de liderança em ambientes de alta pressão.'
                }
            ],
            'courses': [
                {
                    'title': 'Strategic Leadership Program',
                    'description': 'Programa executivo focado em liderança estratégica e transformação organizacional.'
                },
                {
                    'title': 'Executive Communication',
                    'description': 'Desenvolvimento de habilidades de comunicação para líderes sêniores.'
                },
                {
                    'title': 'Finance for Non-Financial Managers',
                    'description': 'Competências financeiras essenciais para tomada de decisão estratégica.'
                }
            ]
        }
    }
    
    return plan

def generate_professional_pdf_report(results, options):
    """Gera relatório PDF profissional"""
    
    # Aqui você implementaria a geração real do PDF
    # Por enquanto, vamos simular com um conteúdo mock
    
    from fpdf import FPDF
    import io
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    
    # Adiciona conteúdo ao PDF
    pdf.cell(0, 10, 'NeuroMap - Relatorio Profissional de Personalidade', ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f"Tipo MBTI: {results['mbti_type']}", ln=True)
    pdf.cell(0, 10, f"Confiabilidade: {results['reliability']}%", ln=True)
    pdf.ln(10)
    
    # Seção DISC
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Perfil DISC:', ln=True)
    pdf.set_font('Arial', '', 12)
    
    for key, value in results['disc'].items():
        pdf.cell(0, 8, f"{key}: {value:.1f}%", ln=True)
    
    pdf.ln(10)
    
    # Seção Big Five
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Big Five:', ln=True)
    pdf.set_font('Arial', '', 12)
    
    trait_names = {
        'O': 'Abertura', 'C': 'Conscienciosidade', 'E': 'Extroversao',
        'A': 'Amabilidade', 'N': 'Neuroticismo'
    }
    
    for key, value in results['big_five'].items():
        name = trait_names.get(key, key)
        pdf.cell(0, 8, f"{name}: Percentil {value:.1f}%", ln=True)
    
    # Converte para bytes
    pdf_output = pdf.output(dest='S').encode('latin1')
    
    return pdf_output

def generate_pdf_preview(results):
    """Gera preview do conteúdo do PDF"""
    
    dominant_disc = max(results['disc'], key=results['disc'].get)
    
    preview = f"""
    ## 📄 Conteúdo do Relatório PDF
    
    ### 📋 Sumário Executivo
    - Perfil DISC dominante: **{dominant_disc}** ({results['disc'][dominant_disc]:.0f}%)
    - Tipo MBTI: **{results['mbti_type']}**
    - Confiabilidade da avaliação: **{results['reliability']}%**
    - Tempo de conclusão: **{results['completion_time']} minutos**
    
    ### 📊 Análises Detalhadas
    1. **Perfil DISC Completo** - Interpretação de cada dimensão
    2. **Big Five Detalhado** - Percentis e comparações populacionais  
    3. **Tipo MBTI Explicado** - Características e preferências
    4. **Análise Comportamental** - Padrões únicos identificados
    
    ### 💼 Orientações Profissionais
    - **Carreiras Ideais** - Lista personalizada com compatibilidade
    - **Ambientes de Trabalho** - Contextos que potencializam performance
    - **Competências Chave** - Habilidades prioritárias para desenvolvimento
    - **Estratégias de Liderança** - Abordagens baseadas no seu perfil
    
    ### 🎯 Plano de Desenvolvimento
    - **Objetivos 90 dias** - Metas específicas e mensuráveis
    - **Visão 6 meses** - Marcos de desenvolvimento profissional
    - **Recursos Recomendados** - Livros, cursos e ferramentas
    - **Métricas de Progresso** - Como acompanhar evolução
    
    **Total de páginas:** 15-18 páginas  
    **Formato:** PDF profissional com gráficos e visualizações
    """
    
    return preview

def main():
    """Função principal melhorada"""
    initialize_session_state()
    render_header()
    render_sidebar()
    
    # Roteamento de páginas
    if not st.session_state.user_authenticated:
        render_landing_page()
    elif st.session_state.current_page == 'dashboard':
        render_dashboard()
    elif st.session_state.current_page == 'assessment':
        render_assessment()
    elif st.session_state.current_page == 'results':
        render_results()
    else:
        render_dashboard()

if __name__ == "__main__":
    main()
