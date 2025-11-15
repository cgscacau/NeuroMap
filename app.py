import streamlit as st
import os
from datetime import datetime

# Configuração da página
st.set_page_config(
    page_title="NeuroMap - Avaliação de Personalidade",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #0b0f17 0%, #1a1f3a 100%);
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .metric-card {
        background: #1e2a44;
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 4px solid #8ab4f8;
        margin: 0.5rem 0;
    }
    
    .stButton > button {
        width: 100%;
        border-radius: 8px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Header principal
    st.markdown("""
    <div class="main-header">
        <h1 style='color: #8ab4f8; margin-bottom: 0.5rem;'>
            🧠 NeuroMap
        </h1>
        <p style='color: #a8c7fa; font-size: 1.2rem; margin: 0;'>
            Descubra sua personalidade com precisão científica
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Inicializa estado da sessão
    if 'user_authenticated' not in st.session_state:
        st.session_state.user_authenticated = False
    
    if 'assessment_completed' not in st.session_state:
        st.session_state.assessment_completed = False
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 🧭 Navegação")
        
        if st.session_state.user_authenticated:
            st.success(f"👋 Bem-vindo!")
            
            if st.button("🚪 Sair"):
                st.session_state.user_authenticated = False
                st.session_state.clear()
                st.rerun()
        else:
            render_auth_sidebar()
    
    # Conteúdo principal
    if not st.session_state.user_authenticated:
        render_landing_page()
    else:
        render_main_dashboard()

def render_auth_sidebar():
    """Renderiza autenticação na sidebar"""
    
    st.markdown("#### 🔑 Acesso")
    
    tab1, tab2 = st.tabs(["Entrar", "Cadastrar"])
    
    with tab1:
        with st.form("login_form"):
            email = st.text_input("📧 Email", placeholder="seu@email.com")
            password = st.text_input("🔐 Senha", type="password")
            
            if st.form_submit_button("Entrar", use_container_width=True):
                # Simulação de login (substitua por autenticação real)
                if email and password:
                    st.session_state.user_authenticated = True
                    st.session_state.user_email = email
                    st.success("Login realizado!")
                    st.rerun()
                else:
                    st.error("Preencha todos os campos")
    
    with tab2:
        with st.form("register_form"):
            name = st.text_input("👤 Nome completo")
            email = st.text_input("📧 Email")
            password = st.text_input("🔐 Senha", type="password")
            
            if st.form_submit_button("Criar conta", use_container_width=True):
                if name and email and password:
                    st.session_state.user_authenticated = True
                    st.session_state.user_email = email
                    st.session_state.user_name = name
                    st.success("Conta criada!")
                    st.rerun()
                else:
                    st.error("Preencha todos os campos")

def render_landing_page():
    """Renderiza página inicial para usuários não autenticados"""
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🎯 **O que você descobrirá:**
        
        - **Perfil DISC** - Seu estilo comportamental no trabalho
        - **Big Five** - Os 5 grandes traços de personalidade
        - **Tipo MBTI** - Suas preferências cognitivas
        - **Insights personalizados** - Recomendações específicas para você
        """)
        
        st.markdown("""
        ### ⏱️ **Informações:**
        
        - ⏰ **15-20 minutos** para completar
        - 📊 **48 questões** baseadas em ciência
        - 🔒 **100% gratuito** e confidencial
        - 📱 **Funciona em qualquer dispositivo**
        """)
    
    with col2:
        st.markdown("""
        ### 📈 **Benefícios:**
        
        ✅ **Autoconhecimento profundo**  
        ✅ **Melhore seus relacionamentos**  
        ✅ **Desenvolva sua carreira**  
        ✅ **Entenda seus pontos fortes**  
        ✅ **Identifique áreas de crescimento**  
        ✅ **Relatórios detalhados**  
        """)
        
        st.info("👆 **Faça login na barra lateral para começar!**")
    
    # Demonstração
    st.markdown("---")
    st.markdown("### 🎪 **Prévia dos Resultados**")
    
    # Gráfico demo
    import plotly.graph_objects as go
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=[75, 45, 30, 60, 75],
        theta=['Dominância', 'Influência', 'Estabilidade', 'Conformidade', 'Dominância'],
        fill='toself',
        name='Exemplo de Perfil DISC',
        line_color='#8ab4f8'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100])
        ),
        showlegend=True,
        title="Exemplo: Perfil DISC",
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_main_dashboard():
    """Renderiza dashboard principal"""
    
    st.markdown(f"### 👋 Olá, {st.session_state.get('user_name', 'Usuário')}!")
    
    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📊 Avaliações", "1", delta="Nova!")
    
    with col2:
        st.metric("🎭 Tipo MBTI", "INTJ" if st.session_state.assessment_completed else "?")
    
    with col3:
        st.metric("📈 Progresso", "100%" if st.session_state.assessment_completed else "0%")
    
    with col4:
        st.metric("🔥 Sequência", "1 dia")
    
    st.markdown("---")
    
    # Ações principais
    col1, col2 = st.columns(2)
    
    with col1:
        if not st.session_state.assessment_completed:
            if st.button("🚀 Fazer Primeira Avaliação", type="primary", use_container_width=True):
                st.switch_page("pages/2_📝_Avaliacao.py")
        else:
            if st.button("🔄 Nova Avaliação", use_container_width=True):
                st.switch_page("pages/2_📝_Avaliacao.py")
    
    with col2:
        if st.session_state.assessment_completed:
            if st.button("📊 Ver Dashboard Completo", use_container_width=True):
                st.switch_page("pages/1_📊_Dashboard.py")
        else:
            st.info("Complete uma avaliação para acessar o dashboard")
    
    # Conteúdo condicional
    if st.session_state.assessment_completed:
        render_results_preview()
    else:
        render_getting_started()

def render_results_preview():
    """Preview dos resultados"""
    st.markdown("### 🎯 Seus Últimos Resultados")
    
    # Simulação de dados
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📊 Perfil DISC")
        
        import plotly.graph_objects as go
        
        fig = go.Figure(go.Bar(
            x=['D', 'I', 'S', 'C'],
            y=[75, 45, 30, 60],
            marker_color=['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4']
        ))
        
        fig.update_layout(
            title="Seus Scores DISC",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white')
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### 🧠 Big Five")
        
        traits = ['Abertura', 'Conscienciosidade', 'Extroversão', 'Amabilidade', 'Neuroticismo']
        values = [85, 90, 35, 75, 20]
        
        fig = go.Figure(go.Bar(
            y=traits,
            x=values,
            orientation='h',
            marker_color='#8ab4f8'
        ))
        
        fig.update_layout(
            title="Seus Percentis Big Five",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white')
        )
        
        st.plotly_chart(fig, use_container_width=True)

def render_getting_started():
    """Guia de primeiros passos"""
    st.markdown("### 🌟 Primeiros Passos")
    
    steps = [
        ("1️⃣", "Faça sua primeira avaliação", "Responda 48 questões sobre seu comportamento"),
        ("2️⃣", "Receba seus resultados", "Descubra seu perfil DISC, Big Five e MBTI"),
        ("3️⃣", "Explore insights", "Entenda seus pontos fortes e áreas de desenvolvimento"),
        ("4️⃣", "Baixe relatórios", "Obtenha relatórios detalhados em PDF")
    ]
    
    for icon, title, description in steps:
        st.markdown(f"""
        <div class="metric-card">
            <h4>{icon} {title}</h4>
            <p style='margin: 0; color: #a8c7fa;'>{description}</p>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
