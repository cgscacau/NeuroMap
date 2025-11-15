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

# URLs do Firebase
FIREBASE_SIGNUP_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FIREBASE_API_KEY}"
FIREBASE_SIGNIN_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
FIREBASE_RESET_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={FIREBASE_API_KEY}"
FIRESTORE_BASE_URL = f"https://firestore.googleapis.com/v1/projects/{FIREBASE_PROJECT_ID}/databases/(default)/documents"

# CSS
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
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(30, 64, 175, 0.5) !important;
        background: linear-gradient(135deg, #1d4ed8 0%, #2563eb 100%) !important;
    }
    
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #3b82f6 0%, #60a5fa 100%) !important;
    }
    
    [data-testid="metric-container"] {
        background: rgba(30, 41, 59, 0.95) !important;
        border: 1px solid rgba(59, 130, 246, 0.2) !important;
        padding: 1rem !important;
        border-radius: 10px !important;
        color: #f1f5f9 !important;
    }
    
    .stTextInput > div > div > input {
        background: rgba(51, 65, 85, 0.9) !important;
        color: #f1f5f9 !important;
        border: 1px solid rgba(59, 130, 246, 0.3) !important;
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
</style>
""", unsafe_allow_html=True)

# Questões da avaliação
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

def save_assessment_to_firestore(user_id, results):
    """Salva avaliação no Firestore usando REST API com debug detalhado"""
    
    if not FIREBASE_PROJECT_ID or not user_id:
        st.error("❌ Dados incompletos para salvar no Firestore")
        st.error(f"Project ID: {'✅' if FIREBASE_PROJECT_ID else '❌'}")
        st.error(f"User ID: {'✅' if user_id else '❌'}")
        return False
    
    try:
        # URL REST do Firestore
        doc_url = f"https://firestore.googleapis.com/v1/projects/{FIREBASE_PROJECT_ID}/databases/(default)/documents/users/{user_id}?key={FIREBASE_API_KEY}"
        
        st.info(f"🔗 **URL:** {doc_url}")
        
        # Dados no formato Firestore
        firestore_data = {
            "fields": {
                "results": {
                    "mapValue": {
                        "fields": {
                            "disc": {
                                "mapValue": {
                                    "fields": {
                                        "D": {"doubleValue": float(results["disc"]["D"])},
                                        "I": {"doubleValue": float(results["disc"]["I"])},
                                        "S": {"doubleValue": float(results["disc"]["S"])},
                                        "C": {"doubleValue": float(results["disc"]["C"])}
                                    }
                                }
                            },
                            "mbti_type": {"stringValue": str(results["mbti_type"])},
                            "reliability": {"integerValue": str(int(results["reliability"]))},
                            "completion_time": {"integerValue": str(int(results["completion_time"]))},
                            "total_questions": {"integerValue": str(int(results["total_questions"]))},
                            "response_consistency": {"doubleValue": float(results["response_consistency"])},
                            "response_variance": {"doubleValue": float(results["response_variance"])},
                            "answered_questions": {"integerValue": str(int(results["answered_questions"]))}
                        }
                    }
                },
                "timestamp": {"timestampValue": datetime.now().isoformat() + "Z"},
                "user_email": {"stringValue": str(st.session_state.user_email)},
                "user_id": {"stringValue": str(user_id)},
                "version": {"stringValue": "8.0"}
            }
        }
        
        # Headers
        headers = {
            "Content-Type": "application/json"
        }
        
        st.info("📤 **Enviando dados para Firestore...**")
        
        # Requisição PATCH para criar/atualizar documento
        response = requests.patch(doc_url, json=firestore_data, headers=headers, timeout=30)
        
        st.info(f"📡 **Status HTTP:** {response.status_code}")
        
        if response.status_code in [200, 201]:
            st.success("✅ **SUCESSO!** Dados salvos no Firestore!")
            return True
        else:
            st.error(f"❌ **Erro Firestore:** {response.status_code}")
            st.error(f"**Response:** {response.text}")
            
            # Tenta diagnóstico do erro
            if response.status_code == 403:
                st.error("🚫 **Erro de Permissão:** Verifique as regras do Firestore")
            elif response.status_code == 400:
                st.error("📝 **Erro de Formato:** Dados mal formatados")
            elif response.status_code == 401:
                st.error("🔑 **Erro de Auth:** API Key inválida")
            
            return False
        
    except requests.exceptions.Timeout:
        st.error("⏰ **Timeout:** Firestore demorou para responder")
        return False
    except requests.exceptions.ConnectionError:
        st.error("🌐 **Erro de Conexão:** Verifique sua internet")
        return False
    except Exception as e:
        st.error(f"❌ **Erro geral:** {str(e)}")
        return False


def load_assessment_from_firestore(user_id):
    """Carrega avaliação do Firestore usando REST API"""
    
    if not FIREBASE_PROJECT_ID or not user_id:
        return None
    
    try:
        doc_url = f"https://firestore.googleapis.com/v1/projects/{FIREBASE_PROJECT_ID}/databases/(default)/documents/users/{user_id}?key={FIREBASE_API_KEY}"
        
        headers = {
            "Content-Type": "application/json"
        }
        
        response = requests.get(doc_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if "fields" in data and "results" in data["fields"]:
                # Converte formato Firestore de volta para Python
                firestore_results = data["fields"]["results"]["mapValue"]["fields"]
                
                results = {
                    "disc": {
                        "D": float(firestore_results["disc"]["mapValue"]["fields"]["D"]["doubleValue"]),
                        "I": float(firestore_results["disc"]["mapValue"]["fields"]["I"]["doubleValue"]),
                        "S": float(firestore_results["disc"]["mapValue"]["fields"]["S"]["doubleValue"]),
                        "C": float(firestore_results["disc"]["mapValue"]["fields"]["C"]["doubleValue"])
                    },
                    "mbti_type": firestore_results["mbti_type"]["stringValue"],
                    "reliability": int(firestore_results["reliability"]["integerValue"]),
                    "completion_time": int(firestore_results["completion_time"]["integerValue"]),
                    "total_questions": int(firestore_results["total_questions"]["integerValue"]),
                    "response_consistency": float(firestore_results["response_consistency"]["doubleValue"]),
                    "response_variance": float(firestore_results["response_variance"]["doubleValue"]),
                    "answered_questions": int(firestore_results["answered_questions"]["integerValue"])
                }
                
                st.success("✅ Dados carregados do Firestore!")
                return results
            else:
                return None
                
        elif response.status_code == 404:
            return None
        else:
            st.error(f"❌ Erro ao carregar: {response.status_code}")
            return None
        
    except Exception as e:
        st.error(f"❌ Erro ao carregar: {str(e)}")
        return None

def test_firestore_connection():
    """Testa conexão com Firestore usando REST API"""
    
    if not FIREBASE_PROJECT_ID:
        st.error("❌ FIREBASE_PROJECT_ID não configurado")
        return False
    
    if not FIREBASE_API_KEY:
        st.error("❌ FIREBASE_API_KEY não configurado")
        return False
    
    try:
        # Testa criação de documento de teste
        test_url = f"https://firestore.googleapis.com/v1/projects/{FIREBASE_PROJECT_ID}/databases/(default)/documents/test_connection/test_doc?key={FIREBASE_API_KEY}"
        
        test_data = {
            "fields": {
                "test": {"stringValue": "connection_test"},
                "timestamp": {"timestampValue": datetime.now().isoformat() + "Z"},
                "status": {"stringValue": "testing"},
                "user_id": {"stringValue": st.session_state.user_id if st.session_state.user_id else "anonymous"}
            }
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        # Teste de escrita
        response = requests.patch(test_url, json=test_data, headers=headers, timeout=15)
        
        if response.status_code not in [200, 201]:
            st.error(f"❌ Falha na escrita: {response.status_code}")
            return False
        
        st.success("✅ Firestore funcionando!")
        
        # Limpa teste
        requests.delete(test_url, headers=headers, timeout=10)
        
        return True
        
    except Exception as e:
        st.error(f"❌ Erro no teste: {str(e)}")
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
    """Calcula resultados da avaliação com algoritmo corrigido"""
    
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
        
        # Sistema de pontuação
        if answer == 5:
            points = 2.0 * weight    # Concordo totalmente
        elif answer == 4:
            points = 1.0 * weight    # Concordo parcialmente
        elif answer == 3:
            points = 0.0             # Neutro
        elif answer == 2:
            points = -1.0 * weight   # Discordo parcialmente
        else:  # answer == 1
            points = -2.0 * weight   # Discordo totalmente
        
        if category.startswith('DISC_'):
            dim = category.split('_')[1]
            disc_raw_scores[dim] += points
            disc_question_counts[dim] += 1
    
    # Calcula médias por dimensão
    disc_averages = {}
    for dim in disc_raw_scores:
        if disc_question_counts[dim] > 0:
            disc_averages[dim] = disc_raw_scores[dim] / disc_question_counts[dim]
        else:
            disc_averages[dim] = 0
    
    # Converte para escala 0-100
    min_avg = min(disc_averages.values())
    max_avg = max(disc_averages.values())
    
    if abs(max_avg - min_avg) < 0.1:  # Valores muito próximos
        disc_scores = {"D": 25, "I": 25, "S": 25, "C": 25}
    else:
        # Converte para escala 5-45
        base_score = 5
        range_score = 40
        total_range = max_avg - min_avg
        
        disc_scores = {}
        for dim, avg in disc_averages.items():
            normalized = ((avg - min_avg) / total_range) * range_score + base_score
            disc_scores[dim] = max(5, min(45, normalized))
    
    # Normaliza para somar 100%
    total = sum(disc_scores.values())
    if total > 0:
        for dim in disc_scores:
            disc_scores[dim] = (disc_scores[dim] / total) * 100
    
    # MBTI baseado nos scores DISC
    mbti_type = ""
    
    # Extroversão vs Introversão
    extraversion_score = disc_scores["I"] - disc_scores["S"]
    mbti_type += "E" if extraversion_score > 0 else "I"
    
    # Sensação vs Intuição
    sensing_score = disc_scores["C"] - disc_scores["D"]
    mbti_type += "S" if sensing_score > 0 else "N"
    
    # Pensamento vs Sentimento
    thinking_score = (disc_scores["D"] + disc_scores["C"]) - (disc_scores["I"] + disc_scores["S"])
    mbti_type += "T" if thinking_score > 0 else "F"
    
    # Julgamento vs Percepção
    judging_score = (disc_scores["C"] + disc_scores["S"]) - (disc_scores["D"] + disc_scores["I"])
    mbti_type += "J" if judging_score > 0 else "P"
    
    # Confiabilidade
    response_values = list(answers.values())
    response_variance = np.var(response_values) if len(response_values) > 1 else 0
    disc_variance = np.var(list(disc_scores.values()))
    
    base_reliability = 70
    variance_bonus = min(15, response_variance * 5)
    differentiation_bonus = min(10, disc_variance * 2)
    
    reliability = int(base_reliability + variance_bonus + differentiation_bonus)
    reliability = max(70, min(95, reliability))
    
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
        "response_consistency": round(disc_variance, 2),
        "response_variance": round(response_variance, 2),
        "answered_questions": len(answers)
    }
    
    dominant = max(disc_scores, key=disc_scores.get)
    st.success(f"🎉 Resultado: DISC dominante = {dominant} ({disc_scores[dominant]:.0f}%) | MBTI = {mbti_type}")

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
            st.success(f"👋 {st.session_state.user_name}!")
            st.caption(f"📧 {st.session_state.user_email}")
            
            if st.button("🏠 Dashboard", key="nav_dashboard", use_container_width=True):
                st.session_state.current_page = 'dashboard'
                st.rerun()
            
            if st.button("📝 Avaliação", key="nav_assessment", use_container_width=True):
                st.session_state.current_page = 'assessment'
                st.rerun()
            
            if st.session_state.results:
                if st.button("📊 Resultados", key="nav_results", use_container_width=True):
                    st.session_state.current_page = 'results'
                    st.rerun()
            
            st.markdown("---")
            
            if st.button("🚪 Sair", key="nav_logout", use_container_width=True):
                # Limpa session state
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
        else:
            render_auth_sidebar()

def render_auth_sidebar():
    """Renderiza autenticação na sidebar"""
    
    if not FIREBASE_API_KEY:
        st.error("⚠️ Configure FIREBASE_API_KEY nos secrets")
        return
    
    st.markdown("### 🔑 Acesso")
    
    tab1, tab2 = st.tabs(["Entrar", "Cadastrar"])
    
    with tab1:
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
                            
                            st.success("✅ Login realizado!")
                            st.rerun()
                        else:
                            st.error(f"❌ {message}")
                else:
                    st.error("❌ Preencha email e senha")
    
    with tab2:
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
                                st.success("✅ Conta criada! Faça login na aba 'Entrar'")
                            else:
                                st.error(f"❌ {message}")
                else:
                    st.error("❌ Preencha todos os campos")

def render_login_required():
    """Renderiza tela de login obrigatório"""
    
    st.markdown("""
    <div class="login-required">
        <h2 style="font-size: 2.5rem; margin-bottom: 1rem;">🔒 Login Necessário</h2>
        <p style="font-size: 1.3rem; margin: 1.5rem 0;">
            Para usar o NeuroMap Pro, faça login ou crie uma conta.
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
        - **Relatórios TXT** para download
        - **Dados salvos** no Firestore
        - **Histórico de avaliações** pessoal
        """)
    
    with col2:
        st.markdown("""
        ### 🔒 Segurança Firestore:
        
        - 🛡️ **Autenticação segura** do Google
        - ☁️ **Dados na nuvem** protegidos
        - 🔐 **Criptografia** end-to-end
        - 📱 **Acesso multiplataforma**
        - 🔄 **Recuperação de senha** automática
        - ✅ **Conformidade LGPD**
        """)

def render_dashboard():
    """Dashboard principal"""
    st.markdown(f"## 👋 Bem-vindo, {st.session_state.user_name}!")
    
    # Debug Firestore
    st.markdown("### 🔧 Firestore Debug")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🧪 Testar Firestore", key="test_firestore", use_container_width=True):
            test_firestore_connection()
    
    with col2:
        if st.button("🔄 Carregar Dados", key="load_data", use_container_width=True):
            if st.session_state.user_id:
                existing_results = load_assessment_from_firestore(st.session_state.user_id)
                if existing_results:
                    st.session_state.results = existing_results
                    st.session_state.assessment_completed = True
                    st.rerun()
    
    with col3:
        if st.session_state.results and st.button("💾 Salvar Agora", key="save_now", use_container_width=True):
            save_assessment_to_firestore(st.session_state.user_id, st.session_state.results)
    
    # Informações
    st.info(f"📋 **Firestore:** Project = `{FIREBASE_PROJECT_ID}` | User = `{st.session_state.user_id[:8] if st.session_state.user_id else 'N/A'}...`")
    
    st.markdown("---")
    
    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        completed = "1" if st.session_state.assessment_completed else "0"
        delta = "✨ Completa!" if st.session_state.assessment_completed else "Pendente"
        st.metric("📊 Avaliações", completed, delta=delta)
    
    with col2:
        if st.session_state.results:
            mbti_type = st.session_state.results.get('mbti_type', 'N/A')
            st.metric("🎭 Tipo MBTI", mbti_type, delta="Identificado")
        else:
            st.metric("🎭 Tipo MBTI", "?", delta="Não avaliado")
    
    with col3:
        if st.session_state.results:
            reliability = st.session_state.results.get('reliability', 0)
            delta = "Alta" if reliability > 80 else "Média" if reliability > 60 else "Baixa"
            st.metric("🎯 Confiabilidade", f"{reliability}%", delta=delta)
        else:
            st.metric("🎯 Confiabilidade", "0%", delta="Não avaliado")
    
    with col4:
        if st.session_state.results:
            completion_time = st.session_state.results.get('completion_time', 0)
            st.metric("⏱️ Tempo", f"{completion_time} min", delta="Concluído")
        else:
            st.metric("⏱️ Tempo", "0 min", delta="Não iniciado")
    
    st.markdown("---")
    
    # Ações principais
    if not st.session_state.assessment_completed:
        st.markdown("### 🚀 Iniciar Nova Avaliação")
        
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
            if st.button("🎯 Começar Avaliação", key="start_new", type="primary", use_container_width=True):
                st.session_state.current_page = 'assessment'
                st.rerun()
            
            st.caption("⏱️ **Tempo:** 25-30 minutos")
            st.caption("📊 **Questões:** 48 científicas")
            st.caption("🔀 **Ordem:** Aleatória")
    else:
        st.markdown("### 🎉 Avaliação Concluída!")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📊 Ver Resultados", key="view_results", type="primary", use_container_width=True):
                st.session_state.current_page = 'results'
                st.rerun()
        
        with col2:
            if st.button("🔄 Nova Avaliação", key="restart", use_container_width=True):
                # Reset completo
                st.session_state.assessment_answers = {}
                st.session_state.selected_questions = None
                st.session_state.assessment_completed = False
                st.session_state.results = None
                st.session_state.question_page = 0
                st.session_state.current_page = 'assessment'
                st.rerun()
        
        # Preview dos resultados
        if st.session_state.results:
            st.markdown("### 🎯 Preview dos Resultados")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 🎭 Perfil DISC")
                for dim, score in st.session_state.results['disc'].items():
                    if score > 20:
                        st.write(f"**{dim}**: {score:.0f}%")
            
            with col2:
                st.markdown("#### 💭 Tipo MBTI")
                st.write(f"**Tipo**: {st.session_state.results['mbti_type']}")
                st.write(f"**Confiabilidade**: {st.session_state.results['reliability']}%")

def render_assessment():
    """Página de avaliação com navegação no final"""
    
    if st.session_state.selected_questions is None:
        st.session_state.selected_questions = generate_random_questions(48)
        st.session_state.assessment_start_time = datetime.now()
    
    questions = st.session_state.selected_questions
    st.title("📝 Avaliação de Personalidade")
    
    # Variáveis de paginação
    questions_per_page = 6
    total_questions = len(questions)
    total_pages = (total_questions + questions_per_page - 1) // questions_per_page
    current_page = st.session_state.question_page
    
    # Progress geral (no topo)
    answered = len([k for k, v in st.session_state.assessment_answers.items() if v != 3])  # Não conta neutros
    progress = answered / total_questions if total_questions > 0 else 0
    
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
    
    # Indicador de página atual (simples)
    st.markdown(f"### 📄 Página {current_page + 1} de {total_pages}")
    
    # Progress da página atual
    current_page_start = current_page * questions_per_page
    current_page_end = min(current_page_start + questions_per_page, total_questions)
    current_page_questions = list(range(current_page_start, current_page_end))
    
    page_answered = 0
    for i in current_page_questions:
        q = questions[i]
        answer = st.session_state.assessment_answers.get(q['display_id'], 3)
        if answer != 3:  # Não conta neutros
            page_answered += 1
    
    page_progress = page_answered / len(current_page_questions) if len(current_page_questions) > 0 else 0
    
    st.info(f"📋 **Esta página:** {page_answered}/{len(current_page_questions)} questões respondidas ({page_progress:.1%})")
    
    st.markdown("---")
    
    # ===== RENDERIZA TODAS AS QUESTÕES DA PÁGINA =====
    start_idx = current_page * questions_per_page
    end_idx = min(start_idx + questions_per_page, total_questions)
    
    for i in range(start_idx, end_idx):
        question = questions[i]
        render_single_question(question)
    
    # ===== NAVEGAÇÃO NO FINAL DA PÁGINA =====
    st.markdown("---")
    st.markdown("### 🧭 Navegação")
    
    # Botões de navegação principais
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if current_page > 0:
            if st.button("⬅️ Página Anterior", key="prev_page", use_container_width=True):
                st.session_state.question_page = current_page - 1
                st.success("⬅️ Voltando para página anterior...")
                time.sleep(0.5)
                st.rerun()
        else:
            st.button("⬅️ Página Anterior", key="prev_page_disabled", disabled=True, use_container_width=True)
    
    with col2:
        # Botão central com status
        if answered >= total_questions:
            if st.button("✨ FINALIZAR AVALIAÇÃO", key="finish_assessment", type="primary", use_container_width=True):
                with st.spinner("🧠 Processando seus resultados..."):
                    # Calcula resultados
                    calculate_results()
                    
                    # Debug dos resultados
                    if st.session_state.results:
                        st.success("✅ Resultados calculados com sucesso!")
                    else:
                        st.error("❌ Erro ao calcular resultados!")
                        return
                    
                    # Salva no Firestore
                    if st.session_state.user_id and st.session_state.results:
                        save_success = save_assessment_to_firestore(st.session_state.user_id, st.session_state.results)
                        
                        if save_success:
                            st.balloons()
                            st.success("🎉 **SUCESSO!** Resultados salvos!")
                        else:
                            st.warning("⚠️ Resultados calculados, mas problema no salvamento")
                    
                    st.session_state.assessment_completed = True
                    st.session_state.current_page = 'results'
                    time.sleep(2)
                    st.rerun()
        
        elif page_progress >= 0.5:  # Pelo menos 50% da página respondida
            st.button(f"📝 Responda mais {remaining} questões", key="need_more", disabled=True, use_container_width=True)
        else:
            st.button(f"📝 Complete esta página primeiro", key="complete_page", disabled=True, use_container_width=True)
    
    with col3:
        if current_page < total_pages - 1:
            # Só permite avançar se pelo menos 70% da página foi respondida
            if page_progress >= 0.7:
                if st.button("Próxima Página ➡️", key="next_page", use_container_width=True):
                    st.session_state.question_page = current_page + 1
                    st.success("➡️ Avançando para próxima página...")
                    time.sleep(0.5)
                    st.rerun()
            else:
                needed = int(len(current_page_questions) * 0.7) - page_answered + 1
                st.button(f"Responda +{needed} ➡️", key="next_page_disabled", disabled=True, use_container_width=True)
        else:
            st.button("Última Página ✅", key="last_page", disabled=True, use_container_width=True)
    
    # ===== INFORMAÇÕES ADICIONAIS =====
    st.markdown("---")
    
    # Barra de progresso das páginas
    st.markdown("### 📊 Progresso por Página")
    
    pages_progress = []
    for page in range(total_pages):
        page_start = page * questions_per_page
        page_end = min(page_start + questions_per_page, total_questions)
        
        page_answered_count = 0
        for i in range(page_start, page_end):
            q = questions[i]
            answer = st.session_state.assessment_answers.get(q['display_id'], 3)
            if answer != 3:
                page_answered_count += 1
        
        page_total = page_end - page_start
        page_pct = page_answered_count / page_total if page_total > 0 else 0
        pages_progress.append(page_pct)
    
    # Mostra progresso visual das páginas
    progress_cols = st.columns(total_pages)
    for i, (col, pct) in enumerate(zip(progress_cols, pages_progress)):
        with col:
            if i == current_page:
                st.metric(f"📍 Pág {i+1}", f"{pct:.0%}", delta="Atual")
            elif pct >= 0.7:
                st.metric(f"✅ Pág {i+1}", f"{pct:.0%}", delta="OK")
            elif pct > 0:
                st.metric(f"⏳ Pág {i+1}", f"{pct:.0%}", delta="Parcial")
            else:
                st.metric(f"⭕ Pág {i+1}", f"{pct:.0%}", delta="Vazia")
    
    # ===== AÇÕES SECUNDÁRIAS =====
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💾 Salvar Progresso", key="save_progress", use_container_width=True):
            st.success("✅ Progresso salvo localmente!")
            st.info(f"📊 {answered} questões respondidas de {total_questions}")
            # Limpa qualquer estado de confirmação
            if 'confirm_exit' in st.session_state:
                del st.session_state.confirm_exit
            if 'confirm_restart' in st.session_state:
                del st.session_state.confirm_restart
    
    with col2:
        # Botão Dashboard com confirmação melhorada
        if answered > 0:
            # Se já confirmou, mostra botão diferente
            if st.session_state.get('confirm_exit', False):
                if st.button("✅ Confirmar Saída", key="confirm_back_to_dashboard", use_container_width=True, type="primary"):
                    st.session_state.current_page = 'dashboard'
                    st.session_state.confirm_exit = False
                    st.rerun()
                st.caption("⚠️ Seu progresso será mantido")
            else:
                if st.button("🏠 Voltar ao Dashboard", key="back_to_dashboard", use_container_width=True):
                    st.session_state.confirm_exit = True
                    # Limpa outros estados de confirmação
                    if 'confirm_restart' in st.session_state:
                        del st.session_state.confirm_restart
                    st.rerun()
        else:
            # Se não há progresso, volta direto
            if st.button("🏠 Voltar ao Dashboard", key="back_to_dashboard_direct", use_container_width=True):
                st.session_state.current_page = 'dashboard'
                st.rerun()
    
    with col3:
        # Botão Reiniciar com confirmação melhorada
        if st.session_state.get('confirm_restart', False):
            if st.button("❌ Confirmar Reset", key="confirm_restart_assessment", use_container_width=True, type="primary"):
                st.session_state.assessment_answers = {}
                st.session_state.selected_questions = None
                st.session_state.question_page = 0
                st.session_state.confirm_restart = False
                st.success("🔄 Avaliação reiniciada!")
                time.sleep(1)
                st.rerun()
            st.caption("⚠️ Todos os dados serão perdidos")
        else:
            if st.button("🔄 Reiniciar Avaliação", key="restart_assessment", use_container_width=True):
                st.session_state.confirm_restart = True
                # Limpa outros estados de confirmação
                if 'confirm_exit' in st.session_state:
                    del st.session_state.confirm_exit
                st.rerun()
    
    # Mostra avisos de confirmação se necessário
    if st.session_state.get('confirm_exit', False):
        st.warning("⚠️ **Tem certeza que quer sair?** Clique em 'Confirmar Saída' acima. Seu progresso será mantido.")
        
        # Botão para cancelar
        if st.button("❌ Cancelar", key="cancel_exit", use_container_width=False):
            st.session_state.confirm_exit = False
            st.rerun()
    
    if st.session_state.get('confirm_restart', False):
        st.error("⚠️ **Tem certeza que quer reiniciar?** Clique em 'Confirmar Reset' acima. Todos os dados serão perdidos!")
        
        # Botão para cancelar
        if st.button("❌ Cancelar", key="cancel_restart", use_container_width=False):
            st.session_state.confirm_restart = False
            st.rerun()



def render_single_question(question):
    """Renderiza uma questão individual com auto-avanço inteligente"""
    
    st.markdown(f"""
    <div class="question-container">
        <h4>
            {question['display_id']}. {question['text']}
        </h4>
    </div>
    """, unsafe_allow_html=True)
    
    current_value = st.session_state.assessment_answers.get(question['display_id'], 3)
    
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
    
    # Armazena resposta
    old_value = st.session_state.assessment_answers.get(question['display_id'], 3)
    new_value = selected[0]
    st.session_state.assessment_answers[question['display_id']] = new_value
    
    # ===== LÓGICA DE AUTO-AVANÇO CORRIGIDA =====
    
    # Só verifica auto-avanço se:
    # 1. A resposta mudou de verdade (não é valor inicial)
    # 2. A mudança não foi para o valor padrão (3)
    # 3. Existe questões selecionadas
    should_check_advance = (
        old_value != new_value and  # Resposta mudou
        new_value != 3 and         # Não mudou para neutro
        old_value != 3 and         # Não era neutro antes
        st.session_state.selected_questions  # Questões existem
    )
    
    if should_check_advance:
        try:
            # Informações da paginação
            questions_per_page = 6
            current_page = st.session_state.question_page
            total_questions = len(st.session_state.selected_questions)
            total_pages = (total_questions + questions_per_page - 1) // questions_per_page
            
            # Questões da página atual
            start_idx = current_page * questions_per_page
            end_idx = min(start_idx + questions_per_page, total_questions)
            
            # Verifica quantas questões da página foram realmente respondidas (não neutro)
            page_answered = 0
            page_total = 0
            
            for i in range(start_idx, end_idx):
                q = st.session_state.selected_questions[i]
                page_total += 1
                
                # Considera respondida se não for neutro (3)
                answer = st.session_state.assessment_answers.get(q['display_id'], 3)
                if answer != 3:
                    page_answered += 1
            
            # Só avança se TODAS as questões da página foram respondidas (não neutro)
            page_complete = (page_answered == page_total)
            
            # Debug (remover depois)
            st.caption(f"📊 Página atual: {page_answered}/{page_total} respondidas (não neutras)")
            
            # Avança automaticamente apenas se:
            # 1. Página realmente completa
            # 2. Não é a última página
            # 3. Pelo menos 4 questões foram respondidas (evita avanço muito cedo)
            if page_complete and current_page < total_pages - 1 and page_answered >= 4:
                # Pequeno delay para mostrar feedback
                st.success("✅ Página concluída! Avançando em 2 segundos...")
                
                # Usa session state para controlar o avanço
                if 'auto_advance_triggered' not in st.session_state:
                    st.session_state.auto_advance_triggered = True
                    
                    # Agendar avanço após delay
                    import threading
                    def advance_page():
                        time.sleep(2)
                        if st.session_state.auto_advance_triggered:
                            st.session_state.question_page += 1
                            st.session_state.auto_advance_triggered = False
                            st.rerun()
                    
                    thread = threading.Thread(target=advance_page)
                    thread.daemon = True
                    thread.start()
                    
        except Exception as e:
            # Se der erro no auto-avanço, apenas continua normalmente
            st.caption(f"⚠️ Auto-avanço desabilitado: {str(e)}")
            pass
    
    # Feedback visual
    feedback_emojis = {1: "🔴", 2: "🟠", 3: "🟡", 4: "🟢", 5: "🟢"}
    feedback_texts = {
        1: "Discordo totalmente",
        2: "Discordo parcialmente", 
        3: "Neutro",
        4: "Concordo parcialmente",
        5: "Concordo totalmente"
    }
    
    st.caption(f"{feedback_emojis[new_value]} {feedback_texts[new_value]}")
    st.markdown("---")





def render_results():
    """Renderiza página de resultados"""
    
    # Verifica se há resultados para exibir
    if not st.session_state.results:
        st.error("❌ Nenhum resultado encontrado. Complete a avaliação primeiro.")
        if st.button("📝 Fazer Avaliação", key="go_to_assessment", use_container_width=True):
            st.session_state.current_page = 'assessment'
            st.rerun()
        return
    
    results = st.session_state.results
    
    st.title("📊 Seus Resultados")
    
    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🎭 Tipo MBTI", results['mbti_type'])
    
    with col2:
        dominant_disc = max(results['disc'], key=results['disc'].get)
        st.metric("🎯 DISC Dominante", f"{dominant_disc} ({results['disc'][dominant_disc]:.0f}%)")
    
    with col3:
        st.metric("🎯 Confiabilidade", f"{results['reliability']}%")
    
    with col4:
        st.metric("⏱️ Tempo", f"{results['completion_time']} min")
    
    st.markdown("---")
    
    # Gráfico DISC
    st.markdown("### 📊 Perfil DISC")
    
    disc_scores = results['disc']
    for dim, score in disc_scores.items():
        if score >= 35:
            color = "#48bb78"
            level = "Alto"
        elif score >= 25:
            color = "#ed8936"
            level = "Moderado"
        else:
            color = "#e53e3e"
            level = "Baixo"
            
        bar_width = int((score / 100) * 50)
        bar = "█" * bar_width + "░" * (50 - bar_width)
        
        st.markdown(f"""
        <div style="background: {color}20; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; 
                    border-left: 4px solid {color};">
            <strong>{dim}: {score:.1f}% ({level})</strong><br>
            <div style="font-family: monospace; font-size: 0.8rem; color: {color};">
                {bar}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
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
    
    # MBTI
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
    
    # Botões de download
    st.markdown("---")
    st.markdown("### 📄 Gerar Relatórios")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📝 Relatório TXT", key="generate_txt", use_container_width=True):
            with st.spinner("📝 Gerando relatório..."):
                txt_content = generate_text_report(results)
                
                if txt_content is not None:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"NeuroMap_Relatorio_{timestamp}.txt"
                    
                    st.download_button(
                        label="⬇️ Baixar TXT",
                        data=txt_content,
                        file_name=filename,
                        mime="text/plain",
                        key="download_txt",
                        use_container_width=True
                    )
                    
                    st.success("🎉 Relatório TXT gerado!")
                else:
                    st.error("❌ Erro ao gerar relatório TXT")
    
    with col2:
        if st.button("🌐 Relatório HTML", key="generate_html", use_container_width=True):
            with st.spinner("🌐 Gerando relatório HTML..."):
                html_content = generate_html_report(results)
                
                if html_content is not None:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"NeuroMap_Relatorio_{timestamp}.html"
                    
                    st.download_button(
                        label="⬇️ Baixar HTML",
                        data=html_content,
                        file_name=filename,
                        mime="text/html",
                        key="download_html",
                        use_container_width=True
                    )
                    
                    st.success("🎉 Relatório HTML gerado!")
                else:
                    st.error("❌ Erro ao gerar relatório HTML")
    
    # Ações adicionais
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Nova Avaliação", key="restart_from_results", use_container_width=True):
            # Reset completo
            st.session_state.assessment_answers = {}
            st.session_state.selected_questions = None
            st.session_state.assessment_completed = False
            st.session_state.results = None
            st.session_state.question_page = 0
            st.session_state.current_page = 'assessment'
            st.rerun()
    
    with col2:
        if st.button("🏠 Voltar ao Dashboard", key="back_to_dashboard", use_container_width=True):
            st.session_state.current_page = 'dashboard'
            st.rerun()

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
    """Gera insights personalizados"""
    
    # Insights baseados no MBTI
    mbti_insights = {
        'INFP': {
            'strengths': [
                "Criatividade e imaginação excepcional",
                "Empatia profunda e compreensão das pessoas",
                "Valores sólidos e integridade pessoal",
                "Capacidade de inspirar através de ideais"
            ],
            'development': [
                "Desenvolver habilidades de organização",
                "Praticar comunicação mais direta",
                "Melhorar gestão de tempo e prazos",
                "Equilibrar idealismo com realismo"
            ],
            'careers': [
                "Psicólogo ou Terapeuta",
                "Escritor ou Jornalista",
                "Consultor em Recursos Humanos",
                "Profissional de ONGs"
            ]
        },
        'ESTJ': {
            'strengths': [
                "Liderança natural e orientação para resultados",
                "Capacidade de organizar pessoas e processos",
                "Tomada de decisão rápida e eficiente",
                "Foco em produtividade e eficiência"
            ],
            'development': [
                "Desenvolver flexibilidade e adaptabilidade",
                "Melhorar escuta ativa e empatia",
                "Praticar delegação efetiva",
                "Equilibrar assertividade com colaboração"
            ],
            'careers': [
                "Diretor Executivo ou CEO",
                "Gerente de Operações",
                "Consultor Empresarial",
                "Líder de Projetos Estratégicos"
            ]
        }
    }
    
    # Retorna insights específicos ou genérico
    if mbti_type in mbti_insights:
        return mbti_insights[mbti_type]
    else:
        # Insights genéricos baseados no DISC dominante
        if dominant_disc == 'D':
            return mbti_insights['ESTJ']
        elif dominant_disc in ['I', 'S']:
            return mbti_insights['INFP']
        else:
            return {
                'strengths': [
                    "Perfil equilibrado com múltiplas competências",
                    "Adaptabilidade a diferentes situações",
                    "Capacidade de trabalhar em diversos contextos",
                    "Flexibilidade comportamental"
                ],
                'development': [
                    "Identificar pontos fortes específicos",
                    "Focar em áreas de maior interesse",
                    "Desenvolver especialização",
                    "Buscar feedback para autoconhecimento"
                ],
                'careers': [
                    "Consultor Generalista",
                    "Coordenador de Projetos",
                    "Analista de Negócios",
                    "Gestor de Equipes"
                ]
            }

def generate_html_report(results):
    """Gera relatório em HTML com gráficos visuais"""
    
    try:
        user_email = st.session_state.user_email
        user_name = st.session_state.user_name
        mbti_descriptions = get_mbti_description(results['mbti_type'])
        dominant_disc = max(results['disc'], key=results['disc'].get)
        insights = generate_insights(dominant_disc, results['mbti_type'], results)
        
        html_content = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NeuroMap Pro - Relatório de {user_name}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5rem;
            margin-bottom: 10px;
            font-weight: 700;
        }}
        
        .content {{
            padding: 40px;
        }}
        
        .section {{
            margin-bottom: 40px;
        }}
        
        .section h2 {{
            color: #667eea;
            font-size: 1.8rem;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #e9ecef;
        }}
        
        .user-info {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 30px;
            border-left: 5px solid #667eea;
        }}
        
        .metrics {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .metric-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            border-left: 4px solid #667eea;
        }}
        
        .metric-value {{
            font-size: 2rem;
            font-weight: bold;
            color: #667eea;
        }}
        
        .metric-label {{
            color: #6c757d;
            font-size: 0.9rem;
            margin-top: 5px;
        }}
        
        /* Gráfico DISC com barras CSS */
        .disc-chart {{
            display: grid;
            gap: 20px;
            margin: 30px 0;
        }}
        
        .disc-item {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 15px;
            position: relative;
            overflow: hidden;
        }}
        
        .disc-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            font-weight: bold;
            font-size: 1.1rem;
            z-index: 2;
            position: relative;
        }}
        
        .disc-bar-container {{
            position: relative;
            height: 30px;
            background: #e9ecef;
            border-radius: 15px;
            overflow: hidden;
            margin: 15px 0;
        }}
        
        .disc-bar {{
            height: 100%;
            border-radius: 15px;
            position: relative;
            transition: width 1s ease-in-out;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            font-size: 0.9rem;
        }}
        
        .disc-description {{
            color: #6c757d;
            font-size: 0.95rem;
            margin-top: 10px;
        }}
        
        /* Cores específicas para cada dimensão DISC */
        .disc-d {{ border-left: 5px solid #dc3545; }}
        .disc-d .disc-bar {{ background: linear-gradient(90deg, #dc3545 0%, #e57373 100%); }}
        
        .disc-i {{ border-left: 5px solid #ffc107; }}
        .disc-i .disc-bar {{ background: linear-gradient(90deg, #ffc107 0%, #ffeb3b 100%); }}
        
        .disc-s {{ border-left: 5px solid #28a745; }}
        .disc-s .disc-bar {{ background: linear-gradient(90deg, #28a745 0%, #66bb6a 100%); }}
        
        .disc-c {{ border-left: 5px solid #007bff; }}
        .disc-c .disc-bar {{ background: linear-gradient(90deg, #007bff 0%, #42a5f5 100%); }}
        
        /* Gráfico circular MBTI */
        .mbti-section {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 15px;
            margin: 30px 0;
            text-align: center;
        }}
        
        .mbti-type {{
            font-size: 4rem;
            font-weight: bold;
            margin: 20px 0;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        
        .mbti-circle {{
            width: 150px;
            height: 150px;
            border-radius: 50%;
            background: rgba(255,255,255,0.2);
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 20px auto;
            border: 3px solid rgba(255,255,255,0.5);
        }}
        
        .insights-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 30px;
            margin: 30px 0;
        }}
        
        .insight-card {{
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        
        .strengths {{
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
            color: white;
        }}
        
        .development {{
            background: linear-gradient(135deg, #dc3545 0%, #fd7e14 100%);
            color: white;
        }}
        
        .careers {{
            background: linear-gradient(135deg, #6f42c1 0%, #e83e8c 100%);
            color: white;
        }}
        
        .insight-card h3 {{
            margin-bottom: 15px;
            font-size: 1.3rem;
        }}
        
        .insight-card ul {{
            list-style: none;
            padding: 0;
        }}
        
        .insight-card li {{
            padding: 8px 0;
            padding-left: 20px;
            position: relative;
        }}
        
        .insight-card li:before {{
            content: "●";
            position: absolute;
            left: 0;
            font-weight: bold;
            font-size: 1.2rem;
        }}
        
        .footer {{
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #6c757d;
            border-top: 1px solid #e9ecef;
        }}
        
        /* Animações */
        @keyframes slideIn {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        .section {{
            animation: slideIn 0.6s ease-out;
        }}
        
        .disc-bar {{
            animation: fillBar 2s ease-out;
        }}
        
        @keyframes fillBar {{
            from {{ width: 0%; }}
        }}
        
        @media print {{
            body {{ background: white; padding: 0; }}
            .container {{ box-shadow: none; border-radius: 0; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧠 NeuroMap Pro</h1>
            <p style="font-size: 1.2rem; opacity: 0.9;">Relatório Completo de Análise de Personalidade</p>
        </div>
        
        <div class="content">
            <div class="user-info">
                <h3>📋 Informações Gerais</h3>
                <p><strong>Usuário:</strong> {user_name} ({user_email})</p>
                <p><strong>Data:</strong> {datetime.now().strftime('%d/%m/%Y às %H:%M')}</p>
                <p><strong>Tempo de Conclusão:</strong> {results['completion_time']} minutos</p>
                <p><strong>Total de Questões:</strong> {results['total_questions']}</p>
                <p><strong>Confiabilidade:</strong> {results['reliability']}%</p>
            </div>
            
            <div class="metrics">
                <div class="metric-card">
                    <div class="metric-value">{results['mbti_type']}</div>
                    <div class="metric-label">Tipo MBTI</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{dominant_disc}</div>
                    <div class="metric-label">DISC Dominante</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{results['reliability']}%</div>
                    <div class="metric-label">Confiabilidade</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{results['response_consistency']:.1f}</div>
                    <div class="metric-label">Consistência</div>
                </div>
            </div>
            
            <div class="section">
                <h2>📊 Análise DISC Detalhada</h2>
                <div class="disc-chart">
"""

        # Adiciona gráfico DISC com barras
        disc_descriptions = {
            "D": ("Dominância", "Orientação para resultados, liderança direta, tomada de decisão rápida"),
            "I": ("Influência", "Comunicação persuasiva, networking, motivação de equipes"),
            "S": ("Estabilidade", "Cooperação, paciência, trabalho em equipe consistente"),
            "C": ("Conformidade", "Foco em qualidade, precisão, análise sistemática")
        }
        
        for key, score in results['disc'].items():
            name, description = disc_descriptions[key]
            
            if score >= 35:
                level_text = "Alto"
            elif score >= 20:
                level_text = "Moderado"
            else:
                level_text = "Baixo"
            
            html_content += f"""
                    <div class="disc-item disc-{key.lower()}">
                        <div class="disc-header">
                            <span>{name} ({key})</span>
                            <span>{score:.1f}% - {level_text}</span>
                        </div>
                        <div class="disc-bar-container">
                            <div class="disc-bar" style="width: {score}%">
                                {score:.0f}%
                            </div>
                        </div>
                        <div class="disc-description">{description}</div>
                    </div>
"""

        html_content += f"""
                </div>
            </div>
            
            <div class="mbti-section">
                <div class="mbti-circle">
                    <div class="mbti-type">{results['mbti_type']}</div>
                </div>
                <h2 style="color: white;">{mbti_descriptions['title']}</h2>
                <p style="font-size: 1.1rem; margin-top: 15px;">{mbti_descriptions['description']}</p>
            </div>
            
            <div class="section">
                <h2>🎯 Insights e Recomendações</h2>
                <div class="insights-grid">
                    <div class="insight-card strengths">
                        <h3>🏆 Pontos Fortes</h3>
                        <ul>
"""

        for strength in insights['strengths']:
            html_content += f"                            <li>{strength}</li>\n"

        html_content += """
                        </ul>
                    </div>
                    
                    <div class="insight-card development">
                        <h3>📈 Áreas de Desenvolvimento</h3>
                        <ul>
"""

        for area in insights['development']:
            html_content += f"                            <li>{area}</li>\n"

        html_content += """
                        </ul>
                    </div>
                    
                    <div class="insight-card careers">
                        <h3>💼 Carreiras Sugeridas</h3>
                        <ul>
"""

        for career in insights['careers']:
            html_content += f"                            <li>{career}</li>\n"

        html_content += f"""
                        </ul>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>Relatório gerado pelo <strong>NeuroMap Pro</strong> em {datetime.now().strftime('%d/%m/%Y às %H:%M')}</p>
            <p>Análise Científica Avançada de Personalidade</p>
        </div>
    </div>
</body>
</html>
"""
        
        return html_content.encode('utf-8')
        
    except Exception as e:
        st.error(f"❌ Erro ao gerar relatório HTML: {str(e)}")
        return None

def generate_text_report(results):
    """Gera relatório em texto simples"""
    
    try:
        report = "NEUROMAP PRO - RELATORIO DE PERSONALIDADE\n"
        report += "=" * 50 + "\n\n"
        
        report += "INFORMACOES GERAIS:\n"
        report += f"Usuario: {st.session_state.user_email}\n"
        report += f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
        report += f"Tempo de conclusao: {results['completion_time']} minutos\n"
        report += f"Total de questoes: {results['total_questions']}\n"
        report += f"Confiabilidade: {results['reliability']}%\n"
        report += f"Tipo MBTI: {results['mbti_type']}\n\n"
        
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
        
        # Insights
        dominant_disc = max(results['disc'], key=results['disc'].get)
        insights = generate_insights(dominant_disc, results['mbti_type'], results)
        
        report += "\nPONTOS FORTES IDENTIFICADOS:\n"
        report += "-" * 30 + "\n"
        
        for i, strength in enumerate(insights['strengths'], 1):
            report += f"{i}. {strength}\n"
        
        report += "\nAREAS PARA DESENVOLVIMENTO:\n"
        report += "-" * 30 + "\n"
        
        for i, area in enumerate(insights['development'], 1):
            report += f"{i}. {area}\n"
        
        report += "\nCARREIRAS SUGERIDAS:\n"
        report += "-" * 20 + "\n"
        
        for i, career in enumerate(insights['careers'], 1):
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
    
    if not st.session_state.authenticated:
        render_login_required()
        return
    
    # Roteamento
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
