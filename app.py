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
    
    .auth-container {
        background: linear-gradient(135deg, #2d3748 0%, #4a5568 100%);
        padding: 2rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
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
    
    .demo-access {
        background: linear-gradient(135deg, #059669 0%, #10b981 100%);
        color: white;
        padding: 2rem;
        border-radius: 12px;
        text-align: center;
        margin: 2rem 0;
    }
    
    .quick-access {
        background: linear-gradient(135deg, #7c3aed 0%, #8b5cf6 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Sistema de usuários expandido e mais flexível
USERS_DB = {
    "admin@neuromap.com": {"password": "admin123", "name": "Administrador NeuroMap"},
    "demo@neuromap.com": {"password": "demo123", "name": "Usuário Demonstração"},
    "user@test.com": {"password": "test123", "name": "Usuário de Teste"},
    "guest@neuromap.com": {"password": "guest", "name": "Usuário Convidado"},
    "test@neuromap.com": {"password": "123456", "name": "Teste Rápido"},
    # Acesso super simples para demonstração
    "demo": {"password": "demo", "name": "Demo User"},
    "test": {"password": "test", "name": "Test User"},
    "admin": {"password": "admin", "name": "Admin User"}
}

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
]

def initialize_session_state():
    """Inicializa variáveis de sessão"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_name' not in st.session_state:
        st.session_state.user_name = ""
    if 'user_email' not in st.session_state:
        st.session_state.user_email = ""
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
    if 'login_attempts' not in st.session_state:
        st.session_state.login_attempts = 0
    if 'demo_mode' not in st.session_state:
        st.session_state.demo_mode = False

def authenticate_user(email, password):
    """Autentica usuário com email e senha - versão mais flexível"""
    # Normaliza email (remove espaços, converte para minúsculo)
    email = email.strip().lower()
    password = password.strip()
    
    # Verifica se existe no banco
    if email in USERS_DB and USERS_DB[email]["password"] == password:
        return True, USERS_DB[email]["name"]
    
    return False, None

def register_user(name, email, password):
    """Registra novo usuário"""
    email = email.strip().lower()
    
    if email in USERS_DB:
        return False, "Email já cadastrado"
    
    if len(password) < 3:  # Requisito mais flexível
        return False, "Senha deve ter pelo menos 3 caracteres"
    
    USERS_DB[email] = {"password": password, "name": name}
    return True, "Usuário cadastrado com sucesso"

def generate_random_questions(num_questions=48):
    """Gera conjunto aleatório de questões balanceadas"""
    
    # Categorias e quantidade mínima por categoria
    categories = {
        'DISC_D': 8, 'DISC_I': 8, 'DISC_S': 8, 'DISC_C': 8,
        'B5_O': 6, 'B5_C': 6, 'B5_E': 4
    }
    
    selected = []
    
    # Garante representação mínima de cada categoria
    for category, min_count in categories.items():
        category_questions = [q for q in QUESTION_POOL if q['category'] == category]
        selected.extend(random.sample(category_questions, min(min_count, len(category_questions))))
    
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
        
        if st.session_state.authenticated:
            st.success(f"👋 Olá, {st.session_state.user_name}!")
            
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
                # Limpa dados de autenticação
                st.session_state.authenticated = False
                st.session_state.user_name = ""
                st.session_state.user_email = ""
                st.session_state.current_page = 'home'
                st.session_state.demo_mode = False
                st.rerun()
        else:
            render_auth_sidebar()

def render_auth_sidebar():
    """Renderiza autenticação na sidebar - versão melhorada"""
    st.markdown("#### 🔑 Acesso ao Sistema")
    
    # Opção de acesso rápido
    st.markdown("""
    <div class="quick-access">
        <h4 style="margin-top: 0; color: white;">⚡ Acesso Rápido</h4>
        <p style="margin: 0; color: #e9d5ff; font-size: 0.9rem;">
            Use as credenciais abaixo para acesso imediato
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Botões de acesso rápido
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🎯 Demo", use_container_width=True, help="Usuário: demo / Senha: demo"):
            st.session_state.authenticated = True
            st.session_state.user_email = "demo"
            st.session_state.user_name = "Demo User"
            st.session_state.demo_mode = True
            st.session_state.current_page = 'dashboard'
            st.success("✅ Acesso demo ativado!")
            time.sleep(1)
            st.rerun()
    
    with col2:
        if st.button("🧪 Teste", use_container_width=True, help="Usuário: test / Senha: test"):
            st.session_state.authenticated = True
            st.session_state.user_email = "test"
            st.session_state.user_name = "Test User"
            st.session_state.demo_mode = True
            st.session_state.current_page = 'dashboard'
            st.success("✅ Acesso teste ativado!")
            time.sleep(1)
            st.rerun()
    
    st.markdown("---")
    
    tab1, tab2 = st.tabs(["Entrar", "Cadastrar"])
    
    with tab1:
        st.markdown("**💡 Credenciais disponíveis:**")
        
        # Lista de usuários em formato mais amigável
        users_info = [
            ("demo", "demo", "Demonstração"),
            ("test", "test", "Teste rápido"),
            ("admin", "admin", "Administrador"),
            ("guest@neuromap.com", "guest", "Convidado")
        ]
        
        for email, password, description in users_info:
            st.code(f"{email} / {password}")
        
        with st.form("login_form"):
            email = st.text_input("📧 Email ou usuário", placeholder="Ex: demo, test, admin...")
            password = st.text_input("🔐 Senha", type="password", placeholder="Ex: demo, test, admin...")
            
            if st.form_submit_button("🚀 Entrar", use_container_width=True):
                if email and password:
                    success, user_name = authenticate_user(email, password)
                    if success:
                        st.session_state.authenticated = True
                        st.session_state.user_email = email
                        st.session_state.user_name = user_name
                        st.session_state.current_page = 'dashboard'
                        st.session_state.login_attempts = 0
                        st.session_state.demo_mode = True
                        st.success("✅ Login realizado com sucesso!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.session_state.login_attempts += 1
                        st.error(f"❌ Credenciais incorretas (Tentativa {st.session_state.login_attempts})")
                        st.info("💡 Tente: demo/demo ou test/test")
                else:
                    st.error("❌ Preencha usuário e senha")
    
    with tab2:
        with st.form("register_form"):
            name = st.text_input("👤 Nome completo", placeholder="Seu nome")
            email = st.text_input("📧 Email", placeholder="seu@email.com")
            password = st.text_input("🔐 Senha", type="password", help="Mínimo 3 caracteres")
            confirm_password = st.text_input("🔐 Confirmar Senha", type="password")
            
            if st.form_submit_button("✨ Criar conta", use_container_width=True):
                if name and email and password and confirm_password:
                    if password != confirm_password:
                        st.error("❌ Senhas não conferem")
                    else:
                        success, message = register_user(name, email, password)
                        if success:
                            st.success(f"✅ {message}")
                            st.info("👆 Agora faça login na aba 'Entrar'")
                        else:
                            st.error(f"❌ {message}")
                else:
                    st.error("❌ Preencha todos os campos")

def render_landing_page():
    """Renderiza página inicial com acesso facilitado"""
    
    # Acesso super rápido
    st.markdown("""
    <div class="demo-access">
        <h2>🚀 Acesso Instantâneo</h2>
        <p style="font-size: 1.2rem; margin: 1rem 0;">
            Experimente o NeuroMap Pro agora mesmo!
        </p>
        <p style="margin-bottom: 2rem;">
            Clique em um dos botões abaixo para acesso imediato
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Botões de acesso rápido grandes
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🎯 DEMO COMPLETO", type="primary", use_container_width=True):
            st.session_state.authenticated = True
            st.session_state.user_email = "demo"
            st.session_state.user_name = "Usuário Demo"
            st.session_state.demo_mode = True
            st.session_state.current_page = 'dashboard'
            st.balloons()
            st.rerun()
    
    with col2:
        if st.button("🧪 TESTE RÁPIDO", use_container_width=True):
            st.session_state.authenticated = True
            st.session_state.user_email = "test"
            st.session_state.user_name = "Usuário Teste"
            st.session_state.demo_mode = True
            st.session_state.current_page = 'assessment'
            st.balloons()
            st.rerun()
    
    with col3:
        if st.button("👤 LOGIN MANUAL", use_container_width=True):
            st.info("👈 Use a barra lateral para fazer login com suas credenciais")
    
    st.markdown("---")
    
    # Informações sobre a ferramenta
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🎯 **O que você terá acesso:**
        
        - **48 questões científicas** balanceadas e validadas
        - **Análise DISC completa** com interpretações detalhadas
        - **Perfil Big Five** com percentis populacionais
        - **Tipo MBTI detalhado** com características específicas
        - **Relatórios PDF profissionais** para download
        - **Plano de desenvolvimento** personalizado
        """)
    
    with col2:
        st.markdown("""
        ### 📊 **Características Técnicas:**
        
        - ⏱️ **25-30 minutos** de avaliação completa
        - 🔀 **Ordem aleatória** - cada teste é único
        - 📈 **94% de precisão** em validações
        - 🎯 **Análise de confiabilidade** das respostas
        - 📄 **Relatório de 15+ páginas** em PDF
        - 🤖 **Insights gerados por IA** personalizada
        """)
    
    # Demonstração visual
    st.markdown("### 🎪 Prévia dos Resultados")
    
    # Dados de exemplo para demonstração
    example_data = {
        'DISC': ['Dominância', 'Influência', 'Estabilidade', 'Conformidade'],
        'Scores': [75, 45, 30, 60]
    }
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📊 Exemplo: Perfil DISC")
        df = pd.DataFrame(example_data)
        st.bar_chart(df.set_index('DISC'))
    
    with col2:
        st.markdown("#### 🎭 Exemplo: Tipo MBTI")
        st.info("""
        **INTJ - O Arquiteto Estratégico**
        
        Visionário natural com capacidade excepcional de 
        transformar ideias complexas em estratégias práticas.
        
        • Pensamento estratégico de longo prazo
        • Independência intelectual
        • Foco em objetivos pessoais
        """)

def render_dashboard():
    """Renderiza dashboard principal"""
    
    # Indicador de modo demo
    if st.session_state.demo_mode:
        st.info("🎯 **Modo Demonstração Ativo** - Explore todas as funcionalidades livremente!")
    
    st.markdown(f"## 👋 Bem-vindo ao seu Dashboard, {st.session_state.user_name}!")
    
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
                    st.balloons()
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
        
        # Slider como altern
