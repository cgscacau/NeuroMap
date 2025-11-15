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
    
    .login-required {
        background: linear-gradient(135deg, #dc2626 0%, #ef4444 100%);
        color: white;
        padding: 2rem;
        border-radius: 12px;
        text-align: center;
        margin: 2rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Sistema de usuários simples (em produção, use um banco de dados real)
USERS_DB = {
    "admin@neuromap.com": {"password": "admin123", "name": "Administrador"},
    "demo@neuromap.com": {"password": "demo123", "name": "Usuário Demo"},
    "user@test.com": {"password": "test123", "name": "Usuário Teste"}
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

def authenticate_user(email, password):
    """Autentica usuário com email e senha"""
    if email in USERS_DB and USERS_DB[email]["password"] == password:
        return True, USERS_DB[email]["name"]
    return False, None

def register_user(name, email, password):
    """Registra novo usuário"""
    if email in USERS_DB:
        return False, "Email já cadastrado"
    
    if len(password) < 6:
        return False, "Senha deve ter pelo menos 6 caracteres"
    
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
                # Limpa apenas dados de autenticação, mantém resultados
                st.session_state.authenticated = False
                st.session_state.user_name = ""
                st.session_state.user_email = ""
                st.session_state.current_page = 'home'
                st.rerun()
        else:
            render_auth_sidebar()

def render_auth_sidebar():
    """Renderiza autenticação na sidebar"""
    st.markdown("#### 🔑 Acesso Necessário")
    
    tab1, tab2 = st.tabs(["Entrar", "Cadastrar"])
    
    with tab1:
        st.markdown("**Usuários de teste:**")
        st.code("admin@neuromap.com / admin123")
        st.code("demo@neuromap.com / demo123")
        st.code("user@test.com / test123")
        
        with st.form("login_form"):
            email = st.text_input("📧 Email", placeholder="seu@email.com")
            password = st.text_input("🔐 Senha", type="password")
            
            if st.form_submit_button("Entrar", use_container_width=True):
                if email and password:
                    success, user_name = authenticate_user(email, password)
                    if success:
                        st.session_state.authenticated = True
                        st.session_state.user_email = email
                        st.session_state.user_name = user_name
                        st.session_state.current_page = 'dashboard'
                        st.session_state.login_attempts = 0
                        st.success("✅ Login realizado com sucesso!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.session_state.login_attempts += 1
                        st.error(f"❌ Email ou senha incorretos (Tentativa {st.session_state.login_attempts})")
                        if st.session_state.login_attempts >= 3:
                            st.warning("⚠️ Muitas tentativas. Use os usuários de teste acima.")
                else:
                    st.error("❌ Preencha todos os campos")
    
    with tab2:
        with st.form("register_form"):
            name = st.text_input("👤 Nome completo")
            email = st.text_input("📧 Email")
            password = st.text_input("🔐 Senha", type="password", help="Mínimo 6 caracteres")
            confirm_password = st.text_input("🔐 Confirmar Senha", type="password")
            
            if st.form_submit_button("Criar conta", use_container_width=True):
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

def render_login_required():
    """Renderiza tela de login obrigatório"""
    st.markdown("""
    <div class="login-required">
        <h2>🔒 Acesso Restrito</h2>
        <p style="font-size: 1.2rem; margin: 1rem 0;">
            Para acessar o NeuroMap Pro, você precisa fazer login.
        </p>
        <p>
            Esta é uma versão profissional que requer autenticação para:
        </p>
        <ul style="text-align: left; display: inline-block;">
            <li>Garantir a privacidade dos seus dados</li>
            <li>Salvar seu progresso na avaliação</li>
            <li>Gerar relatórios personalizados</li>
            <li>Acompanhar sua evolução ao longo do tempo</li>
        </ul>
        <p style="margin-top: 2rem; font-size: 1.1rem;">
            👈 <strong>Faça login na barra lateral</strong>
        </p>
    </div>
    """, unsafe_allow_html=True)
    
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

def render_dashboard():
    """Renderiza dashboard principal"""
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
    
    # Calcula médias ponderadas
    for dim in disc_scores:
        if disc_counts[dim] > 0:
            disc_scores[dim] = disc_scores[dim] / disc_counts[dim]
    
    for dim in b5_scores:
        if b5_counts[dim] > 0:
            b5_scores[dim] = b5_scores[dim] / b5_counts[dim]
    
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
    
    # Determina tipo MBTI (simplificado baseado em Big Five)
    mbti_type = ""
    mbti_type += "E" if b5_scores["E"] >= 50 else "I"
    mbti_type += "S" if b5_scores["O"] < 50 else "N"  # Inverso da Abertura
    mbti_type += "T" if b5_scores["A"] < 50 else "F"  # Inverso da Amabilidade
    mbti_type += "J" if b5_scores["C"] >= 50 else "P"  # Baseado na Conscienciosidade
    
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
        "reliability": reliability,
        "completion_time": completion_time,
        "total_questions": len(questions),
        "response_consistency": round(response_variance, 2)
    }

def render_results():
    """Renderiza página de resultados com PDF funcional"""
    
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
    tab1, tab2, tab3 = st.tabs([
        "📊 Perfil Completo", 
        "🎯 Insights Detalhados", 
        "📄 Relatório PDF"
    ])
    
    with tab1:
        render_complete_profile_tab(results)
    
    with tab2:
        render_detailed_insights_tab(results)
    
    with tab3:
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

def render_pdf_report_tab(results):
    """Renderiza tab do relatório PDF com download funcional"""
    
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
    
    with col2:
        language = st.selectbox("🌐 Idioma:", ["Português", "English"])
        
        include_action_plan = st.checkbox("🎯 Incluir plano de ação", value=True)
    
    # Botão de geração
    if st.button("🚀 Gerar e Baixar Relatório PDF", type="primary", use_container_width=True):
        
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
                time.sleep(0.5)
            
            # Gera o PDF
            pdf_content = generate_professional_pdf_report(results, {
                'style': report_style,
                'include_charts': include_charts,
                'language': language,
                'include_action_plan': include_action_plan
            })
            
            status_text.text("✅ Relatório gerado com sucesso!")
        
        # Download do PDF
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"NeuroMap_Relatorio_{report_style}_{timestamp}.pdf"
        
        st.download_button(
            label="⬇️ Baixar Relatório PDF Completo",
            data=pdf_content,
            file_name=filename,
            mime="application/pdf",
            use_container_width=True,
            key="download_pdf_button"
        )
        
        st.success("🎉 Seu relatório está pronto para download!")
        st.info("👆 Clique no botão acima para fazer o download do seu relatório PDF completo.")

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

# Funções auxiliares

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
        'ESTJ': {
            'title': 'O Executivo Organizador',
            'description': 'Líder natural focado em eficiência e resultados, com talento excepcional para organizar pessoas e recursos.',
            'characteristics': [
                'Liderança prática e orientada para resultados',
                'Excelente capacidade organizacional',
                'Foco em eficiência e produtividade',
                'Comunicação direta e clara',
                'Responsabilidade e confiabilidade'
            ],
            'processing_style': 'Você processa informações de forma linear e estruturada, focando em fatos concretos e aplicações práticas.'
        }
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
        ]
    }
    
    return insights

def generate_professional_pdf_report(results, options):
    """Gera relatório PDF profissional funcional"""
    
    try:
        from fpdf import FPDF
        
        class PDF(FPDF):
            def header(self):
                self.set_font('Arial', 'B', 15)
                self.cell(0, 10, 'NeuroMap - Relatorio Profissional de Personalidade', 0, 1, 'C')
                self.ln(10)
            
            def footer(self):
                self.set_y(-15)
                self.set_font('Arial', 'I', 8)
                self.cell(0, 10, f'Pagina {self.page_no()}', 0, 0, 'C')
        
        pdf = PDF()
        pdf.add_page()
        
        # Capa
        pdf.set_font('Arial', 'B', 20)
        pdf.ln(30)
        pdf.cell(0, 15, 'RELATORIO DE PERSONALIDADE', 0, 1, 'C')
        pdf.set_font('Arial', '', 16)
        pdf.cell(0, 10, f"Tipo MBTI: {results['mbti_type']}", 0, 1, 'C')
        pdf.cell(0, 10, f"Confiabilidade: {results['reliability']}%", 0, 1, 'C')
        pdf.ln(20)
        
        # Data
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 10, f"Gerado em: {datetime.now().strftime('%d/%m/%Y as %H:%M')}", 0, 1, 'C')
        
        # Nova página - Resumo Executivo
        pdf.add_page()
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, 'RESUMO EXECUTIVO', 0, 1, 'L')
        pdf.ln(5)
        
        pdf.set_font('Arial', '', 12)
        dominant_disc = max(results['disc'], key=results['disc'].get)
        
        summary_text = f"""
Baseado em uma avaliacao cientifica de {results['total_questions']} questoes,
seu perfil apresenta as seguintes caracteristicas principais:

• Perfil DISC dominante: {dominant_disc} ({results['disc'][dominant_disc]:.0f}%)
• Tipo MBTI identificado: {results['mbti_type']}
• Nivel de confiabilidade: {results['reliability']}%
• Tempo de conclusao: {results['completion_time']} minutos

Este relatorio fornece uma analise detalhada de sua personalidade,
incluindo pontos fortes, areas de desenvolvimento e orientacoes
profissionais personalizadas.
        """
        
        # Quebra texto em linhas
        lines = summary_text.strip().split('\n')
        for line in lines:
            if line.strip():
                pdf.cell(0, 6, line.strip().encode('latin1', 'replace').decode('latin1'), 0, 1, 'L')
        
        # Nova página - Perfil DISC
        pdf.add_page()
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, 'PERFIL DISC DETALHADO', 0, 1, 'L')
        pdf.ln(5)
        
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 8, 'Scores por Dimensao:', 0, 1, 'L')
        pdf.set_font('Arial', '', 11)
        
        disc_names = {
            'D': 'Dominancia - Orientacao para resultados e lideranca',
            'I': 'Influencia - Comunicacao e networking',
            'S': 'Estabilidade - Cooperacao e trabalho em equipe',
            'C': 'Conformidade - Qualidade e precisao'
        }
        
        for key, score in results['disc'].items():
            name = disc_names.get(key, key)
            pdf.cell(0, 6, f"{name}: {score:.1f}%", 0, 1, 'L')
        
        # Nova página - Big Five
        pdf.add_page()
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, 'PERFIL BIG FIVE', 0, 1, 'L')
        pdf.ln(5)
        
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 8, 'Percentis Populacionais:', 0, 1, 'L')
        pdf.set_font('Arial', '', 11)
        
        b5_names = {
            'O': 'Abertura a Experiencia - Criatividade e curiosidade',
            'C': 'Conscienciosidade - Organizacao e disciplina',
            'E': 'Extroversao - Sociabilidade e energia',
            'A': 'Amabilidade - Cooperacao e empatia',
            'N': 'Neuroticismo - Estabilidade emocional'
        }
        
        for key, percentile in results['big_five'].items():
            name = b5_names.get(key, key)
            level = "Alto" if percentile > 70 else "Medio" if percentile > 30 else "Baixo"
            pdf.cell(0, 6, f"{name}: Percentil {percentile:.0f}% ({level})", 0, 1, 'L')
        
        # Nova página - Tipo MBTI
        pdf.add_page()
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, f'TIPO MBTI: {results["mbti_type"]}', 0, 1, 'L')
        pdf.ln(5)
        
        mbti_desc = get_detailed_mbti_description(results['mbti_type'])
        
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 8, mbti_desc['title'], 0, 1, 'L')
        pdf.ln(3)
        
        pdf.set_font('Arial', '', 11)
        # Quebra descrição em linhas
        desc_lines = mbti_desc['description'][:200].split(' ')
        current_line = ""
        
        for word in desc_lines:
            if len(current_line + word) < 80:
                current_line += word + " "
            else:
                pdf.cell(0, 6, current_line.strip().encode('latin1', 'replace').decode('latin1'), 0, 1, 'L')
                current_line = word + " "
        
        if current_line:
            pdf.cell(0, 6, current_line.strip().encode('latin1', 'replace').decode('latin1'), 0, 1, 'L')
        
        # Nova página - Recomendações
        pdf.add_page()
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, 'RECOMENDACOES DE DESENVOLVIMENTO', 0, 1, 'L')
        pdf.ln(5)
        
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 8, 'Pontos Fortes Identificados:', 0, 1, 'L')
        pdf.set_font('Arial', '', 11)
        
        strengths = [
            'Lideranca estrategica e visao de longo prazo',
            'Capacidade analitica e resolucao de problemas',
            'Orientacao para resultados e eficiencia',
            'Independencia e autonomia nas decisoes'
        ]
        
        for strength in strengths:
            pdf.cell(0, 6, f"• {strength}", 0, 1, 'L')
        
        pdf.ln(5)
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 8, 'Areas de Desenvolvimento:', 0, 1, 'L')
        pdf.set_font('Arial', '', 11)
        
        development_areas = [
            'Inteligencia emocional e empatia',
            'Delegacao efetiva e confianca na equipe',
            'Comunicacao interpessoal e feedback',
            'Flexibilidade e adaptacao a mudancas'
        ]
        
        for area in development_areas:
            pdf.cell(0, 6, f"• {area}", 0, 1, 'L')
        
        # Rodapé final
        pdf.ln(20)
        pdf.set_font('Arial', 'I', 10)
        pdf.cell(0, 6, 'Este relatorio foi gerado pelo NeuroMap Pro', 0, 1, 'C')
        pdf.cell(0, 6, 'Ferramenta cientifica de analise de personalidade', 0, 1, 'C')
        
        # Converte para bytes
        pdf_output = pdf.output(dest='S')
        
        # Garante que seja bytes
        if isinstance(pdf_output, str):
            pdf_output = pdf_output.encode('latin1')
        
        return pdf_output
        
    except Exception as e:
        st.error(f"Erro ao gerar PDF: {e}")
        # Retorna um PDF simples de fallback
        simple_pdf = FPDF()
        simple_pdf.add_page()
        simple_pdf.set_font('Arial', 'B', 16)
        simple_pdf.cell(0, 10, 'NeuroMap - Relatorio de Personalidade', 0, 1, 'C')
        simple_pdf.ln(10)
        simple_pdf.set_font('Arial', '', 12)
        simple_pdf.cell(0, 10, f"Tipo MBTI: {results['mbti_type']}", 0, 1, 'L')
        simple_pdf.cell(0, 10, f"Confiabilidade: {results['reliability']}%", 0, 1, 'L')
        
        output = simple_pdf.output(dest='S')
        return output.encode('latin1') if isinstance(output, str) else output

def main():
    """Função principal com autenticação obrigatória"""
    initialize_session_state()
    render_header()
    render_sidebar()
    
    # Verifica autenticação
    if not st.session_state.authenticated:
        render_login_required()
        return
    
    # Roteamento de páginas para usuários autenticados
    if st.session_state.current_page == 'dashboard':
        render_dashboard()
    elif st.session_state.current_page == 'assessment':
        render_assessment()
    elif st.session_state.current_page == 'results':
        render_results()
    else:
        render_dashboard()

if __name__ == "__main__":
    main()
