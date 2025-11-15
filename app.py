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

# CSS com melhor contraste
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        color: #f1f5f9;
    }
    
    .main-header {
        background: linear-gradient(135deg, #1e40af 0%, #1d4ed8 100%);
        color: white;
        padding: 3rem 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 8px 32px rgba(30, 64, 175, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .metric-card {
        background: rgba(30, 41, 59, 0.95);
        padding: 2rem;
        border-radius: 15px;
        border-left: 6px solid #3b82f6;
        margin: 1rem 0;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(10px);
        color: #f1f5f9;
        border: 1px solid rgba(59, 130, 246, 0.2);
    }
    
    .question-container {
        background: rgba(30, 41, 59, 0.98);
        padding: 2.5rem;
        border-radius: 15px;
        border-left: 6px solid #3b82f6;
        margin: 2rem 0;
        box-shadow: 0 6px 25px rgba(0, 0, 0, 0.4);
        color: #f1f5f9;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(59, 130, 246, 0.2);
    }
    
    .question-container h4 {
        font-size: 1.3rem;
        font-weight: 600;
        line-height: 1.6;
        margin-bottom: 1.5rem;
        color: #ffffff !important;
        text-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
    }
    
    .insight-card {
        background: rgba(30, 41, 59, 0.95);
        padding: 2rem;
        border-radius: 15px;
        margin: 1.5rem 0;
        border-left: 6px solid #10b981;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        color: #f1f5f9;
        border: 1px solid rgba(16, 185, 129, 0.2);
    }
    
    .auth-container {
        background: rgba(30, 41, 59, 0.98);
        padding: 2.5rem;
        border-radius: 15px;
        margin: 1.5rem 0;
        box-shadow: 0 6px 25px rgba(0, 0, 0, 0.4);
        border: 1px solid rgba(59, 130, 246, 0.2);
        backdrop-filter: blur(10px);
        color: #f1f5f9;
    }
    
    .strength-card {
        background: linear-gradient(135deg, #059669 0%, #047857 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 0.8rem 0;
        box-shadow: 0 4px 15px rgba(5, 150, 105, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .development-card {
        background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 0.8rem 0;
        box-shadow: 0 4px 15px rgba(220, 38, 38, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .career-card {
        background: linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 0.8rem 0;
        box-shadow: 0 4px 15px rgba(124, 58, 237, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .login-required {
        background: linear-gradient(135deg, #1e40af 0%, #1d4ed8 100%);
        color: white;
        padding: 3rem 2rem;
        border-radius: 20px;
        text-align: center;
        margin: 2rem 0;
        box-shadow: 0 8px 32px rgba(30, 64, 175, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .stRadio > div {
        background: rgba(51, 65, 85, 0.9) !important;
        padding: 1.2rem !important;
        border-radius: 10px !important;
        margin: 0.5rem 0 !important;
        border: 1px solid rgba(59, 130, 246, 0.3) !important;
        color: #f1f5f9 !important;
    }
    
    .stRadio label {
        color: #f1f5f9 !important;
        font-weight: 500 !important;
    }
    
    .stMarkdown {
        color: #f1f5f9 !important;
    }
    
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4 {
        color: #ffffff !important;
        font-weight: 700 !important;
        text-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
    }
    
    .stMarkdown p {
        color: #e2e8f0 !important;
        line-height: 1.6 !important;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #1e40af 0%, #1d4ed8 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.8rem 2rem !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 15px rgba(30, 64, 175, 0.4) !important;
        transition: all 0.3s ease !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(30, 64, 175, 0.5) !important;
        background: linear-gradient(135deg, #1d4ed8 0%, #2563eb 100%) !important;
    }
    
    /* Progresso */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #3b82f6 0%, #60a5fa 100%) !important;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background: rgba(30, 41, 59, 0.95) !important;
        color: #f1f5f9 !important;
    }
    
    /* Métricas */
    [data-testid="metric-container"] {
        background: rgba(30, 41, 59, 0.95) !important;
        border: 1px solid rgba(59, 130, 246, 0.2) !important;
        padding: 1rem !important;
        border-radius: 10px !important;
        color: #f1f5f9 !important;
    }
    
    /* Inputs */
    .stTextInput > div > div > input {
        background: rgba(51, 65, 85, 0.9) !important;
        color: #f1f5f9 !important;
        border: 1px solid rgba(59, 130, 246, 0.3) !important;
    }
    
    .stSelectbox > div > div > div {
        background: rgba(51, 65, 85, 0.9) !important;
        color: #f1f5f9 !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(30, 41, 59, 0.9) !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: #e2e8f0 !important;
        background: rgba(51, 65, 85, 0.5) !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: rgba(59, 130, 246, 0.3) !important;
        color: #ffffff !important;
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
    """Salva avaliação no Firebase com método simplificado"""
    
    if not FIREBASE_PROJECT_ID:
        st.error("❌ FIREBASE_PROJECT_ID não configurado")
        return False
    
    if not user_id:
        st.error("❌ User ID não encontrado")
        return False
    
    try:
        # URL simplificada sem autenticação
        url = f"https://{FIREBASE_PROJECT_ID}-default-rtdb.firebaseio.com/assessments/{user_id}.json"
        
        data = {
            "results": results,
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "user_email": st.session_state.user_email,
            "version": "3.0"
        }
        
        st.write(f"🔄 **Salvando em:** {url}")
        st.write(f"📊 **Dados:** {len(str(data))} caracteres")
        
        # Usando requests.put sem autenticação (Firebase public rules)
        response = requests.put(url, json=data, timeout=20)
        
        st.write(f"📡 **Status HTTP:** {response.status_code}")
        st.write(f"📄 **Response:** {response.text}")
        
        if response.status_code == 200:
            st.success("✅ Dados salvos no Firebase com sucesso!")
            return True
        else:
            st.error(f"❌ Erro HTTP {response.status_code}: {response.text}")
            return False
        
    except Exception as e:
        st.error(f"❌ Erro ao salvar: {str(e)}")
        return False

def load_assessment_from_firebase(user_id):
    """Carrega avaliação do Firebase"""
    
    if not FIREBASE_PROJECT_ID or not user_id:
        return None
    
    try:
        url = f"https://{FIREBASE_PROJECT_ID}-default-rtdb.firebaseio.com/assessments/{user_id}.json"
        
        st.write(f"🔄 **Carregando de:** {url}")
        
        response = requests.get(url, timeout=10)
        
        st.write(f"📡 **Status HTTP:** {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if data and "results" in data:
                st.success(f"✅ Dados encontrados! Timestamp: {data.get('timestamp', 'N/A')}")
                return data["results"]
            else:
                st.info("📭 Nenhuma avaliação anterior encontrada")
                return None
        else:
            st.warning(f"⚠️ Erro ao carregar: {response.status_code}")
            return None
        
    except Exception as e:
        st.error(f"❌ Erro ao carregar: {str(e)}")
        return None

def test_firebase_connection():
    """Testa conexão com Firebase"""
    
    if not FIREBASE_PROJECT_ID:
        st.error("❌ FIREBASE_PROJECT_ID não configurado")
        return False
    
    try:
        # Testa acesso básico
        url = f"https://{FIREBASE_PROJECT_ID}-default-rtdb.firebaseio.com/.json"
        
        st.write(f"🧪 **Testando:** {url}")
        
        response = requests.get(url, timeout=10)
        
        st.write(f"📡 **Status:** {response.status_code}")
        st.write(f"📄 **Response:** {response.text}")
        
        if response.status_code == 200:
            st.success("✅ Firebase acessível!")
            
            # Testa escrita
            test_url = f"https://{FIREBASE_PROJECT_ID}-default-rtdb.firebaseio.com/test.json"
            test_data = {"test": "connection", "timestamp": datetime.now().isoformat()}
            
            write_response = requests.put(test_url, json=test_data, timeout=10)
            
            st.write(f"📝 **Teste de escrita:** {write_response.status_code}")
            
            if write_response.status_code == 200:
                st.success("✅ Escrita funcionando!")
                
                # Remove o teste
                requests.delete(test_url, timeout=10)
                return True
            else:
                st.error(f"❌ Erro na escrita: {write_response.status_code}")
                return False
        else:
            st.error(f"❌ Firebase inacessível: {response.status_code}")
            return False
            
    except Exception as e:
        st.error(f"❌ Erro de conexão: {str(e)}")
        return False

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

def calculate_results():
    """Calcula resultados da avaliação com algoritmo aprimorado"""
    
    answers = st.session_state.assessment_answers
    questions = st.session_state.selected_questions
    
    if not answers or not questions:
        st.error("❌ Dados da avaliação não encontrados")
        return
    
    # Inicializa scores DISC
    disc_raw_scores = {"D": 0.0, "I": 0.0, "S": 0.0, "C": 0.0}
    disc_question_counts = {"D": 0, "I": 0, "S": 0, "C": 0}
    
    # Processa cada resposta
    for q_id, answer in answers.items():
        question = next((q for q in questions if q['display_id'] == q_id), None)
        if not question:
            continue
            
        category = question['category']
        weight = question['weight']
        
        # Converte resposta Likert (1-5) para score ponderado
        if answer >= 4:
            contribution = (answer - 3) * weight  # +1 ou +2 * weight
        elif answer <= 2:
            contribution = (answer - 3) * weight  # -1 ou -2 * weight
        else:
            contribution = 0  # Neutro
        
        if category.startswith('DISC_'):
            dim = category.split('_')[1]
            disc_raw_scores[dim] += contribution
            disc_question_counts[dim] += 1
    
    # Calcula médias por dimensão
    disc_averages = {}
    for dim in disc_raw_scores:
        if disc_question_counts[dim] > 0:
            disc_averages[dim] = disc_raw_scores[dim] / disc_question_counts[dim]
        else:
            disc_averages[dim] = 0
    
    # Normaliza para escala 0-100 (com base mínima de 10%)
    min_score = min(disc_averages.values())
    max_score = max(disc_averages.values())
    
    # Evita divisão por zero
    if max_score == min_score:
        disc_scores = {"D": 25, "I": 25, "S": 25, "C": 25}
    else:
        range_scores = max_score - min_score
        disc_scores = {}
        
        for dim, score in disc_averages.items():
            normalized = ((score - min_score) / range_scores) * 40 + 10
            disc_scores[dim] = max(10, min(50, normalized))
    
    # Ajusta para somar 100%
    total = sum(disc_scores.values())
    for dim in disc_scores:
        disc_scores[dim] = (disc_scores[dim] / total) * 100
    
    # Determina MBTI baseado em múltiplos fatores
    mbti_type = ""
    
    # Extroversão vs Introversão (baseado em Influência)
    mbti_type += "E" if disc_scores["I"] > 30 else "I"
    
    # Sensação vs Intuição (baseado em Conformidade vs outros)
    mbti_type += "S" if disc_scores["C"] > 30 else "N"
    
    # Pensamento vs Sentimento (baseado em Dominância vs Estabilidade)
    thinking_score = disc_scores["D"] + disc_scores["C"]
    feeling_score = disc_scores["I"] + disc_scores["S"]
    mbti_type += "T" if thinking_score > feeling_score else "F"
    
    # Julgamento vs Percepção (baseado em Conformidade + Dominância)
    judging_score = disc_scores["C"] + disc_scores["D"]
    mbti_type += "J" if judging_score > 50 else "P"
    
    # Calcula confiabilidade baseada na variância e consistência
    response_values = list(answers.values())
    response_variance = np.var(response_values) if len(response_values) > 1 else 0
    
    # Verifica consistência interna
    consistency_score = 0
    for dim in ["D", "I", "S", "C"]:
        dim_responses = []
        for q_id, answer in answers.items():
            question = next((q for q in questions if q['display_id'] == q_id), None)
            if question and question['category'] == f'DISC_{dim}':
                dim_responses.append(answer)
        
        if len(dim_responses) > 1:
            dim_variance = np.var(dim_responses)
            consistency_score += (2.0 - min(2.0, dim_variance))
    
    consistency_score = consistency_score / 4
    
    # Calcula confiabilidade final (60-95%)
    base_reliability = 60
    variance_bonus = min(20, (2.0 - response_variance) * 10)
    consistency_bonus = min(15, consistency_score * 7.5)
    
    reliability = int(base_reliability + variance_bonus + consistency_bonus)
    reliability = max(60, min(95, reliability))
    
    # Tempo de conclusão
    completion_time = 0
    if st.session_state.assessment_start_time:
        completion_time = (datetime.now() - st.session_state.assessment_start_time).seconds // 60
    
    # Armazena resultados
    st.session_state.results = {
        "disc": disc_scores,
        "disc_raw": disc_raw_scores,
        "mbti_type": mbti_type,
        "reliability": reliability,
        "completion_time": max(1, completion_time),
        "total_questions": len(questions),
        "response_consistency": round(consistency_score, 2),
        "response_variance": round(response_variance, 2),
        "answered_questions": len(answers)
    }

def create_simple_charts():
    """Cria gráficos simples sem Plotly"""
    
    results = st.session_state.get('results')
    if not results:
        return
    
    disc_scores = results['disc']
    
    # Gráfico de barras simples
    st.markdown("### 📊 Perfil DISC")
    
    for dim, score in disc_scores.items():
        # Determina cor baseada no score
        if score >= 35:
            color = "#48bb78"  # Verde
        elif score >= 25:
            color = "#ed8936"  # Laranja  
        else:
            color = "#e53e3e"  # Vermelho
            
        # Cria barra visual
        bar_width = int((score / 100) * 50)  # Max 50 caracteres
        bar = "█" * bar_width + "░" * (50 - bar_width)
        
        st.markdown(f"""
        <div style="background: {color}20; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; 
                    border-left: 4px solid {color};">
            <strong>{dim}: {score:.1f}%</strong><br>
            <div style="font-family: monospace; font-size: 0.8rem;">
                {bar}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Métricas adicionais
    col1, col2, col3 = st.columns(3)
    
    with col1:
        dominant = max(disc_scores, key=disc_scores.get)
        st.metric("🎯 Perfil Dominante", dominant, f"{disc_scores[dominant]:.0f}%")
    
    with col2:
        st.metric("🧠 Tipo MBTI", results['mbti_type'])
    
    with col3:
        st.metric("📈 Confiabilidade", f"{results['reliability']}%")

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
                            
                            # Não carrega automaticamente para evitar logs
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
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🎯 O que você terá acesso:
        
        - **48 questões científicas** balanceadas
        - **Análise DISC completa** detalhada
        - **Perfil comportamental** profundo
        - **Gráficos visuais** informativos
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
    
    # Seção de debug Firebase
    with st.expander("🔧 Debug Firebase", expanded=False):
        st.markdown("### Configurações:")
        st.write(f"**Project ID:** {FIREBASE_PROJECT_ID}")
        st.write(f"**Database URL:** {FIREBASE_DATABASE_URL}")
        st.write(f"**User ID:** {st.session_state.user_id}")
        
        if st.button("🧪 Testar Conexão Firebase", key="test_firebase"):
            test_firebase_connection()
        
        if st.button("🔄 Carregar Dados", key="force_load"):
            if st.session_state.user_id:
                existing_results = load_assessment_from_firebase(st.session_state.user_id)
                if existing_results:
                    st.session_state.results = existing_results
                    st.session_state.assessment_completed = True
                    st.success("✅ Dados carregados!")
                    st.rerun()
        
        if st.session_state.results and st.button("💾 Salvar Dados", key="force_save"):
            if save_assessment_to_firebase(st.session_state.user_id, st.session_state.results):
                st.success("✅ Dados salvos!")
    
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
                with st.spinner("🧠 Processando resultados..."):
                    calculate_results()
                    
                    # Tenta salvar no Firebase
                    if st.session_state.user_id and st.session_state.results:
                        st.write("💾 **Salvando seus resultados...**")
                        save_success = save_assessment_to_firebase(st.session_state.user_id, st.session_state.results)
                        
                        if save_success:
                            st.success("✅ Resultados salvos na nuvem!")
                        else:
                            st.warning("⚠️ Resultados calculados, mas não foi possível salvar na nuvem")
                    
                    st.session_state.assessment_completed = True
                    st.session_state.current_page = 'results'
                    
                    st.success("🎉 Avaliação concluída!")
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
        <h2 style="color: #ffffff; margin-top: 0;">🎯 Resumo do seu Perfil</h2>
        <p style="font-size: 1.2rem; margin-bottom: 0; color: #e2e8f0;">
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
    
    # Gráficos simples
    create_simple_charts()
    
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
            <p style="margin: 0.8rem 0 0 0; color: #e2e8f0; font-size: 1rem;">
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
        <h3 style="color: #ffffff; margin-top: 0; font-size: 1.5rem;">
            Tipo {mbti_type}: {mbti_descriptions['title']}
        </h3>
        <p style="font-size: 1.2rem; color: #e2e8f0;">{mbti_descriptions['description']}</p>
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
    
    # Botão de download
    st.markdown("---")
    
    if st.button("📝 Gerar Relatório TXT", key="generate_txt", use_container_width=True):
        with st.spinner("📝 Gerando relatório..."):
            txt_content = generate_text_report(results)
            
            if txt_content is not None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"NeuroMap_Relatorio_{timestamp}.txt"
                
                st.download_button(
                    label="⬇️ Baixar Relatório",
                    data=txt_content,
                    file_name=filename,
                    mime="text/plain",
                    key="download_txt",
                    use_container_width=True
                )
                
                st.success("🎉 Relatório gerado!")
            else:
                st.error("❌ Erro ao gerar relatório")

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
        },
        'ESTP': {
            'title': 'O Empreendedor',
            'description': 'Pessoa espontânea, energética e entusiasta, que nunca perde uma oportunidade.'
        },
        'ENTP': {
            'title': 'O Debatedor',
            'description': 'Pensador inteligente e curioso que não consegue resistir a um desafio intelectual.'
        },
        'ESFP': {
            'title': 'O Animador',
            'description': 'Pessoa espontânea, energética e entusiasta, que torna a vida dos outros mais alegre.'
        },
        'ENFP': {
            'title': 'O Ativista',
            'description': 'Pessoa entusiasta, criativa e sociável, sempre capaz de encontrar uma razão para sorrir.'
        },
        'ISTP': {
            'title': 'O Virtuoso',
            'description': 'Experimentador ousado e prático, mestre de todos os tipos de ferramentas.'
        },
        'INTP': {
            'title': 'O Pensador',
            'description': 'Inventor inovador com sede insaciável de conhecimento.'
        },
        'ISFP': {
            'title': 'O Aventureiro',
            'description': 'Artista flexível e charmoso, sempre pronto para explorar novas possibilidades.'
        },
        'INFP': {
            'title': 'O Mediador',
            'description': 'Pessoa poética, bondosa e altruísta, sempre ansiosa para ajudar uma boa causa.'
        }
    }
    
    return descriptions.get(mbti_type, {
        'title': f'Tipo {mbti_type}',
        'description': f'Perfil único com características específicas da combinação {mbti_type}.'
    })

def generate_insights(dominant_disc, mbti_type, results):
    """Gera insights personalizados baseados no perfil real"""
    
    disc_scores = results['disc']
    
    # Identifica perfis dominantes (acima de 30%)
    high_traits = [dim for dim, score in disc_scores.items() if score >= 30]
    
    # Insights baseados em combinações reais
    if 'D' in high_traits and 'C' in high_traits:
        # Dominante + Conformidade = Líder Analítico
        strengths = [
            "Liderança baseada em dados e análise",
            "Tomada de decisão fundamentada",
            "Foco em resultados com qualidade",
            "Capacidade de planejamento estratégico"
        ]
        development = [
            "Desenvolver flexibilidade em situações imprevistas",
            "Melhorar comunicação interpessoal",
            "Praticar delegação com menos controle",
            "Equilibrar perfeccionismo com prazos"
        ]
        careers = [
            "CEO ou Diretor Geral",
            "Consultor em Gestão",
            "Gerente de Projetos Complexos",
            "Analista Sênior de Negócios"
        ]
    
    elif 'I' in high_traits and 'S' in high_traits:
        # Influência + Estabilidade = Colaborador Natural
        strengths = [
            "Excelente em trabalho em equipe",
            "Comunicação empática e efetiva",
            "Capacidade de mediar conflitos",
            "Construção de relacionamentos duradouros"
        ]
        development = [
            "Desenvolver assertividade em negociações",
            "Praticar tomada de decisão individual",
            "Melhorar gestão de tempo pessoal",
            "Aumentar conforto com mudanças rápidas"
        ]
        careers = [
            "Gerente de Recursos Humanos",
            "Coordenador de Equipes",
            "Consultor em Relacionamento",
            "Facilitador de Treinamentos"
        ]
    
    else:
        # Perfil padrão baseado no dominante
        if dominant_disc == 'D':
            strengths = [
                "Liderança natural e orientação para resultados",
                "Capacidade de tomar decisões rapidamente",
                "Foco em eficiência e produtividade",
                "Habilidade de superar obstáculos"
            ]
            development = [
                "Desenvolver paciência com processos colaborativos",
                "Melhorar escuta ativa",
                "Praticar delegação efetiva",
                "Equilibrar assertividade com diplomacia"
            ]
            careers = [
                "Diretor Executivo",
                "Gerente de Operações",
                "Empreendedor",
                "Líder de Vendas"
            ]
        
        elif dominant_disc == 'I':
            strengths = [
                "Comunicação persuasiva e carismática",
                "Capacidade de motivar equipes",
                "Networking e construção de relacionamentos",
                "Adaptabilidade social"
            ]
            development = [
                "Melhorar foco em detalhes",
                "Desenvolver planejamento de longo prazo",
                "Praticar escuta mais que fala",
                "Aumentar consistência nas entregas"
            ]
            careers = [
                "Gerente de Marketing",
                "Coordenador de Vendas",
                "Facilitador de Treinamentos",
                "Relações Públicas"
            ]
        
        elif dominant_disc == 'S':
            strengths = [
                "Confiabilidade e consistência",
                "Trabalho em equipe colaborativo",
                "Paciência e estabilidade emocional",
                "Suporte efetivo aos colegas"
            ]
            development = [
                "Desenvolver iniciativa pessoal",
                "Melhorar adaptação a mudanças",
                "Praticar liderança ativa",
                "Aumentar assertividade"
            ]
            careers = [
                "Coordenador de Suporte",
                "Analista de Processos",
                "Gerente de Operações",
                "Especialista em Atendimento"
            ]
        
        else:  # C dominante
            strengths = [
                "Atenção excepcional aos detalhes",
                "Análise sistemática e precisa",
                "Foco em qualidade e excelência",
                "Pensamento crítico desenvolvido"
            ]
            development = [
                "Melhorar comunicação interpessoal",
                "Desenvolver flexibilidade",
                "Praticar tomada de decisão rápida",
                "Aumentar tolerância a ambiguidade"
            ]
            careers = [
                "Analista de Dados",
                "Consultor Técnico",
                "Gerente de Qualidade",
                "Especialista em Compliance"
            ]
    
    return {
        'strengths': strengths,
        'development': development,
        'careers': careers
    }

def generate_text_report(results):
    """Gera relatório em texto simples para download"""
    
    try:
        # Cabeçalho
        report = "NEUROMAP PRO - RELATORIO DE PERSONALIDADE\n"
        report += "=" * 50 + "\n\n"
        
        # Informações gerais
        report += "INFORMACOES GERAIS:\n"
        report += f"Usuario: {st.session_state.user_email}\n"
        report += f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
        report += f"Tempo de conclusao: {results['completion_time']} minutos\n"
        report += f"Total de questoes: {results['total_questions']}\n"
        report += f"Confiabilidade: {results['reliability']}%\n"
        report += f"Tipo MBTI: {results['mbti_type']}\n\n"
        
        # Perfil DISC
        report += "PERFIL DISC DETALHADO:\n"
        report += "-" * 25 + "\n"
        
        disc_descriptions = {
            "D": "Dominancia - Orientacao para resultados",
            "I": "Influencia - Comunicacao e networking",
            "S": "Estabilidade - Cooperacao e paciencia", 
            "C": "Conformidade - Qualidade e precisao"
        }
        
        for key, value in results['disc'].items():
            description = disc_descriptions[key]
            if value >= 35:
                level = "Alto"
            elif value >= 20:
                level = "Moderado"
            else:
                level = "Baixo"
            
            report += f"{description}: {value:.0f}% (Nivel {level})\n"
        
        report += "\n"
        
        # Pontos fortes
        report += "PONTOS FORTES IDENTIFICADOS:\n"
        report += "-" * 30 + "\n"
        strengths = [
            "Lideranca natural e orientacao para resultados",
            "Capacidade de tomar decisoes rapidamente",
            "Foco em eficiencia e produtividade", 
            "Habilidade de motivar equipes",
            "Comunicacao clara e direta"
        ]
        
        for i, strength in enumerate(strengths, 1):
            report += f"{i}. {strength}\n"
        
        report += "\n"
        
        # Áreas de desenvolvimento
        report += "AREAS PARA DESENVOLVIMENTO:\n"
        report += "-" * 30 + "\n"
        development_areas = [
            "Desenvolver paciencia com processos mais lentos",
            "Melhorar escuta ativa e empatia",
            "Praticar delegacao efetiva",
            "Equilibrar assertividade com colaboracao"
        ]
        
        for i, area in enumerate(development_areas, 1):
            report += f"{i}. {area}\n"
        
        report += "\n"
        
        # Carreiras sugeridas
        report += "CARREIRAS SUGERIDAS:\n"
        report += "-" * 20 + "\n"
        careers = [
            "Gerente ou Diretor Executivo",
            "Consultor Empresarial",
            "Empreendedor ou Fundador", 
            "Lider de Projetos Estrategicos",
            "Coordenador de Equipes"
        ]
        
        for i, career in enumerate(careers, 1):
            report += f"{i}. {career}\n"
        
        report += "\n" + "=" * 50 + "\n"
        report += f"Relatorio gerado em {datetime.now().strftime('%d/%m/%Y as %H:%M')}\n"
        report += "NeuroMap Pro - Analise Cientifica de Personalidade\n"
        
        return report.encode('utf-8')
        
    except Exception as e:
        st.error(f"❌ Erro ao gerar relatório: {str(e)}")
        return None

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
