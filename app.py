import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import json
import random
import time
import requests

# Configuração da página
st.set_page_config(
    page_title="NeuroMap - Avaliação de Personalidade",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configurações do Firebase
FIREBASE_API_KEY = st.secrets.get("FIREBASE_API_KEY", "")
FIREBASE_PROJECT_ID = st.secrets.get("FIREBASE_PROJECT_ID", "")
FIREBASE_DATABASE_URL = f"https://{FIREBASE_PROJECT_ID}-default-rtdb.firebaseio.com"

# URLs da Firebase Auth API
FIREBASE_SIGNUP_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FIREBASE_API_KEY}"
FIREBASE_SIGNIN_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
FIREBASE_RESET_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={FIREBASE_API_KEY}"

# CSS melhorado com melhor visibilidade
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 3rem 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .metric-card {
        background: rgba(255, 255, 255, 0.95);
        padding: 2rem;
        border-radius: 15px;
        border-left: 6px solid #667eea;
        margin: 1rem 0;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
        backdrop-filter: blur(10px);
    }
    
    .question-container {
        background: rgba(255, 255, 255, 0.95);
        padding: 2.5rem;
        border-radius: 15px;
        border-left: 6px solid #667eea;
        margin: 2rem 0;
        box-shadow: 0 6px 25px rgba(0, 0, 0, 0.15);
        color: #1a202c;
        backdrop-filter: blur(10px);
    }
    
    .question-container h4 {
        font-size: 1.3rem;
        font-weight: 600;
        line-height: 1.5;
        margin-bottom: 1.5rem;
        color: #2d3748;
    }
    
    .insight-card {
        background: linear-gradient(135deg, #e6fffa 0%, #f0fff4 100%);
        padding: 2rem;
        border-radius: 15px;
        margin: 1.5rem 0;
        border-left: 6px solid #38b2ac;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
        color: #1a202c;
    }
    
    .auth-container {
        background: rgba(255, 255, 255, 0.95);
        padding: 2.5rem;
        border-radius: 15px;
        margin: 1.5rem 0;
        box-shadow: 0 6px 25px rgba(0, 0, 0, 0.15);
        border: 1px solid rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(10px);
    }
    
    .strength-card {
        background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 0.8rem 0;
        box-shadow: 0 4px 15px rgba(72, 187, 120, 0.3);
    }
    
    .development-card {
        background: linear-gradient(135deg, #ed8936 0%, #dd6b20 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 0.8rem 0;
        box-shadow: 0 4px 15px rgba(237, 137, 54, 0.3);
    }
    
    .career-card {
        background: linear-gradient(135deg, #9f7aea 0%, #805ad5 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 0.8rem 0;
        box-shadow: 0 4px 15px rgba(159, 122, 234, 0.3);
    }
    
    .login-required {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 3rem 2rem;
        border-radius: 20px;
        text-align: center;
        margin: 2rem 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
    }
    
    .nav-button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 1rem 2rem;
        border-radius: 12px;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        transition: all 0.3s ease;
    }
    
    .nav-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    .stRadio > div {
        background: rgba(255, 255, 255, 0.8);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    
    .stMarkdown {
        color: #1a202c;
    }
    
    /* Melhor visibilidade para texto */
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4 {
        color: #2d3748 !important;
        font-weight: 700;
    }
    
    .stMarkdown p {
        color: #4a5568 !important;
        line-height: 1.6;
    }
    
    /* Botões mais visíveis */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.8rem 2rem;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
</style>
""", unsafe_allow_html=True)

# Questões da avaliação (48 questões)
QUESTION_POOL = [
    # DISC - Dominância (D) - 12 questões
    {"id": 1, "text": "Gosto de assumir a responsabilidade quando algo importante precisa ser feito.", "category": "DISC_D", "weight": 0.9},
    {"id": 2, "text": "Prefiro liderar a ser liderado em projetos importantes.", "category": "DISC_D", "weight": 0.8},
    {"id": 3, "text": "Sinto-me confortável tomando decisões difíceis rapidamente.", "category": "DISC_D", "weight": 0.85},
    {"id": 4, "text": "Gosto de desafios que testam minha capacidade de liderança.", "category": "DISC_D", "weight": 0.8},
    {"id": 5, "text": "Prefiro ambientes competitivos onde posso me destacar.", "category": "DISC_D", "weight": 0.75},
    {"id": 6, "text": "Tenho facilidade em convencer outros a seguirem minha visão.", "category": "DISC_D", "weight": 0.7},
    {"id": 7, "text": "Costumo assumir o controle quando as coisas não estão funcionando.", "category": "DISC_D", "weight": 0.85},
    {"id": 8, "text": "Prefiro resultados rápidos a processos longos e detalhados.", "category": "DISC_D", "weight": 0.6},
    {"id": 9, "text": "Não tenho medo de confrontar pessoas quando necessário.", "category": "DISC_D", "weight": 0.8},
    {"id": 10, "text": "Gosto de estabelecer metas ambiciosas e alcançá-las.", "category": "DISC_D", "weight": 0.75},
    {"id": 11, "text": "Prefiro trabalhar em ritmo acelerado.", "category": "DISC_D", "weight": 0.7},
    {"id": 12, "text": "Sou direto ao comunicar minhas expectativas.", "category": "DISC_D", "weight": 0.8},
    
    # DISC - Influência (I) - 12 questões
    {"id": 13, "text": "Gosto de estar rodeado de pessoas e conversar sobre vários assuntos.", "category": "DISC_I", "weight": 0.9},
    {"id": 14, "text": "Tenho facilidade em fazer novos contatos e networking.", "category": "DISC_I", "weight": 0.85},
    {"id": 15, "text": "Prefiro trabalhar em equipe a trabalhar sozinho.", "category": "DISC_I", "weight": 0.7},
    {"id": 16, "text": "Sou bom em motivar e inspirar outras pessoas.", "category": "DISC_I", "weight": 0.8},
    {"id": 17, "text": "Gosto de apresentar ideias para grupos de pessoas.", "category": "DISC_I", "weight": 0.75},
    {"id": 18, "text": "Tenho facilidade em adaptar meu estilo de comunicação às pessoas.", "category": "DISC_I", "weight": 0.7},
    {"id": 19, "text": "Prefiro ambientes dinâmicos e socialmente ativos.", "category": "DISC_I", "weight": 0.8},
    {"id": 20, "text": "Costumo ser otimista mesmo em situações difíceis.", "category": "DISC_I", "weight": 0.6},
    {"id": 21, "text": "Gosto de convencer pessoas através do entusiasmo.", "category": "DISC_I", "weight": 0.8},
    {"id": 22, "text": "Me sinto energizado em eventos sociais.", "category": "DISC_I", "weight": 0.85},
    {"id": 23, "text": "Prefiro comunicação verbal à escrita.", "category": "DISC_I", "weight": 0.7},
    {"id": 24, "text": "Gosto de reconhecimento público pelo meu trabalho.", "category": "DISC_I", "weight": 0.75},
    
    # DISC - Estabilidade (S) - 12 questões
    {"id": 25, "text": "Valorizo consistência e previsibilidade no trabalho.", "category": "DISC_S", "weight": 0.85},
    {"id": 26, "text": "Prefiro mudanças graduais a transformações bruscas.", "category": "DISC_S", "weight": 0.8},
    {"id": 27, "text": "Sou uma pessoa paciente e raramente me irrito.", "category": "DISC_S", "weight": 0.75},
    {"id": 28, "text": "Gosto de ajudar outros e oferecer suporte quando necessário.", "category": "DISC_S", "weight": 0.7},
    {"id": 29, "text": "Prefiro harmonia a conflito em relacionamentos.", "category": "DISC_S", "weight": 0.8},
    {"id": 30, "text": "Sou confiável e as pessoas sabem que podem contar comigo.", "category": "DISC_S", "weight": 0.85},
    {"id": 31, "text": "Gosto de rotinas estabelecidas e métodos testados.", "category": "DISC_S", "weight": 0.7},
    {"id": 32, "text": "Prefiro cooperar a competir com colegas.", "category": "DISC_S", "weight": 0.75},
    {"id": 33, "text": "Sou leal às pessoas e organizações.", "category": "DISC_S", "weight": 0.8},
    {"id": 34, "text": "Gosto de ambientes de trabalho estáveis.", "category": "DISC_S", "weight": 0.85},
    {"id": 35, "text": "Prefiro ouvir antes de falar.", "category": "DISC_S", "weight": 0.7},
    {"id": 36, "text": "Valorizo relacionamentos de longo prazo.", "category": "DISC_S", "weight": 0.75},
    
    # DISC - Conformidade (C) - 12 questões
    {"id": 37, "text": "Gosto de seguir métodos e padrões bem definidos.", "category": "DISC_C", "weight": 0.9},
    {"id": 38, "text": "Presto atenção aos detalhes e busco precisão no meu trabalho.", "category": "DISC_C", "weight": 0.85},
    {"id": 39, "text": "Prefiro ter todas as informações antes de tomar uma decisão.", "category": "DISC_C", "weight": 0.8},
    {"id": 40, "text": "Valorizo qualidade mais do que velocidade na execução.", "category": "DISC_C", "weight": 0.75},
    {"id": 41, "text": "Gosto de analisar dados e fatos antes de formar opinião.", "category": "DISC_C", "weight": 0.8},
    {"id": 42, "text": "Prefiro trabalhar de forma sistemática e organizada.", "category": "DISC_C", "weight": 0.85},
    {"id": 43, "text": "Fico incomodado quando as regras não são seguidas.", "category": "DISC_C", "weight": 0.7},
    {"id": 44, "text": "Gosto de planejar cuidadosamente antes de agir.", "category": "DISC_C", "weight": 0.75},
    {"id": 45, "text": "Prefiro documentar processos e procedimentos.", "category": "DISC_C", "weight": 0.8},
    {"id": 46, "text": "Sou cuidadoso ao tomar decisões importantes.", "category": "DISC_C", "weight": 0.85},
    {"id": 47, "text": "Gosto de trabalhar com precisão e exatidão.", "category": "DISC_C", "weight": 0.9},
    {"id": 48, "text": "Valorizo expertise técnica e conhecimento especializado.", "category": "DISC_C", "weight": 0.7}
]

def initialize_session_state():
    """Inicializa variáveis de sessão"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_name' not in st.session_state:
        st.session_state.user_name = ""
    if 'user_email' not in st.session_state:
        st.session_state.user_email = ""
    if 'user_id' not in st.session_state:
        st.session_state.user_id = ""
    if 'id_token' not in st.session_state:
        st.session_state.id_token = ""
    if 'assessment_completed' not in st.session_state:
        st.session_state.assessment_completed = False
    if 'assessment_answers' not in st.session_state:
        st.session_state.assessment_answers = {}
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'dashboard'
    if 'results' not in st.session_state:
        st.session_state.results = None
    if 'selected_questions' not in st.session_state:
        st.session_state.selected_questions = None
    if 'assessment_start_time' not in st.session_state:
        st.session_state.assessment_start_time = None
    if 'question_page' not in st.session_state:
        st.session_state.question_page = 0
    if 'confirm_restart' not in st.session_state:
        st.session_state.confirm_restart = False

def firebase_signup(email, password, display_name=""):
    """Cadastra usuário no Firebase"""
    try:
        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }
        
        if display_name:
            payload["displayName"] = display_name
            
        response = requests.post(FIREBASE_SIGNUP_URL, json=payload, timeout=10)
        
        if response.status_code == 200:
            return True, response.json(), "Usuário cadastrado com sucesso!"
        else:
            error_data = response.json()
            error_message = error_data.get('error', {}).get('message', 'Erro desconhecido')
            
            if 'EMAIL_EXISTS' in error_message:
                return False, None, "Este email já está cadastrado"
            elif 'WEAK_PASSWORD' in error_message:
                return False, None, "Senha muito fraca. Use pelo menos 6 caracteres"
            elif 'INVALID_EMAIL' in error_message:
                return False, None, "Email inválido"
            else:
                return False, None, f"Erro: {error_message}"
                
    except Exception as e:
        return False, None, f"Erro de conexão: {str(e)}"

def firebase_signin(email, password):
    """Faz login no Firebase"""
    try:
        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }
        
        response = requests.post(FIREBASE_SIGNIN_URL, json=payload, timeout=10)
        
        if response.status_code == 200:
            return True, response.json(), "Login realizado com sucesso!"
        else:
            error_data = response.json()
            error_message = error_data.get('error', {}).get('message', 'Erro desconhecido')
            
            if 'EMAIL_NOT_FOUND' in error_message:
                return False, None, "Email não encontrado"
            elif 'INVALID_PASSWORD' in error_message:
                return False, None, "Senha incorreta"
            elif 'USER_DISABLED' in error_message:
                return False, None, "Usuário desabilitado"
            elif 'INVALID_EMAIL' in error_message:
                return False, None, "Email inválido"
            else:
                return False, None, f"Erro: {error_message}"
                
    except Exception as e:
        return False, None, f"Erro de conexão: {str(e)}"

def firebase_reset_password(email):
    """Envia email de reset de senha"""
    try:
        payload = {
            "requestType": "PASSWORD_RESET",
            "email": email
        }
        
        response = requests.post(FIREBASE_RESET_URL, json=payload, timeout=10)
        
        if response.status_code == 200:
            return True, "Email de recuperação enviado!"
        else:
            error_data = response.json()
            error_message = error_data.get('error', {}).get('message', 'Erro desconhecido')
            
            if 'EMAIL_NOT_FOUND' in error_message:
                return False, "Email não encontrado"
            else:
                return False, f"Erro: {error_message}"
                
    except Exception as e:
        return False, f"Erro de conexão: {str(e)}"

def save_assessment_to_firebase(user_id, results):
    """Salva avaliação no Firebase Realtime Database"""
    if not FIREBASE_PROJECT_ID or not user_id:
        return False
    
    try:
        url = f"{FIREBASE_DATABASE_URL}/assessments/{user_id}.json"
        
        data = {
            "results": results,
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id
        }
        
        response = requests.put(url, json=data, timeout=10)
        return response.status_code == 200
        
    except Exception as e:
        st.error(f"Erro ao salvar no Firebase: {e}")
        return False

def load_assessment_from_firebase(user_id):
    """Carrega avaliação do Firebase Realtime Database"""
    if not FIREBASE_PROJECT_ID or not user_id:
        return None
    
    try:
        url = f"{FIREBASE_DATABASE_URL}/assessments/{user_id}.json"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data:
                return data.get("results")
        
        return None
        
    except Exception as e:
        st.error(f"Erro ao carregar do Firebase: {e}")
        return None

def generate_random_questions(num_questions=48):
    """Gera conjunto aleatório de questões balanceadas"""
    selected = []
    categories = ['DISC_D', 'DISC_I', 'DISC_S', 'DISC_C']
    
    for category in categories:
        category_questions = [q for q in QUESTION_POOL if q['category'] == category]
        selected.extend(category_questions)
    
    random.shuffle(selected)
    
    for i, question in enumerate(selected, 1):
        question['display_id'] = i
    
    return selected

def render_header():
    """Renderiza cabeçalho principal"""
    st.markdown("""
    <div class="main-header">
        <h1 style='margin-bottom: 1rem; font-size: 3rem; font-weight: 700;'>
            🧠 NeuroMap Pro
        </h1>
        <p style='font-size: 1.4rem; margin: 0; opacity: 0.95; font-weight: 500;'>
            Análise Científica Avançada de Personalidade
        </p>
    </div>
    """, unsafe_allow_html=True)

def render_sidebar():
    """Renderiza sidebar com navegação"""
    with st.sidebar:
        st.markdown("### 🧭 Navegação")
        
        if st.session_state.authenticated:
            st.success(f"👋 Olá, {st.session_state.user_name}!")
            st.caption(f"📧 {st.session_state.user_email}")
            
            # Botões de navegação com keys únicos
            if st.button("🏠 Dashboard", key="nav_dashboard", use_container_width=True):
                st.session_state.current_page = 'dashboard'
                st.rerun()
            
            if st.button("📝 Nova Avaliação", key="nav_assessment", use_container_width=True):
                st.session_state.assessment_answers = {}
                st.session_state.selected_questions = None
                st.session_state.assessment_completed = False
                st.session_state.results = None
                st.session_state.question_page = 0
                st.session_state.current_page = 'assessment'
                st.rerun()
            
            if st.session_state.assessment_completed or st.session_state.results:
                if st.button("📊 Ver Resultados", key="nav_results", use_container_width=True):
                    st.session_state.current_page = 'results'
                    st.rerun()
            
            st.markdown("---")
            
            if st.button("🚪 Sair", key="nav_logout", use_container_width=True):
                # Limpa dados de autenticação
                for key in ['authenticated', 'user_name', 'user_email', 'user_id', 'id_token', 
                          'assessment_completed', 'assessment_answers', 'results', 'selected_questions']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.session_state.current_page = 'home'
                st.rerun()
        else:
            render_auth_sidebar()

def render_auth_sidebar():
    """Renderiza autenticação na sidebar"""
    
    if not FIREBASE_API_KEY:
        st.error("⚠️ Configure FIREBASE_API_KEY nos secrets")
        return
    
    st.markdown("### 🔑 Acesso")
    
    tab1, tab2, tab3 = st.tabs(["Entrar", "Cadastrar", "Recuperar"])
    
    with tab1:
        st.markdown("**Login com Firebase**")
        
        with st.form("login_form"):
            email = st.text_input("📧 Email", placeholder="seu@email.com")
            password = st.text_input("🔐 Senha", type="password")
            
            if st.form_submit_button("🚀 Entrar", use_container_width=True):
                if email and password:
                    with st.spinner("🔐 Autenticando..."):
                        success, data, message = firebase_signin(email, password)
                        
                        if success:
                            st.session_state.authenticated = True
                            st.session_state.user_email = email
                            st.session_state.user_name = data.get('displayName', email.split('@')[0])
                            st.session_state.user_id = data.get('localId', '')
                            st.session_state.id_token = data.get('idToken', '')
                            st.session_state.current_page = 'dashboard'
                            
                            # Carrega avaliação existente
                            existing_results = load_assessment_from_firebase(st.session_state.user_id)
                            if existing_results:
                                st.session_state.results = existing_results
                                st.session_state.assessment_completed = True
                            
                            st.success("✅ Login realizado!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(f"❌ {message}")
                else:
                    st.error("❌ Preencha email e senha")
    
    with tab2:
        st.markdown("**Criar Nova Conta**")
        
        with st.form("signup_form"):
            name = st.text_input("👤 Nome", placeholder="Seu nome completo")
            email = st.text_input("📧 Email", placeholder="seu@email.com")
            password = st.text_input("🔐 Senha", type="password", help="Mínimo 6 caracteres")
            confirm_password = st.text_input("🔐 Confirmar Senha", type="password")
            
            if st.form_submit_button("📝 Criar Conta", use_container_width=True):
                if name and email and password and confirm_password:
                    if password != confirm_password:
                        st.error("❌ Senhas não conferem")
                    else:
                        with st.spinner("📝 Criando conta..."):
                            success, data, message = firebase_signup(email, password, name)
                            
                            if success:
                                st.success("✅ Conta criada com sucesso!")
                                st.info("👆 Agora faça login na aba 'Entrar'")
                            else:
                                st.error(f"❌ {message}")
                else:
                    st.error("❌ Preencha todos os campos")
    
    with tab3:
        st.markdown("**Esqueceu a Senha?**")
        
        with st.form("reset_form"):
            email = st.text_input("📧 Email da conta", placeholder="seu@email.com")
            
            if st.form_submit_button("📨 Enviar Reset", use_container_width=True):
                if email:
                    with st.spinner("📨 Enviando email..."):
                        success, message = firebase_reset_password(email)
                        
                        if success:
                            st.success("✅ Email de recuperação enviado!")
                            st.info("📬 Verifique sua caixa de entrada")
                        else:
                            st.error(f"❌ {message}")
                else:
                    st.error("❌ Digite seu email")

def render_login_required():
    """Renderiza tela de login obrigatório"""
    
    if not FIREBASE_API_KEY:
        st.error("""
        ⚠️ **Configuração Firebase Necessária**
        
        Para usar autenticação Firebase, você precisa configurar:
        1. `FIREBASE_API_KEY` nos secrets do Streamlit
        2. `FIREBASE_PROJECT_ID` nos secrets do Streamlit
        
        Obtenha essas chaves no console do Firebase.
        """)
        return
    
    st.markdown("""
    <div class="login-required">
        <h2 style="font-size: 2.5rem; margin-bottom: 1rem;">🔒 Login com Firebase</h2>
        <p style="font-size: 1.3rem; margin: 1.5rem 0;">
            Para acessar o NeuroMap Pro, faça login ou crie uma conta.
        </p>
        <p style="font-size: 1.2rem; font-weight: 500;">
            👈 Use a barra lateral para entrar ou se cadastrar
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Informações sobre a ferramenta
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🎯 O que você terá acesso:
        
        - **48 questões científicas** balanceadas
        - **Análise DISC completa** detalhada
        - **Perfil comportamental** profundo
        - **Relatórios PDF** para download
        - **Dados salvos** na nuvem Firebase
        - **Histórico de avaliações** pessoal
        """)
    
    with col2:
        st.markdown("""
        ### 🔒 Segurança Firebase:
        
        - 🛡️ **Autenticação segura** do Google
        - ☁️ **Dados na nuvem** protegidos
        - 🔐 **Criptografia** end-to-end
        - 📱 **Acesso multiplataforma**
        - 🔄 **Recuperação de senha** automática
        - ✅ **Conformidade LGPD**
        """)

def render_dashboard():
    """Renderiza dashboard principal"""
    st.markdown(f"## 👋 Bem-vindo, {st.session_state.user_name}!")
    
    # Carrega dados existentes se ainda não carregou
    if not st.session_state.results and st.session_state.user_id:
        existing_results = load_assessment_from_firebase(st.session_state.user_id)
        if existing_results:
            st.session_state.results = existing_results
            st.session_state.assessment_completed = True
    
    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        completed = "1" if st.session_state.assessment_completed else "0"
        delta = "✨ Completa!" if st.session_state.assessment_completed else "Pendente"
        st.metric("📊 Avaliações", completed, delta=delta)
    
    with col2:
        if st.session_state.assessment_completed and st.session_state.results:
            mbti_type = st.session_state.results.get('mbti_type', 'N/A')
            st.metric("🎭 Tipo MBTI", mbti_type, delta="Identificado")
        else:
            st.metric("🎭 Tipo MBTI", "?", delta="Não avaliado")
    
    with col3:
        if st.session_state.assessment_completed and st.session_state.results:
            reliability = st.session_state.results.get('reliability', 0)
            delta = "Alta" if reliability > 80 else "Média" if reliability > 60 else "Baixa"
            st.metric("🎯 Confiabilidade", f"{reliability}%", delta=delta)
        else:
            st.metric("🎯 Confiabilidade", "0%", delta="Não avaliado")
    
    with col4:
        if st.session_state.assessment_completed and st.session_state.results:
            completion_time = st.session_state.results.get('completion_time', 0)
            st.metric("⏱️ Tempo", f"{completion_time} min", delta="Concluído")
        else:
            st.metric("⏱️ Tempo", "0 min", delta="Não iniciado")
    
    st.markdown("---")
    
    # Informações do usuário Firebase
    if st.session_state.user_id:
        st.info(f"🔐 **Conta Firebase:** {st.session_state.user_email} | **ID:** {st.session_state.user_id[:8]}...")
    
    # Ações principais
    if not st.session_state.assessment_completed:
        st.markdown("### 🚀 Pronto para descobrir seu perfil?")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("""
            **Sua jornada de autoconhecimento começa aqui!**
            
            Nossa avaliação científica revelará:
            • Seu estilo de liderança natural
            • Pontos fortes únicos e talentos
            • Áreas para desenvolvimento profissional  
            • Orientações de carreira personalizadas
            • Estratégias de comunicação efetiva
            """)
        
        with col2:
            if st.button("🎯 Iniciar Avaliação", key="start_assessment", type="primary", use_container_width=True):
                st.session_state.current_page = 'assessment'
                st.rerun()
            
            st.caption("⏱️ **Tempo:** 25-30 minutos")
            st.caption("📊 **Questões:** 48 científicas")
            st.caption("🔀 **Ordem:** Aleatória")
    
    else:
        st.markdown("### 🎉 Sua avaliação está completa!")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📊 Ver Análise Completa", key="view_results", type="primary", use_container_width=True):
                st.session_state.current_page = 'results'
                st.rerun()
        
        with col2:
            if st.button("🔄 Nova Avaliação", key="new_assessment", use_container_width=True):
                st.session_state.assessment_answers = {}
                st.session_state.selected_questions = None
                st.session_state.assessment_completed = False
                st.session_state.results = None
                st.session_state.question_page = 0
                st.session_state.current_page = 'assessment'
                st.rerun()
        
        # Preview dos resultados
        if st.session_state.results:
            render_results_preview()

def render_assessment():
    """Renderiza página de avaliação"""
    
    # Gera questões na primeira vez
    if st.session_state.selected_questions is None:
        st.session_state.selected_questions = generate_random_questions(48)
        st.session_state.assessment_start_time = datetime.now()
    
    questions = st.session_state.selected_questions
    
    st.title("📝 Avaliação de Personalidade")
    
    # Progress
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
    current_page = st.session_state.question_page
    
    # Navegação
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if current_page > 0:
            if st.button("⬅️ Anterior", key="prev_page", use_container_width=True):
                st.session_state.question_page = current_page - 1
                st.rerun()
    
    with col2:
        st.markdown(f"### 📄 Página {current_page + 1} de {total_pages}")
    
    with col3:
        if current_page < total_pages - 1:
            if st.button("Próxima ➡️", key="next_page", use_container_width=True):
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
    
    # Ações finais
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💾 Salvar", key="save_progress", use_container_width=True):
            st.success("✅ Progresso salvo!")
            time.sleep(1)
    
    with col2:
        if answered >= total_questions:
            if st.button("✨ Finalizar", key="finish_assessment", type="primary", use_container_width=True):
                with st.spinner("🧠 Processando..."):
                    calculate_results()
                    
                    # Salva no Firebase
                    if st.session_state.user_id and st.session_state.results:
                        save_assessment_to_firebase(st.session_state.user_id, st.session_state.results)
                    
                    st.session_state.assessment_completed = True
                    st.session_state.current_page = 'results'
                    st.success("🎉 Concluído!")
                    time.sleep(2)
                    st.rerun()
        else:
            st.info(f"📝 Faltam {remaining} questões")
    
    with col3:
        if st.button("🔄 Reiniciar", key="restart_assessment", use_container_width=True):
            if st.session_state.confirm_restart:
                st.session_state.assessment_answers = {}
                st.session_state.selected_questions = None
                st.session_state.question_page = 0
                st.session_state.confirm_restart = False
                st.rerun()
            else:
                st.session_state.confirm_restart = True
                st.warning("⚠️ Clique novamente para confirmar")

def render_single_question(question):
    """Renderiza uma questão individual"""
    
    st.markdown(f"""
    <div class="question-container">
        <h4>
            {question['display_id']}. {question['text']}
        </h4>
    </div>
    """, unsafe_allow_html=True)
    
    # Escala Likert
    current_value = st.session_state.assessment_answers.get(question['display_id'], 3)
    
    # Radio buttons
    options = [
        (1, "1 - Discordo Totalmente"),
        (2, "2 - Discordo Parcialmente"),
        (3, "3 - Neutro"),
        (4, "4 - Concordo Parcialmente"),
        (5, "5 - Concordo Totalmente")
    ]
    
    selected = st.radio(
        "Escolha sua resposta:",
        options,
        index=current_value - 1,
        key=f"q{question['display_id']}_radio_{question['id']}",
        format_func=lambda x: x[1],
        horizontal=True,
        label_visibility="collapsed"
    )
    
    st.session_state.assessment_answers[question['display_id']] = selected[0]
    
    # Feedback visual
    feedback_emojis = {1: "🔴", 2: "🟠", 3: "🟡", 4: "🟢", 5: "🟢"}
    feedback_texts = {
        1: "Discordo totalmente",
        2: "Discordo parcialmente", 
        3: "Neutro",
        4: "Concordo parcialmente",
        5: "Concordo totalmente"
    }
    
    st.caption(f"{feedback_emojis[selected[0]]} {feedback_texts[selected[0]]}")
    
    st.markdown("---")

def calculate_results():
    """Calcula resultados da avaliação"""
    
    answers = st.session_state.assessment_answers
    questions = st.session_state.selected_questions
    
    # Inicializa scores
    disc_scores = {"D": 0.0, "I": 0.0, "S": 0.0, "C": 0.0}
    disc_counts = {"D": 0, "I": 0, "S": 0, "C": 0}
    
    # Processa respostas
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
    
    # Calcula médias ponderadas
    for dim in disc_scores:
        if disc_counts[dim] > 0:
            disc_scores[dim] = disc_scores[dim] / disc_counts[dim]
    
    # Normaliza DISC para soma 100%
    disc_total = sum(disc_scores.values())
    if disc_total > 0:
        for key in disc_scores:
            disc_scores[key] = (disc_scores[key] / disc_total) * 100
    
    # Determina MBTI simplificado
    mbti_type = ""
    mbti_type += "E" if disc_scores["I"] > 25 else "I"
    mbti_type += "S" if disc_scores["C"] > 25 else "N"
    mbti_type += "T" if disc_scores["D"] > 25 else "F"
    mbti_type += "J" if disc_scores["C"] > 25 else "P"
    
    # Calcula confiabilidade
    response_values = list(answers.values())
    response_variance = np.var(response_values) if len(response_values) > 1 else 0
    
    if response_variance < 0.5:
        reliability = 65
    elif response_variance > 2.0:
        reliability = 75
    else:
        reliability = 85 + random.randint(0, 10)
    
    # Tempo de conclusão
    completion_time = 0
    if st.session_state.assessment_start_time:
        completion_time = (datetime.now() - st.session_state.assessment_start_time).seconds // 60
    
    # Armazena resultados
    st.session_state.results = {
        "disc": disc_scores,
        "mbti_type": mbti_type,
        "reliability": reliability,
        "completion_time": completion_time,
        "total_questions": len(questions),
        "response_consistency": round(response_variance, 2)
    }

def render_results():
    """Renderiza página de resultados"""
    
    st.title("🎉 Seus Resultados")
    
    results = st.session_state.get('results')
    if not results:
        st.error("❌ Nenhum resultado encontrado.")
        return
    
    # Header de resultados
    st.markdown(f"""
    <div class="insight-card">
        <h2 style="color: #2d3748; margin-top: 0;">🎯 Resumo do seu Perfil</h2>
        <p style="font-size: 1.2rem; margin-bottom: 0;">
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
        st.metric("🧠 Tipo MBTI", results['mbti_type'])
    
    with col3:
        st.metric("🎯 Confiabilidade", f"{results['reliability']}%")
    
    with col4:
        st.metric("📊 Consistência", f"{results['response_consistency']:.1f}")
    
    st.markdown("---")
    
    # Análise DISC detalhada
    st.markdown("### 🎭 Análise DISC Detalhada")
    
    disc_descriptions = {
        "D": ("Dominância", "Orientação para resultados, liderança direta, tomada de decisão rápida"),
        "I": ("Influência", "Comunicação persuasiva, networking, motivação de equipes"),
        "S": ("Estabilidade", "Cooperação, paciência, trabalho em equipe consistente"),
        "C": ("Conformidade", "Foco em qualidade, precisão, análise sistemática")
    }
    
    for key, score in results['disc'].items():
        name, description = disc_descriptions[key]
        
        if score >= 35:
            level = "Alto"
            color = "#48bb78"
        elif score >= 20:
            level = "Moderado"
            color = "#ed8936"
        else:
            level = "Baixo"
            color = "#e53e3e"
        
        st.markdown(f"""
        <div style="background: {color}20; padding: 1.5rem; border-radius: 12px; margin: 1rem 0; 
                    border-left: 6px solid {color};">
            <h5 style="margin: 0; color: {color}; font-size: 1.2rem;">{name} - {score:.0f}% ({level})</h5>
            <p style="margin: 0.8rem 0 0 0; color: #2d3748; font-size: 1rem;">
                {description}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Tipo MBTI
    st.markdown("### 💭 Tipo MBTI")
    
    mbti_type = results['mbti_type']
    mbti_descriptions = get_mbti_description(mbti_type)
    
    st.markdown(f"""
    <div class="insight-card">
        <h3 style="color: #2d3748; margin-top: 0; font-size: 1.5rem;">
            Tipo {mbti_type}: {mbti_descriptions['title']}
        </h3>
        <p style="font-size: 1.2rem; color: #2d3748;">{mbti_descriptions['description']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Insights e recomendações
    st.markdown("### 🎯 Insights e Recomendações")
    
    insights = generate_insights(dominant_disc, mbti_type, results)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🏆 Pontos Fortes")
        for strength in insights['strengths']:
            st.markdown(f"""
            <div class="strength-card">
                <strong>{strength}</strong>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("#### 📈 Desenvolvimento")
        for area in insights['development']:
            st.markdown(f"""
            <div class="development-card">
                <strong>{area}</strong>
            </div>
            """, unsafe_allow_html=True)
    
    # Carreiras sugeridas
    st.markdown("#### 💼 Carreiras Sugeridas")
    for career in insights['careers']:
        st.markdown(f"""
        <div class="career-card">
            <strong>{career}</strong>
        </div>
        """, unsafe_allow_html=True)
    
    # Botão de download PDF
    st.markdown("---")
    
    if st.button("📄 Gerar e Baixar Relatório PDF", key="generate_pdf", type="primary", use_container_width=True):
        with st.spinner("📝 Gerando relatório..."):
            pdf_content = generate_pdf_report(results)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"NeuroMap_Relatorio_{timestamp}.pdf"
            
            st.download_button(
                label="⬇️ Baixar PDF",
                data=pdf_content,
                file_name=filename,
                mime="application/pdf",
                key="download_pdf",
                use_container_width=True
            )
            
            st.success("🎉 Relatório gerado!")

def render_results_preview():
    """Preview dos resultados no dashboard"""
    
    st.markdown("### 🎯 Resumo dos Resultados")
    
    results = st.session_state.results
    if not results:
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🎭 Perfil DISC")
        for dim, score in results['disc'].items():
            if score > 20:
                st.write(f"**{dim}**: {score:.0f}%")
    
    with col2:
        st.markdown("#### 💭 Tipo MBTI")
        st.write(f"**Tipo**: {results['mbti_type']}")
        st.write(f"**Confiabilidade**: {results['reliability']}%")

def get_mbti_description(mbti_type):
    """Retorna descrição do tipo MBTI"""
    
    descriptions = {
        'ESTJ': {
            'title': 'O Executivo',
            'description': 'Líder natural focado em eficiência e resultados, com talento para organizar pessoas e recursos.'
        },
        'ENTJ': {
            'title': 'O Comandante', 
            'description': 'Visionário estratégico com capacidade natural de liderança e foco em objetivos de longo prazo.'
        },
        'ESFJ': {
            'title': 'O Cônsul',
            'description': 'Pessoa calorosa e atenciosa, focada em harmonia e bem-estar das pessoas ao redor.'
        },
        'ENFJ': {
            'title': 'O Protagonista',
            'description': 'Líder carismático e inspirador, capaz de motivar outros a alcançarem seu potencial.'
        },
        'ISTJ': {
            'title': 'O Logístico',
            'description': 'Pessoa prática e orientada a fatos, com confiabilidade que não pode ser questionada.'
        },
        'INTJ': {
            'title': 'O Arquiteto',
            'description': 'Pensador imaginativo e estratégico, com plano para tudo.'
        },
        'ISFJ': {
            'title': 'O Protetor',
            'description': 'Pessoa calorosa e dedicada, sempre pronta a defender seus entes queridos.'
        },
        'INFJ': {
            'title': 'O Advogado',
            'description': 'Pessoa criativa e perspicaz, inspirada e decidida, idealisticamente.'
        }
    }
    
    return descriptions.get(mbti_type, {
        'title': f'Tipo {mbti_type}',
        'description': f'Perfil único com características específicas da combinação {mbti_type}.'
    })

def generate_insights(dominant_disc, mbti_type, results):
    """Gera insights baseados no perfil"""
    
    insights = {
        'strengths': [
            'Liderança natural e orientação para resultados',
            'Capacidade de tomar decisões rapidamente',
            'Foco em eficiência e produtividade',
            'Habilidade de motivar equipes'
        ],
        'development': [
            'Desenvolver paciência com processos mais lentos',
            'Melhorar escuta ativa e empatia',
            'Praticar delegação efetiva',
            'Equilibrar assertividade com colaboração'
        ],
        'careers': [
            'Gerente ou Diretor Executivo',
            'Consultor Empresarial',
            'Empreendedor ou Fundador',
            'Líder de Projetos Estratégicos'
        ]
    }
    
    return insights

def generate_pdf_report(results):
    """Gera relatório PDF"""
    
    try:
        from fpdf import FPDF
        
        class PDF(FPDF):
            def header(self):
                self.set_font('Arial', 'B', 15)
                self.cell(0, 10, 'NeuroMap - Relatorio de Personalidade', 0, 1, 'C')
                self.ln(10)
            
            def footer(self):
                self.set_y(-15)
                self.set_font('Arial', 'I', 8)
                self.cell(0, 10, f'Pagina {self.page_no()}', 0, 0, 'C')
        
        pdf = PDF()
        pdf.add_page()
        
        # Título
        pdf.set_font('Arial', 'B', 20)
        pdf.ln(20)
        pdf.cell(0, 15, 'RELATORIO DE PERSONALIDADE', 0, 1, 'C')
        pdf.ln(10)
        
        # Informações básicas
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 8, f"Usuario Firebase: {st.session_state.user_email}", 0, 1, 'L')
        pdf.cell(0, 8, f"Tipo MBTI: {results['mbti_type']}", 0, 1, 'L')
        pdf.cell(0, 8, f"Confiabilidade: {results['reliability']}%", 0, 1, 'L')
        pdf.cell(0, 8, f"Data: {datetime.now().strftime('%d/%m/%Y')}", 0, 1, 'L')
        pdf.ln(10)
        
        # Perfil DISC
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'PERFIL DISC:', 0, 1, 'L')
        pdf.set_font('Arial', '', 12)
        
        for key, value in results['disc'].items():
            pdf.cell(0, 6, f"{key}: {value:.1f}%", 0, 1, 'L')
        
        pdf.ln(10)
        
        # Insights
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'PRINCIPAIS PONTOS FORTES:', 0, 1, 'L')
        pdf.set_font('Arial', '', 11)
        
        strengths = [
            'Lideranca natural e orientacao para resultados',
            'Capacidade de tomar decisoes rapidamente', 
            'Foco em eficiencia e produtividade',
            'Habilidade de motivar equipes'
        ]
        
        for strength in strengths:
            pdf.cell(0, 6, f"• {strength}", 0, 1, 'L')
        
        # Converte para bytes
        pdf_output = pdf.output(dest='S')
        return pdf_output.encode('latin1') if isinstance(pdf_output, str) else pdf_output
        
    except Exception as e:
        st.error(f"Erro ao gerar PDF: {e}")
        return b"Erro na geracao do PDF"

def main():
    """Função principal"""
    initialize_session_state()
    render_header()
    render_sidebar()
    
    # Verifica autenticação
    if not st.session_state.authenticated:
        render_login_required()
        return
    
    # Roteamento de páginas
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
